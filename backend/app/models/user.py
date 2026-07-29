"""
user.py — Modelo do usuário.

APLICAÇÃO DO SOLID:
- 'S' (Single Responsibility): esta classe SÓ representa a tabela de usuários.
  Ela não sabe sobre JWT, não sabe sobre HTTP, não sabe sobre email.
  Apenas: "eu sou um usuário, tenho estes campos".
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.extensions import db
from app.models.base import TimestampMixin


class User(db.Model, TimestampMixin):
    """
    Representa um usuário da plataforma FinSmart IA.

    Herda de db.Model (a base do SQLAlchemy) e TimestampMixin (campos de data).
    """

    __tablename__ = "users"

    # --- Colunas ---
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # 'relationship' cria a conexão com as transações do usuário.
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",  # deletar user -> deleta as transações
    )

    def __repr__(self) -> str:
        """Como o objeto aparece em prints/logs (não mostra a senha!)."""
        return f"<User id={self.id} email={self.email}>"
