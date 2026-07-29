"""
extensions.py — Instâncias "globais" das extensões Flask.

Por que declarar aqui separadas do app?
- Padrão da Flask: extensões são criadas SEM o app,
  depois "ligadas" ao app no create_app() com db.init_app(app).
- Evita referência circular (app importa routes, routes importam db...).
"""
from flask_sqlalchemy import SQLAlchemy

# Instância ÚNICA do SQLAlchemy usada em todo o app.
# Qualquer arquivo que precisar do banco importa isto.
db = SQLAlchemy()
