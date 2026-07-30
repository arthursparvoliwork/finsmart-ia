"""
transactions.py — Rotas REST para transações e IA de categorização.

Recursos:
- POST   /api/transactions          → cria transação (com categorização IA opcional)
- GET    /api/transactions          → lista transações do usuário
- GET    /api/transactions/<id>     → busca uma transação específica
- PUT    /api/transactions/<id>     → atualiza
- DELETE /api/transactions/<id>     → remove
- GET    /api/transactions/resumo   → totais pra dashboard

- POST   /api/ai/categorizar        → testa categorização IA sem salvar
"""
from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.core.extensions import db
from app.routes.deps import get_db, require_user
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    CategorizacaoRequest,
)
from app.services.ai_service import AIService
from app.services.transaction_service import TransactionService

# Blueprint = grupo de rotas relacionadas
transactions_bp = Blueprint("transactions", __name__)


def _make_service() -> TransactionService:
    """Constrói TransactionService com db e AIService (injeção de dependência)."""
    return TransactionService(get_db(), AIService())


# =====================================================
# CRUD DE TRANSAÇÕES
# =====================================================
@transactions_bp.route("", methods=["POST"])
def create_transaction():
    """POST /api/transactions — cria uma transação."""
    user = require_user()
    data = request.get_json(silent=True) or {}

    try:
        payload = TransactionCreate(**data)
    except ValidationError as err:
        return jsonify({"error": "Dados inválidos", "details": err.errors()}), 422

    service = _make_service()
    transaction = service.criar(
        user_id=user.id,
        valor=payload.valor,
        data=payload.data,
        descricao=payload.descricao,
        tipo=payload.tipo,
        categoria=payload.categoria,
        observacoes=payload.observacoes,
        categorizar_ia=payload.categorizar_ia,
    )
    return jsonify(TransactionResponse.model_validate(transaction).model_dump()), 201


@transactions_bp.route("", methods=["GET"])
def list_transactions():
    """GET /api/transactions — lista transações do usuário logado."""
    user = require_user()
    service = _make_service()
    transacoes = service.listar_por_usuario(user.id)
    return jsonify([
        TransactionResponse.model_validate(t).model_dump() for t in transacoes
    ])


@transactions_bp.route("/resumo", methods=["GET"])
def resumo():
    """GET /api/transactions/resumo — totais pra dashboard."""
    user = require_user()
    service = _make_service()
    return jsonify(service.resumo(user.id))


@transactions_bp.route("/<int:transaction_id>", methods=["GET"])
def get_transaction(transaction_id: int):
    """GET /api/transactions/<id> — busca uma transação específica."""
    user = require_user()
    service = _make_service()
    transaction = service.obter_por_id(transaction_id, user.id)
    if transaction is None:
        return jsonify({"error": "Transação não encontrada"}), 404
    return jsonify(TransactionResponse.model_validate(transaction).model_dump())


@transactions_bp.route("/<int:transaction_id>", methods=["PUT"])
def update_transaction(transaction_id: int):
    """PUT /api/transactions/<id> — atualiza uma transação."""
    user = require_user()
    data = request.get_json(silent=True) or {}

    try:
        payload = TransactionUpdate(**data)
    except ValidationError as err:
        return jsonify({"error": "Dados inválidos", "details": err.errors()}), 422

    service = _make_service()
    transaction = service.atualizar(
        transaction_id, user.id, **payload.model_dump(exclude_unset=True)
    )
    if transaction is None:
        return jsonify({"error": "Transação não encontrada"}), 404
    return jsonify(TransactionResponse.model_validate(transaction).model_dump())


@transactions_bp.route("/<int:transaction_id>", methods=["DELETE"])
def delete_transaction(transaction_id: int):
    """DELETE /api/transactions/<id> — remove uma transação."""
    user = require_user()
    service = _make_service()
    deletado = service.deletar(transaction_id, user.id)
    if not deletado:
        return jsonify({"error": "Transação não encontrada"}), 404
    return jsonify({"message": "Transação removida"}), 200


# =====================================================
# IA: CATEGORIZAÇÃO
# =====================================================
@transactions_bp.route("/categorizar", methods=["POST"])
def categorizar():
    """POST /api/transactions/categorizar — testa categorização IA sem salvar."""
    user = require_user()  # só usuários logados podem usar a IA
    data = request.get_json(silent=True) or {}

    try:
        payload = CategorizacaoRequest(**data)
    except ValidationError as err:
        return jsonify({"error": "Dados inválidos", "details": err.errors()}), 422

    ai = AIService()
    resultado = ai.categorizar(payload.descricao)
    return jsonify({
        "descricao": payload.descricao,
        "categoria": resultado["categoria"],
        "confianca": resultado["confianca"],
    })
