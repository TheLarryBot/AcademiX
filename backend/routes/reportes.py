# ============================================
# AcademiX — routes/reportes.py
# GET /api/reportes?tipo=general     → JSON
# GET /api/reportes/csv?tipo=general → descarga CSV
# ============================================

import csv
import io
from datetime import datetime
from flask import Blueprint, request, jsonify, Response
from backend.database import get_connection

reportes_bp = Blueprint('reportes', __name__)

COLUMNAS_CSV = [
    'id', 'nombre', 'tipologia', 'modalidad', 'programa',
    'mes', 'periodo', 'fecha_inicio', 'fecha_fin',
    'num_participantes', 'horas_dedicadas',
    'descripcion', 'objetivo', 'recursos', 'resultados', 'observaciones',
    'creado_en',
]


def _build_query(tipo, args):
    """Construye la query SQL según el tipo de reporte."""
    sql    = "SELECT * FROM actividades WHERE 1=1"
    params = []

    if tipo == 'tipologia' and args.get('tipologia'):
        sql += " AND tipologia = ?"
        params.append(args['tipologia'])

    elif tipo == 'programa' and args.get('programa'):
        sql += " AND programa = ?"
        params.append(args['programa'])

    elif tipo == 'mensual':
        mes = args.get('mes', '')
        if mes:
            sql += " AND mes = ?"
            params.append(mes)

    elif tipo == 'anual':
        year = args.get('year', str(datetime.now().year))
        sql += " AND strftime('%Y', fecha_inicio) = ?"
        params.append(year)

    sql += " ORDER BY fecha_inicio DESC"
    return sql, params


@reportes_bp.route('/reportes', methods=['GET'])
def ver_reporte():
    tipo = request.args.get('tipo', 'general')
    sql, params = _build_query(tipo, request.args)

    conn = get_connection()
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    return jsonify({
        'tipo':       tipo,
        'total':      len(rows),
        'actividades': [dict(r) for r in rows],
    })


@reportes_bp.route('/reportes/csv', methods=['GET'])
def descargar_csv():
    tipo = request.args.get('tipo', 'general')
    sql, params = _build_query(tipo, request.args)

    conn = get_connection()
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=COLUMNAS_CSV, extrasaction='ignore')
    writer.writeheader()
    for row in rows:
        writer.writerow(dict(row))

    filename = f"academix_reporte_{tipo}_{datetime.now().strftime('%Y%m%d')}.csv"

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )