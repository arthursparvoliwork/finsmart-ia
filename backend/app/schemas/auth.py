"""
auth.py — Schemas de autenticação (cadastro e login).

Pydantic valida automaticamente:
- Tipos corretos (email tem @, senha é string, etc.)
- Tamanhos mínimos/máximos
- Formato de email

Se o usuário mandar lixo, Pydantic rejeita ANTES do nosso código rodar.
"""
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Dados que o usuário envia ao se cadastrar."""

    name: str = Field(..., min_length=2, max_length=100, description="Nome completo")
    email: EmailStr = Field(..., description="Email válido")
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="Senha (mínimo 6 caracteres)",
    )


class LoginRequest(BaseModel):
    """Dados que o usuário envia ao fazer login."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class UserResponse(BaseModel):
    """Como respondemos com dados do usuário (NUNCA incluir password_hash!)."""

    id: int
    name: str
    email: EmailStr

    # Configuração: permite criar este schema a partir de um objeto SQLAlchemy
    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Resposta de login: dados do usuário + token JWT."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
