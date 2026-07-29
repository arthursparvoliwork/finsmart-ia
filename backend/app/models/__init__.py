"""
__init__.py dos modelos.

Centraliza as importações: em vez de importar de cada arquivo separado,
outras partes do código fazem:  from app.models import User, Transaction
"""
from app.core.extensions import db
from app.models.base import TimestampMixin
from app.models.user import User
from app.models.transaction import Transaction

__all__ = ["db", "TimestampMixin", "User", "Transaction"]
