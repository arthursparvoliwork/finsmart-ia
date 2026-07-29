"""
test_auth.py — Testes das rotas de autenticação.

Cada função 'test_...' é um caso de teste.
NOMES DESCRIPTIVOS importam: 'test_register_com_dados_validos_retorna_201'
ja diz exatamente o que está sendo validado.
"""


def test_register_com_dados_validos_retorna_201(client):
    """Cadastro correto deve criar usuário e retornar 201."""
    response = client.post("/api/auth/register", json={
        "name": "João da Silva",
        "email": "joao@example.com",
        "password": "minhasenha123",
    })

    assert response.status_code == 201
    body = response.get_json()
    assert body["email"] == "joao@example.com"
    assert body["name"] == "João da Silva"
    assert "id" in body
    # CRÍTICO: a resposta JAMAIS pode incluir a senha ou hash!
    assert "password" not in body
    assert "password_hash" not in body


def test_register_com_email_duplicado_retorna_409(client):
    """Não pode cadastrar 2 usuários com o mesmo email."""
    payload = {
        "name": "Maria",
        "email": "maria@example.com",
        "password": "senha12345",
    }
    client.post("/api/auth/register", json=payload)

    # Tenta cadastrar de novo com MESMO email
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409


def test_register_com_email_invalido_retorna_422(client):
    """Email sem @ deve ser rejeitado pelo Pydantic."""
    response = client.post("/api/auth/register", json={
        "name": "Carlos",
        "email": "nao_e_email",
        "password": "senha12345",
    })
    assert response.status_code == 422


def test_register_com_senha_curta_retorna_422(client):
    """Senha com menos de 6 caracteres deve ser rejeitada."""
    response = client.post("/api/auth/register", json={
        "name": "Ana",
        "email": "ana@example.com",
        "password": "123",  # só 3 caracteres
    })
    assert response.status_code == 422


def test_login_com_credenciais_validas_retorna_token(client):
    """Login correto deve retornar um token JWT válido."""
    # Primeiro cadastra
    client.post("/api/auth/register", json={
        "name": "Pedro",
        "email": "pedro@example.com",
        "password": "pedro12345",
    })

    # Depois faz login
    response = client.post("/api/auth/login", json={
        "email": "pedro@example.com",
        "password": "pedro12345",
    })

    assert response.status_code == 200
    body = response.get_json()
    assert "access_token" in body
    # Token JWT começa com 3 partes separadas por ponto
    assert body["access_token"].count(".") == 2
    assert body["token_type"] == "bearer"


def test_login_com_senha_errada_retorna_401(client):
    """Login com senha errada deve retornar 401."""
    client.post("/api/auth/register", json={
        "name": "Júlia",
        "email": "julia@example.com",
        "password": "julia12345",
    })

    response = client.post("/api/auth/login", json={
        "email": "julia@example.com",
        "password": "SENHA_ERRADA",
    })
    assert response.status_code == 401
    assert "Credenciais" in response.get_json()["error"]


def test_login_com_email_inexistente_retorna_401(client):
    """
    Login com email que não existe deve dar 401 com MESMA mensagem
    de "senha errada" (pra não revelar quais emails existem).
    """
    response = client.post("/api/auth/login", json={
        "email": "ninguem@example.com",
        "password": "qualquer",
    })
    assert response.status_code == 401
