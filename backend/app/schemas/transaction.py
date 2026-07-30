"""
transaction.py — Schemas Pydantic para transações e IA.
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class TransactionBase(BaseModel):
    """Campos comuns a criar e atualizar."""
    valor: Decimal = Field(..., gt=0, description="Valor (positivo)")
    data: date
    descricao: str = Field(..., min_length=1, max_length=255)
    tipo: str = Field(..., description="receita ou despesa")
    categoria: Optional[str] = None
    observacoes: Optional[str] = None

    @field_validator("tipo")
    @classmethod
    def tipo_valido(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in {"receita", "despesa"}:
            raise ValueError("tipo deve ser 'receita' ou 'despesa'")
        return v


class TransactionCreate(TransactionBase):
    """Criação de transação."""
    # Se True, chama a IA pra preencher a categoria automaticamente
    categorizar_ia: bool = Field(default=True)


class TransactionUpdate(BaseModel):
    """Atualização parcial (todos os campos opcionais)."""
    valor: Optional[Decimal] = Field(default=None, gt=0)
    data: Optional[date] = None
    descricao: Optional[str] = Field(default=None, min_length=1, max_length=255)
    tipo: Optional[str] = None
    categoria: Optional[str] = None
    observacoes: Optional[str] = None

    @field_validator("tipo")
    @classmethod
    def tipo_valido(cls, v):
        if v is None:
            return v
        v = v.lower().strip()
        if v not in {"receita", "despesa"}:
            raise ValueError("tipo deve ser 'receita' ou 'despesa'")
        return v


class TransactionResponse(TransactionBase):
    """Resposta com id e user_id (não vem do cliente)."""
    id: int
    user_id: int
    model_config = {"from_attributes": True}


# --- Schemas de IA ---
class CategorizacaoRequest(BaseModel):
    """Pedido pra IA categorizar uma descrição."""
    descricao: str = Field(..., min_length=1, max_length=255)


class CategorizacaoResponse(BaseModel):
    """Resultado da categorização por IA."""
    descricao: str
    categoria: Optional[str]
    confianca: float
