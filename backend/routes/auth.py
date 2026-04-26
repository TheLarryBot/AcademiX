# ============================================
# AcademiX — backend/routes/auth.py
# Blueprint de autenticación.
#
# Endpoints:
#   POST /api/auth/login
#   POST /api/auth/register
#   POST /api/auth/logout
#   GET  /api/auth/me
#   POST /api/auth/change-password
#
# Requiere:   pip install flask bcrypt pyjwt
# ============================================

import re
import jwt
import bcrypt
from datetime import datetime, timezone, timedelta
from functools import wraps

from flask import Blueprint, request, jsonify, g, current_app
from backend.database import get_connection

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# ── Tiempo de expiración del token ──────────────────────────────────────────
TOKEN_TTL_NORMAL   = timedelta(hours=8)
TOKEN_TTL_REMEMBER = timedelta(days=30)


# ════════════════════════════════════════════════════════════════════════════
# Utilidades internas
# ════════════════════════════════════════════════════════════════════════════

def _hash_password(plain: str) -> str:
    """Devuelve el hash bcrypt de la contraseña."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()


def _check_password(plain: str, hashed: str) -> bool:
    """Compara la contraseña en texto plano contra su hash."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def _generate_token(user_id: int, rol: str, remember: bool = False) -> str:
    """Genera un JWT firmado con la SECRET_KEY de la app."""
    ttl = TOKEN_TTL_REMEMBER if remember else TOKEN_TTL_NORMAL
    payload = {
        "sub": user_id,
        "rol": rol,
        "exp": datetime.now(timezone.utc) + ttl,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def _decode_token(token: str) -> dict:
    """Decodifica y valida el JWT. Lanza excepción si es inválido o expirado."""
    return jwt.decode(
        token,
        current_app.config["SECRET_KEY"],
        algorithms=["HS256"],
    )


def _is_valid_correo(correo: str) -> bool:
    return bool(re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", correo))


def _is_strong_password(pw: str) -> bool:
    return (
        len(pw) >= 8
        and bool(re.search(r"[A-Z]", pw))
        and bool(re.search(r"[0-9]", pw))
        and bool(re.search(r"[^A-Za-z0-9]", pw))
    )


def _log_historial(conn, tipo: str, titulo: str, descripcion: str, usuario: str = "Sistema"):
    """Registra una entrada en la tabla historial."""
    conn.execute(
        """INSERT INTO historial (tipo, titulo, descripcion, usuario)
           VALUES (?, ?, ?, ?)""",
        (tipo, titulo, descripcion, usuario),
    )


# ════════════════════════════════════════════════════════════════════════════
# Decorador de autenticación
# ════════════════════════════════════════════════════════════════════════════

def login_required(f):
    """Verifica el JWT en el header Authorization: Bearer <token>."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token requerido"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = _decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Sesión expirada, inicia sesión nuevamente"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401
        g.user_id = payload["sub"]
        g.user_rol = payload["rol"]
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Exige que el usuario autenticado tenga rol 'admin'."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if g.user_rol != "admin":
            return jsonify({"error": "Acceso restringido a administradores"}), 403
        return f(*args, **kwargs)
    return decorated


# ════════════════════════════════════════════════════════════════════════════
# POST /api/auth/login
# ════════════════════════════════════════════════════════════════════════════

@auth_bp.post("/login")
def login():
    """
    Body JSON esperado:
        { "correo": "...", "password": "...", "remember": false }

    Respuesta 200:
        { "token": "...", "usuario": { id, nombre, correo, rol, facultad } }
    """
    data = request.get_json(silent=True) or {}

    correo   = (data.get("correo") or "").strip().lower()
    password = (data.get("password") or "").strip()
    remember = bool(data.get("remember", False))

    # — Validaciones básicas —
    if not correo or not password:
        return jsonify({"error": "Correo y contraseña son obligatorios"}), 400

    if not _is_valid_correo(correo):
        return jsonify({"error": "Formato de correo inválido"}), 400

    conn = get_connection()
    try:
        user = conn.execute(
            "SELECT * FROM usuarios WHERE correo = ?", (correo,)
        ).fetchone()

        # Mensaje genérico para no revelar si el correo existe o no
        if user is None or not _check_password(password, user["password"]):
            _log_historial(
                conn,
                tipo="acceso",
                titulo="Intento de login fallido",
                descripcion=f"Correo: {correo}",
                usuario=correo,
            )
            conn.commit()
            return jsonify({"error": "Credenciales incorrectas"}), 401

        token = _generate_token(user["id"], user["rol"], remember)

        _log_historial(
            conn,
            tipo="acceso",
            titulo="Inicio de sesión",
            descripcion=f"{user['nombre']} ({user['rol']}) ingresó al sistema",
            usuario=user["nombre"],
        )
        conn.commit()

        return jsonify({
            "token": token,
            "usuario": {
                "id":       user["id"],
                "nombre":   user["nombre"],
                "correo":   user["correo"],
                "rol":      user["rol"],
                "facultad": user["facultad"],
            },
        }), 200

    finally:
        conn.close()


# ════════════════════════════════════════════════════════════════════════════
# POST /api/auth/register
# ════════════════════════════════════════════════════════════════════════════

@auth_bp.post("/register")
def register():
    """
    Body JSON esperado:
        { "nombre": "...", "correo": "...", "password": "...",
          "rol": "docente|admin", "facultad": "..." }

    Solo un admin puede crear otro admin.
    Un registro público siempre crea rol 'docente'.
    """
    data = request.get_json(silent=True) or {}

    nombre   = (data.get("nombre") or "").strip()
    correo   = (data.get("correo") or "").strip().lower()
    password = (data.get("password") or "").strip()
    rol      = (data.get("rol") or "docente").strip().lower()
    facultad = (data.get("facultad") or "").strip() or None

    # — Validaciones —
    errors = {}
    if not nombre:
        errors["nombre"] = "El nombre es obligatorio"
    if not correo or not _is_valid_correo(correo):
        errors["correo"] = "Ingresa un correo válido"
    if not password or not _is_strong_password(password):
        errors["password"] = (
            "La contraseña debe tener 8+ caracteres, una mayúscula, "
            "un número y un carácter especial"
        )
    if rol not in ("admin", "docente"):
        errors["rol"] = "Rol inválido. Usa 'admin' o 'docente'"

    if errors:
        return jsonify({"error": "Datos inválidos", "campos": errors}), 400

    # Registros públicos siempre son 'docente' a menos que haya un admin autenticado
    auth_header = request.headers.get("Authorization", "")
    caller_rol = None
    if auth_header.startswith("Bearer "):
        try:
            payload = _decode_token(auth_header.split(" ", 1)[1])
            caller_rol = payload.get("rol")
        except jwt.InvalidTokenError:
            pass

    if rol == "admin" and caller_rol != "admin":
        rol = "docente"   # degradar silenciosamente

    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM usuarios WHERE correo = ?", (correo,)
        ).fetchone()
        if existing:
            return jsonify({"error": "Este correo ya está registrado"}), 409

        hashed = _hash_password(password)
        cursor = conn.execute(
            """INSERT INTO usuarios (nombre, correo, password, rol, facultad)
               VALUES (?, ?, ?, ?, ?)""",
            (nombre, correo, hashed, rol, facultad),
        )
        new_id = cursor.lastrowid

        _log_historial(
            conn,
            tipo="creacion",
            titulo="Nuevo usuario registrado",
            descripcion=f"{nombre} ({rol}) — {correo}",
            usuario=nombre,
        )
        conn.commit()

        return jsonify({
            "mensaje": "Cuenta creada exitosamente",
            "usuario": {
                "id":       new_id,
                "nombre":   nombre,
                "correo":   correo,
                "rol":      rol,
                "facultad": facultad,
            },
        }), 201

    finally:
        conn.close()


# ════════════════════════════════════════════════════════════════════════════
# GET /api/auth/me
# ════════════════════════════════════════════════════════════════════════════

@auth_bp.get("/me")
@login_required
def me():
    """Devuelve los datos del usuario autenticado a partir del token."""
    conn = get_connection()
    try:
        user = conn.execute(
            "SELECT id, nombre, correo, rol, facultad, creado_en FROM usuarios WHERE id = ?",
            (g.user_id,),
        ).fetchone()
        if user is None:
            return jsonify({"error": "Usuario no encontrado"}), 404
        return jsonify(dict(user)), 200
    finally:
        conn.close()


# ════════════════════════════════════════════════════════════════════════════
# POST /api/auth/change-password
# ════════════════════════════════════════════════════════════════════════════

@auth_bp.post("/change-password")
@login_required
def change_password():
    """
    Body JSON esperado:
        { "password_actual": "...", "password_nueva": "..." }
    """
    data = request.get_json(silent=True) or {}
    actual = (data.get("password_actual") or "").strip()
    nueva  = (data.get("password_nueva")  or "").strip()

    if not actual or not nueva:
        return jsonify({"error": "Ambos campos son obligatorios"}), 400

    if not _is_strong_password(nueva):
        return jsonify({
            "error": "La nueva contraseña debe tener 8+ caracteres, "
                     "una mayúscula, un número y un carácter especial"
        }), 400

    conn = get_connection()
    try:
        user = conn.execute(
            "SELECT password, nombre FROM usuarios WHERE id = ?", (g.user_id,)
        ).fetchone()

        if not _check_password(actual, user["password"]):
            return jsonify({"error": "La contraseña actual es incorrecta"}), 401

        conn.execute(
            "UPDATE usuarios SET password = ?, actualizado_en = datetime('now') WHERE id = ?",
            (_hash_password(nueva), g.user_id),
        )
        _log_historial(
            conn,
            tipo="edicion",
            titulo="Cambio de contraseña",
            descripcion=f"{user['nombre']} cambió su contraseña",
            usuario=user["nombre"],
        )
        conn.commit()
        return jsonify({"mensaje": "Contraseña actualizada correctamente"}), 200
    finally:
        conn.close()


# ════════════════════════════════════════════════════════════════════════════
# POST /api/auth/logout
# ════════════════════════════════════════════════════════════════════════════

@auth_bp.post("/logout")
@login_required
def logout():
    """
    El cliente debe eliminar el token de su almacenamiento.
    Este endpoint solo registra el evento en historial.
    """
    conn = get_connection()
    try:
        user = conn.execute(
            "SELECT nombre FROM usuarios WHERE id = ?", (g.user_id,)
        ).fetchone()
        nombre = user["nombre"] if user else "Desconocido"
        _log_historial(
            conn,
            tipo="acceso",
            titulo="Cierre de sesión",
            descripcion=f"{nombre} cerró sesión",
            usuario=nombre,
        )
        conn.commit()
        return jsonify({"mensaje": "Sesión cerrada correctamente"}), 200
    finally:
        conn.close()