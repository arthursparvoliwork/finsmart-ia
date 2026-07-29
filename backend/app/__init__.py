"""
__init__.py — Application Factory (padrão Flask).

Em vez de criar o app globalmente (que dá problema em testes),
criamos uma FUNÇÃO create_app() que constrói e configura o app.
Cada teste pode chamar create_app(config_diferente).
"""
from flask import Flask, jsonify
from flask_cors import CORS

from app.core.config import get_settings
from app.core.extensions import db


def create_app(testing: bool = False) -> Flask:
    """
    Constrói a aplicação Flask.

    Padrão Application Factory: cada chamada cria um app novo,
    com configuração independente. Ideal para testes.
    """
    settings = get_settings()

    # Cria o Flask. __name__ ajuda o Flask a achar arquivos estáticos/templates.
    app = Flask(__name__)

    # Carrega config
    app.config["SECRET_KEY"] = settings.jwt_secret
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = testing

    # Inicializa extensões (liga ao app)
    db.init_app(app)
    CORS(app)  # Permite requisições do frontend React (diferente porta/porta)

    # Registra os blueprints (rotas agrupadas)
    _register_blueprints(app)

    # Tratamento de erros global (qualquer 404/500 volta em JSON bonito)
    _register_error_handlers(app)

    # Cria as tabelas automaticamente (em dev/test). Em prod usamos migrations.
    with app.app_context():
        # Importa modelos pra terem certeza de estarem registrados
        from app.models import User, Transaction  # noqa: F401
        db.create_all()

    return app


def _register_blueprints(app: Flask) -> None:
    """Conecta todos os blueprints (rotas) ao app."""
    from app.routes.auth import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")


def _register_error_handlers(app: Flask) -> None:
    """Converte erros Flask em respostas JSON (em vez de HTML feio)."""

    @app.errorhandler(401)
    def unauthorized(err):
        return jsonify({"error": str(err.description) if err.description else "Não autorizado"}), 401

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Recurso não encontrado"}), 404

    @app.errorhandler(500)
    def server_error(_):
        return jsonify({"error": "Erro interno do servidor"}), 500
