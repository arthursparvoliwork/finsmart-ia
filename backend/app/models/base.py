"""
base.py — Modelo base que todas as tabelas vão herdar.

Usamos a integração do Flask-SQLAlchemy 3.x: db.Model já é uma classe base
declarativa moderna (SQLAlchemy 2.0). Criamos aqui um mixin com os campos
comuns (id, created_at, updated_at) para não repetir em cada modelo.
"""
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.extensions import db


class TimestampMixin:
    """
    Mixin (classe pra 'misturar' em outras) com campos de timestamp.
    Aplicação do princípio DRY (Don't Repeat Yourself).
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # banco preenche automaticamente
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),  # atualiza sozinho a cada UPDATE
    )


# Atalho: db.Model é a classe base que todas as tabelas herdam.
# Declarado aqui pra outros arquivos importarem como: from app.models.base import db, TimestampMixin
__all__ = ["db", "TimestampMixin"]
