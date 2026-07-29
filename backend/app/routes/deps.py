"""
deps.py — Dependências reutilizáveis nas rotas.

Em Flask não existe injeção de dependência nativa como no FastAPI,
mas o padrão é: funções utilitárias que retornam objetos prontos.
"""
from typing import Optional

from flask import request, g
from sqlalchemy import select
from sqlalchemy.orm import Session

import jwt

from app.core.config import get_settings
from app.core.extensions import db
from app.core.security import SecurityService
from app.models import User


def get_security() -> SecurityService:
    """Retorna o serviço de segurança com as settings atuais."""
    return SecurityService(get_settings())


def get_db() -> Session:
    """Retorna a sessão atual do banco (uma por requisição)."""
    return db.session


def get_current_user() -> Optional[User]:
    """
    Extrai o usuário autenticado a partir do header Authorization.

    Como usar nas rotas:
        user = get_current_user()
        if not user:
            return jsonify({"error": "Não autorizado"}), 401

    O token vem no formato:  Authorization: Bearer <token>
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.removeprefix("Bearer ").strip()
    security = get_security()

    try:
        payload = security.decode_token(token)
    except jwt.PyJWTError:
        # Token inválido, expirado ou assinatura errada
        return None

    # 'sub' guarda o id do usuário (criamos no security.py)
    user_id = payload.get("sub")
    if user_id is None:
        return None

    # Busca o usuário no banco
    session = get_db()
    user = session.scalar(select(User).where(User.id == int(user_id)))

    # Salva o usuário na request p/ outras funções reusarem (g = "global" da req)
    if user:
        g.current_user = user

    return user


def require_user() -> User:
    """
    Versão que JÁ levanta erro se não tiver usuário.
    Útil quando a rota EXIGE login (não é opcional).
    """
    user = get_current_user()
    if user is None:
        # Levanta um erro que o error handler pode capturar
        from werkzeug.exceptions import Unauthorized
        raise Unauthorized(description="Token inválido ou ausente")
    return user
