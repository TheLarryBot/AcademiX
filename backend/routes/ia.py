# ============================================
# AcademiX — routes/ia.py
# POST /api/ia/generar  → recibe prompt, llama
#                         a Ollama y devuelve
#                         la respuesta generada
# ============================================

from flask import Blueprint, request, jsonify
from ia.ollama_client import generar

ia_bp = Blueprint('ia', __name__)


@ia_bp.route('/ia/generar', methods=['POST'])
def generar_contenido():
    data   = request.get_json()
    prompt = data.get('prompt', '').strip() if data else ''

    if not prompt:
        return jsonify({'error': 'El prompt no puede estar vacío'}), 400

    try:
        respuesta = generar(prompt)
        return jsonify({'respuesta': respuesta})
    except ConnectionError as e:
        return jsonify({'error': str(e)}), 503
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500