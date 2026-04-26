from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

from backend.routes.auth import auth_bp

from backend.config   import SECRET_KEY, DEBUG, PORT
from backend.database import init_db

from backend.routes.actividades import actividades_bp
from backend.routes.usuarios    import usuarios_bp
from backend.routes.historial   import historial_bp
from backend.routes.reportes    import reportes_bp
from backend.routes.ia          import ia_bp
from ia.ollama_client           import verificar_conexion

BASE_DIR = os.path.dirname(__file__)

def create_app():
    app = Flask(__name__, static_folder='frontend', static_url_path='/frontend')
    app.secret_key = SECRET_KEY

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(actividades_bp, url_prefix='/api')
    app.register_blueprint(usuarios_bp,    url_prefix='/api')
    app.register_blueprint(historial_bp,   url_prefix='/api')
    app.register_blueprint(reportes_bp,    url_prefix='/api')
    app.register_blueprint(ia_bp,          url_prefix='/api')

    app.register_blueprint(auth_bp)

    @app.route('/api/status')
    def status():
        return jsonify({
            'db':     'Conectado',
            'ollama': 'Activo' if verificar_conexion() else 'Sin conexión',
            'version': '1.0.0',
        })

    @app.route('/')
    def index():
        return send_from_directory(
            os.path.join(BASE_DIR, 'frontend', 'pages', 'dashboard'),
            'index.html'
        )

    @app.route('/frontend/<path:filename>')
    def frontend(filename):
        return send_from_directory(
            os.path.join(BASE_DIR, 'frontend'),
            filename
        )

    return app


if __name__ == '__main__':
    init_db()
    app = create_app()
    print(f"\n[AcademiX] Servidor corriendo en http://localhost:{PORT}")
    print(f"[AcademiX] Debug: {DEBUG}\n")
    app.run(host='0.0.0.0', port=5000, debug=True)