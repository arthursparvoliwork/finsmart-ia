"""
conftest.py — Configuração do pytest (fixtures reutilizáveis).

Fixtures = objetos prontos que o pytest injeta nos testes.
Aqui criamos: app de teste, cliente HTTP, banco em memória.
"""
import os
import sys
from pathlib import Path

# Garante que conseguimos importar o pacote 'app'
BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))

# Variáveis de ambiente MÍNIMAS para os testes (não dependem do .env real)
os.environ.setdefault("JWT_SECRET", "chave-super-secreta-de-teste-na-usar-em-prod-12345")
os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")  # banco em memória = rápido

import pytest
from app import create_app
from app.core.extensions import db


@pytest.fixture
def app():
    """
    Cria um app Flask só para testes.
    - Usa banco em MEMÓRIA (some quando o teste acaba, super rápido).
    - Cada teste começa com banco zerado.
    """
    app = create_app(testing=True)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """
    Cliente de teste — simula um navegador fazendo requisições.
    Uso: client.post("/api/auth/login", json={...})
    """
    return app.test_client()
