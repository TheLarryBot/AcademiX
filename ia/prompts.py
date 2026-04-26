# ============================================
# AcademiX — ia/prompts.py
# Plantillas de prompts para cada campo del
# formulario de actividades.
# Centraliza el prompt engineering aquí.
# ============================================

BASE = (
    "Eres un asistente académico especializado en actividades de extensión "
    "universitaria. Responde SOLO con el contenido solicitado, sin títulos, "
    "encabezados ni explicaciones adicionales. Usa un tono formal y académico. "
    "Máximo 3 párrafos."
)


def descripcion(actividad: str) -> str:
    return f"{BASE}\n\nGenera una descripción detallada para la siguiente actividad de extensión: {actividad}"


def objetivo(actividad: str) -> str:
    return f"{BASE}\n\nRedacta el objetivo principal de esta actividad de extensión universitaria: {actividad}"


def observaciones(actividad: str) -> str:
    return f"{BASE}\n\nEscribe las observaciones relevantes para esta actividad de extensión: {actividad}"


def recursos(actividad: str) -> str:
    return f"{BASE}\n\nLista los recursos humanos, materiales y tecnológicos necesarios para: {actividad}"


def resultados(actividad: str) -> str:
    return f"{BASE}\n\nDescribe los resultados esperados al finalizar esta actividad de extensión: {actividad}"


# Mapa para usar desde la ruta de IA
PLANTILLAS = {
    'descripcion':   descripcion,
    'objetivo':      objetivo,
    'observaciones': observaciones,
    'recursos':      recursos,
    'resultados':    resultados,
}


def construir_prompt(tipo: str, actividad: str) -> str:
    """Retorna el prompt correcto según el tipo de campo."""
    fn = PLANTILLAS.get(tipo, descripcion)
    return fn(actividad)