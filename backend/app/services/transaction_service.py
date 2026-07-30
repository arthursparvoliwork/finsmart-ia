"""
transaction_service.py — Regras de negócio de transações.

Esta camada fica entre as rotas (HTTP) e os modelos (banco).
- Rotas chamam estas funções
- Models guardam dados

🎓 POR QUE usar IA aqui?
Quando o usuário cria uma transação sem categoria, chamamos a IA
(CategorizerService) pra prever automaticamente. É a mágica do FinSmart.
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import Transaction
from app.services.ai_service import AIService


class TransactionService:
    """
    CRUD de transações + agregações pra dashboard.
    """

    def __init__(self, db: Session, ai: Optional[AIService] = None):
        # Injeção de dependência
        self._db = db
        # AIService é Singleton (caro de criar), mas pode ser injetado (testes)
        self._ai = ai or AIService()

    # ---------------------------------------------------------
    # CRIAÇÃO
    # ---------------------------------------------------------
    def criar(
        self,
        user_id: int,
        valor: Decimal,
        data: date,
        descricao: str,
        tipo: str,
        categoria: Optional[str] = None,
        observacoes: Optional[str] = None,
        categorizar_ia: bool = True,
    ) -> Transaction:
        """
        Cria uma transação. Se não tiver categoria e categorizar_ia=True,
        chama a IA pra prever.
        """
        # IA só preenche se não tiver categoria explícita
        if not categoria and categorizar_ia:
            resultado_ia = self._ai.categorizar(descricao)
            categoria = resultado_ia["categoria"]

        transaction = Transaction(
            user_id=user_id,
            valor=valor,
            data=data,
            descricao=descricao,
            tipo=tipo,
            categoria=categoria,
            observacoes=observacoes,
        )
        self._db.add(transaction)
        self._db.commit()
        self._db.refresh(transaction)
        return transaction

    # ---------------------------------------------------------
    # LEITURA
    # ---------------------------------------------------------
    def listar_por_usuario(
        self, user_id: int, limite: int = 100
    ) -> list[Transaction]:
        """Lista transações de um usuário (mais recentes primeiro)."""
        stmt = (
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.data.desc(), Transaction.id.desc())
            .limit(limite)
        )
        return list(self._db.scalars(stmt))

    def obter_por_id(self, transaction_id: int, user_id: int) -> Optional[Transaction]:
        """Busca uma transação garantindo que pertence ao usuário."""
        stmt = select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id,
        )
        return self._db.scalar(stmt)

    # ---------------------------------------------------------
    # ATUALIZAÇÃO
    # ---------------------------------------------------------
    def atualizar(self, transaction_id: int, user_id: int, **campos) -> Optional[Transaction]:
        """Atualiza campos de uma transação (só se pertencer ao usuário)."""
        transaction = self.obter_por_id(transaction_id, user_id)
        if transaction is None:
            return None

        for campo, valor in campos.items():
            if valor is not None and hasattr(transaction, campo):
                setattr(transaction, campo, valor)

        self._db.commit()
        self._db.refresh(transaction)
        return transaction

    # ---------------------------------------------------------
    # REMOÇÃO
    # ---------------------------------------------------------
    def deletar(self, transaction_id: int, user_id: int) -> bool:
        """Deleta uma transação (só se pertencer ao usuário)."""
        transaction = self.obter_por_id(transaction_id, user_id)
        if transaction is None:
            return False
        self._db.delete(transaction)
        self._db.commit()
        return True

    # ---------------------------------------------------------
    # AGREGAÇÕES (pra dashboard)
    # ---------------------------------------------------------
    def resumo(self, user_id: int) -> dict:
        """Retorna totais (receitas, despesas, saldo)."""
        # Soma das receitas
        stmt_rec = select(func.coalesce(func.sum(Transaction.valor), 0)).where(
            Transaction.user_id == user_id, Transaction.tipo == "receita"
        )
        total_receitas = self._db.scalar(stmt_rec) or Decimal("0")

        stmt_desp = select(func.coalesce(func.sum(Transaction.valor), 0)).where(
            Transaction.user_id == user_id, Transaction.tipo == "despesa"
        )
        total_despesas = self._db.scalar(stmt_desp) or Decimal("0")

        return {
            "total_receitas": float(total_receitas),
            "total_despesas": float(total_despesas),
            "saldo": float(total_receitas - total_despesas),
        }
