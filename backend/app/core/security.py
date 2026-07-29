"""
security.py — Serviços de segurança: hash de senha e tokens JWT.

PRINCÍPIO SOLID 'S' (Single Responsibility):
- Esta classe SÓ sabe sobre senhas e tokens.
- Ela não sabe de banco de dados, não sabe de HTTP.
- Fácil de testar isoladamente, fácil de trocar a implementação.

PRINCÍPIO SOLID 'D' (Dependency Inversion):
- A classe recebe 'settings' no construtor, em vez de buscar globalmente.
- Em testes, podemos passar settings diferentes facilmente.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.core.config import Settings


class SecurityService:
    """
    Centraliza operações de segurança:
    - Hash e verificação de senhas (bcrypt)
    - Criação e validação de tokens JWT
    """

    def __init__(self, settings: Settings):
        # Recebe settings por injeção de dependência (Dependency Inversion)
        self._settings = settings
        # Algoritmo de assinatura do JWT (HS256 é padrão e seguro)
        self._algorithm = "HS256"

    # ---------------------------------------------------------
    # SENHAS
    # ---------------------------------------------------------
    def hash_password(self, password: str) -> str:
        """
        Converte a senha em texto puro para um hash bcrypt seguro.
        O hash NUNCA pode ser revertido para a senha original.
        """
        # bcrypt exige bytes, então convertemos str -> bytes
        password_bytes = password.encode("utf-8")
        # gensalt() gera um "salt" aleatório pra cada senha
        salt = bcrypt.gensalt(rounds=12)  # rounds=12 = equilíbrio segurança/performance
        hashed = bcrypt.hashpw(password_bytes, salt)
        # Volta pra str pra salvar no banco
        return hashed.decode("utf-8")

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verifica se a senha bate com o hash salvo.
        Retorna True se a senha está correta, False caso contrário.
        """
        password_bytes = password.encode("utf-8")
        hash_bytes = password_hash.encode("utf-8")
        # compare_digest evita timing attacks (ataque por tempo de resposta)
        return bcrypt.checkpw(password_bytes, hash_bytes)

    # ---------------------------------------------------------
    # TOKENS JWT
    # ---------------------------------------------------------
    def create_access_token(self, user_id: int) -> str:
        """
        Cria um token JWT que identifica o usuário.
        Quem tiver o token + o jwt_secret pode confirmar quem é o dono.
        """
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=self._settings.jwt_expire_hours)

        # 'payload' = conteúdo do token (qualquer dado, mas NUNCA senhas!)
        payload: dict[str, Any] = {
            "sub": str(user_id),  # 'sub' = subject (id do usuário, padrão JWT)
            "iat": now.timestamp(),  # 'iat' = issued at (quando foi criado)
            "exp": expires_at.timestamp(),  # 'exp' = expiration (quando expira)
        }

        # jwt.encode ASSINA o payload com o segredo, gerando o token final
        token = jwt.encode(payload, self._settings.jwt_secret, algorithm=self._algorithm)
        return token

    def decode_token(self, token: str) -> dict[str, Any]:
        """
        Decodifica e valida um token JWT.
        Levanta jwt.PyJWTError (ou subclasses) se o token for inválido ou expirou.
        """
        # verify=True garante que a assinatura é checada (não dá pra falsificar)
        return jwt.decode(
            token,
            self._settings.jwt_secret,
            algorithms=[self._algorithm],
        )
