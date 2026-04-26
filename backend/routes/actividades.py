# ============================================
# AcademiX — routes/actividades.py
# GET  /api/actividades          → listar (con filtros opcionales)
# POST /api/actividades          → crear
# GET  /api/actividades/<id>     → detalle
# PUT  /api/actividades/<id>     → editar
# DELETE /api/actividades/<id>   → eliminar
# ============================================

from flask import Blueprint, request, jsonify
from backend.database import get_connection

actividades_bp = Blueprint('actividades', __name__)


def _row_to_dict(row):
    return dict(row) if row else None


# ── Listar / filtrar ──────────────────────────────────────────────────────────
@actividades_bp.route('/actividades', methods=['GET'])
def listar():
    q         = request.args.get('q', '').strip()
    tipologia = request.args.get('tipologia', '').strip()
    modalidad = request.args.get('modalidad', '').strip()
    programa  = request.args.get('programa', '').strip()

    sql    = "SELECT * FROM actividades WHERE 1=1"
    params = []

    if q:
        sql += " AND (nombre LIKE ? OR descripcion LIKE ?)"
        params += [f'%{q}%', f'%{q}%']
    if tipologia:
        sql += " AND tipologia = ?"
        params.append(tipologia)
    if modalidad:
        sql += " AND modalidad = ?"
        params.append(modalidad)
    if programa:
        sql += " AND programa = ?"
        params.append(programa)

    sql += " ORDER BY creado_en DESC"

    conn = get_connection()
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    return jsonify({'actividades': [_row_to_dict(r) for r in rows]})


# ── Crear ─────────────────────────────────────────────────────────────────────
@actividades_bp.route('/actividades', methods=['POST'])
def crear():
    data = request.get_json()

    if not data or not data.get('nombre'):
        return jsonify({'error': 'El nombre es obligatorio'}), 400

    conn = get_connection()
    cursor = conn.execute("""
        INSERT INTO actividades
            (mes, periodo, fecha_inicio, fecha_fin, tipologia, modalidad,
             programa, nombre, descripcion, objetivo, num_participantes,
             horas_dedicadas, recursos, resultados, observaciones)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        data.get('mes'), data.get('periodo'),
        data.get('fecha_inicio'), data.get('fecha_fin'),
        data.get('tipologia'), data.get('modalidad'),
        data.get('programa'), data['nombre'],
        data.get('descripcion'), data.get('objetivo'),
        data.get('num_participantes', 0), data.get('horas_dedicadas', 0),
        data.get('recursos'), data.get('resultados'), data.get('observaciones'),
    ))

    # Registrar en historial
    conn.execute("""
        INSERT INTO historial (tipo, titulo, descripcion, usuario)
        VALUES ('creacion', ?, 'Se registró una nueva actividad de extensión', 'Usuario Demo')
    """, (f"Actividad creada: {data['nombre']}",))

    conn.commit()
    nueva_id = cursor.lastrowid
    actividad = _row_to_dict(conn.execute("SELECT * FROM actividades WHERE id=?", (nueva_id,)).fetchone())
    conn.close()

    return jsonify({'actividad': actividad}), 201


# ── Detalle ───────────────────────────────────────────────────────────────────
@actividades_bp.route('/actividades/<int:id>', methods=['GET'])
def detalle(id):
    conn = get_connection()
    row  = conn.execute("SELECT * FROM actividades WHERE id=?", (id,)).fetchone()
    conn.close()

    if not row:
        return jsonify({'error': 'Actividad no encontrada'}), 404

    return jsonify({'actividad': _row_to_dict(row)})


# ── Editar ────────────────────────────────────────────────────────────────────
@actividades_bp.route('/actividades/<int:id>', methods=['PUT'])
def editar(id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Sin datos'}), 400

    conn = get_connection()
    existe = conn.execute("SELECT id FROM actividades WHERE id=?", (id,)).fetchone()
    if not existe:
        conn.close()
        return jsonify({'error': 'Actividad no encontrada'}), 404

    conn.execute("""
        UPDATE actividades SET
            mes=?, periodo=?, fecha_inicio=?, fecha_fin=?, tipologia=?,
            modalidad=?, programa=?, nombre=?, descripcion=?, objetivo=?,
            num_participantes=?, horas_dedicadas=?, recursos=?,
            resultados=?, observaciones=?,
            actualizado_en=datetime('now')
        WHERE id=?
    """, (
        data.get('mes'), data.get('periodo'),
        data.get('fecha_inicio'), data.get('fecha_fin'),
        data.get('tipologia'), data.get('modalidad'),
        data.get('programa'), data.get('nombre'),
        data.get('descripcion'), data.get('objetivo'),
        data.get('num_participantes', 0), data.get('horas_dedicadas', 0),
        data.get('recursos'), data.get('resultados'),
        data.get('observaciones'), id,
    ))

    conn.execute("""
        INSERT INTO historial (tipo, titulo, descripcion, usuario)
        VALUES ('edicion', ?, 'Se actualizó la información de una actividad existente', 'Usuario Demo')
    """, (f"Actividad modificada: {data.get('nombre', '')}",))

    conn.commit()
    actualizada = _row_to_dict(conn.execute("SELECT * FROM actividades WHERE id=?", (id,)).fetchone())
    conn.close()

    return jsonify({'actividad': actualizada})


# ── Eliminar ──────────────────────────────────────────────────────────────────
@actividades_bp.route('/actividades/<int:id>', methods=['DELETE'])
def eliminar(id):
    conn = get_connection()
    row  = conn.execute("SELECT nombre FROM actividades WHERE id=?", (id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Actividad no encontrada'}), 404

    conn.execute("DELETE FROM actividades WHERE id=?", (id,))
    conn.execute("""
        INSERT INTO historial (tipo, titulo, descripcion, usuario)
        VALUES ('eliminacion', ?, 'Se eliminó una actividad del sistema', 'Usuario Demo')
    """, (f"Actividad eliminada: {row['nombre']}",))

    conn.commit()
    conn.close()

    return jsonify({'mensaje': 'Actividad eliminada correctamente'})