"""
run.py — Ponto de entrada para RODAR o servidor de desenvolvimento.

Como rodar (estando na pasta backend/):
    python run.py

NÃO use isso em produção! Em prod usamos um servidor WSGI como gunicorn:
    gunicorn "app:create_app()" --bind 0.0.0.0:5000
"""
from app import create_app

# Cria o app uma única vez
app = create_app()


if __name__ == "__main__":
    # debug=True: recarrega o código automaticamente quando você salva um arquivo
    # e mostra erros detalhados. NUNCA usar True em produção!
    app.run(host="127.0.0.1", port=5000, debug=True)
