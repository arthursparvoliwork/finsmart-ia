"""
auth.py — Rotas REST de autenticação: /api/auth/register e /api/auth/login.

PRINCÍPIO SOLID:
- 'S': esta rota SÓ cuida de HTTP (recebe JSON, retorna JSON).
- A lógica (validar email, hashear senha) fica no AuthService.

Rota fina = fácil de ler, fácil de testar, fácil de trocar framework.
"""
from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.extensions import db
from app.core.security import SecurityService
from app.core.config import get_settings
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService

# Cria o blueprint. 'auth_bp' é o nome, __name__ ajuda no debug.
auth_bp = Blueprint("auth", __name__)


def _make_session() -> Session:
    """Pega a sessão do banco da requisição atual."""
    return db.session


def _make_auth_service() -> AuthService:
    """Constrói um AuthService com tudo que ele precisa (injeção de dependência)."""
    settings = get_settings()
    security = SecurityService(settings)
    return AuthService(_make_session(), security)


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    POST /api/auth/register
    Body JSON: { "name": "...", "email": "...", "password": "..." }
    """
    data = request.get_json(silent=True) or {}

    # 1. Valida entrada com Pydantic (rejeita email inválido, senha curta, etc.)
    try:
        payload = RegisterRequest(**data)
    except ValidationError as err:
        # 422 = "Unprocessable Entity" (HTTP padrão pra erro de validação)
        return jsonify({"error": "Dados inválidos", "details": err.errors()}), 422

    # 2. Chama o service com a regra de negócio
    service = _make_auth_service()
    try:
        user = service.register(payload.name, payload.email, payload.password)
    except ValueError as err:
        # 409 = "Conflict" (email já existe)
        return jsonify({"error": str(err)}), 409

    # 3. Resposta nunca inclui senha/hash
    return jsonify(UserResponse.model_validate(user).model_dump()), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    POST /api/auth/login
    Body JSON: { "email": "...", "password": "..." }
    """
    data = request.get_json(silent=True) or {}

    try:
        payload = LoginRequest(**data)
    except ValidationError as err:
        return jsonify({"error": "Dados inválidos", "details": err.errors()}), 422

    service = _make_auth_service()
    try:
        user, token = service.login(payload.email, payload.password)
    except ValueError:
        # 401 = "Unauthorized"
        return jsonify({"error": "Credenciais inválidas"}), 401

    response = TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )
    return jsonify(response.model_dump()), 200
