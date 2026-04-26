# ============================================
# AcademiX — routes/historial.py
# GET /api/historial  → lista todos los cambios
# ============================================

from flask import Blueprint, jsonify
from backend.database import get_connection

historial_bp = Blueprint('historial', __name__)


@historial_bp.route('/historial', methods=['GET'])
def listar():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM historial ORDER BY fecha DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return jsonify({'historial': [dict(r) for r in rows]})