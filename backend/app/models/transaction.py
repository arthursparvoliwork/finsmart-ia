"""
transaction.py — Modelo de transação financeira.

Cada transação representa uma entrada (receita) ou saída (despesa) de dinheiro.
Ex: "Comprei pão por R$ 10" ou "Recebi salário de R$ 5000".
"""
from datetime import date
from decimal import Decimal

from sqlalchemy import String, Numeric, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.extensions import db
from app.models.base import TimestampMixin


class Transaction(db.Model, TimestampMixin):
    """Uma transação financeira de um usuário."""

    __tablename__ = "transactions"

    # Tipos válidos (em vez de string livre, valores controlados)
    TIPO_RECEITA = "receita"
    TIPO_DESPESA = "despesa"
    TIPOS_VALIDOS = {TIPO_RECEITA, TIPO_DESPESA}

    # --- Colunas ---
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Decimal, NUNCA float, para dinheiro! (float dá erro de arredondamento)
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)

    # Categoria será preenchida pela IA (Scikit-Learn) depois.
    categoria: Mapped[str | None] = mapped_column(String(50), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="transactions")

    def __repr__(self) -> str:
        return f"<Transaction id={self.id} tipo={self.tipo} valor={self.valor}>"
