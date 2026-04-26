# ============================================
# AcademiX — routes/usuarios.py
# GET    /api/usuarios        → listar
# POST   /api/usuarios        → crear
# PUT    /api/usuarios/<id>   → editar
# DELETE /api/usuarios/<id>   → eliminar
# ============================================

from flask import Blueprint, request, jsonify
from backend.database import get_connection

usuarios_bp = Blueprint('usuarios', __name__)


@usuarios_bp.route('/usuarios', methods=['GET'])
def listar():
    conn  = get_connection()
    rows  = conn.execute("SELECT id, nombre, correo, rol, facultad, creado_en FROM usuarios ORDER BY creado_en DESC").fetchall()
    conn.close()
    return jsonify({'usuarios': [dict(r) for r in rows]})


@usuarios_bp.route('/usuarios', methods=['POST'])
def crear():
    data = request.get_json()
    if not data or not data.get('correo') or not data.get('nombre'):
        return jsonify({'error': 'Nombre y correo son obligatorios'}), 400

    conn = get_connection()
    try:
        cursor = conn.execute("""
            INSERT INTO usuarios (nombre, correo, password, rol, facultad)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data['nombre'], data['correo'],
            data.get('password', ''),
            data.get('rol', 'docente'),
            data.get('facultad', ''),
        ))
        conn.commit()
        nuevo_id = cursor.lastrowid
        usuario  = dict(conn.execute("SELECT id, nombre, correo, rol, facultad FROM usuarios WHERE id=?", (nuevo_id,)).fetchone())
        conn.close()
        return jsonify({'usuario': usuario}), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': 'El correo ya está registrado'}), 409


@usuarios_bp.route('/usuarios/<int:id>', methods=['PUT'])
def editar(id):
    data = request.get_json()
    conn = get_connection()
    conn.execute("""
        UPDATE usuarios SET nombre=?, correo=?, rol=?, facultad=? WHERE id=?
    """, (data.get('nombre'), data.get('correo'), data.get('rol'), data.get('facultad'), id))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Usuario actualizado'})


@usuarios_bp.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar(id):
    conn = get_connection()
    conn.execute("DELETE FROM usuarios WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Usuario eliminado'})