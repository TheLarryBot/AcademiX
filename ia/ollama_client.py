# ============================================
# AcademiX — ia/ollama_client.py
# Wrapper para comunicarse con Ollama local.
# Cambia OLLAMA_MODEL en config.py para usar
# otro modelo (llama3, mistral, gemma, etc.)
# ============================================

import requests
from backend.config import OLLAMA_URL, OLLAMA_MODEL


def generar(prompt: str, temperature: float = 0.7) -> str:
    """
    Envía un prompt a Ollama y retorna la respuesta como texto.

    Args:
        prompt:      El texto del prompt a enviar.
        temperature: Creatividad del modelo (0.0 a 1.0).

    Returns:
        Texto generado por el modelo.

    Raises:
        ConnectionError: Si Ollama no está corriendo.
    """
    url  = f"{OLLAMA_URL}/api/generate"
    body = {
        "model":  OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": 500,   # máximo de tokens en la respuesta
        }
    }

    try:
        response = requests.post(url, json=body, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get('response', '').strip()

    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            f"No se pudo conectar a Ollama en {OLLAMA_URL}. "
            "Asegúrate de que Ollama esté corriendo con: ollama serve"
        )
    except requests.exceptions.Timeout:
        raise ConnectionError("Ollama tardó demasiado en responder. Intenta de nuevo.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error al llamar a Ollama: {e}")


def verificar_conexion() -> bool:
    """Verifica si Ollama está activo. Retorna True/False."""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return response.status_code == 200
    except Exception:
        return False