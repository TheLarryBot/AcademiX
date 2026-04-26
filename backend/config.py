# ============================================
# AcademiX — config.py
# Toda la configuración del sistema en un lugar.
# ============================================

import os

# — Base de datos —
DATABASE = os.path.join(os.path.dirname(__file__), 'academix.db')

# — Flask —
SECRET_KEY = os.environ.get('SECRET_KEY', 'a9f4c8e2d6b1f3c7e8a2d9f0b4c6e1a3d7f8b2c5e9d1a6f4')
DEBUG      = os.environ.get('DEBUG', 'true').lower() == 'true'
PORT       = int(os.environ.get('PORT', 5000))

# — Ollama (IA local) —
OLLAMA_URL   = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
OLLAMA_MODEL = 'llama3.2'