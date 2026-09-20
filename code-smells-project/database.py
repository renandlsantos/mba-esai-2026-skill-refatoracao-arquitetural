import sqlite3
from contextlib import contextmanager
from pathlib import Path
from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, descricao TEXT, preco REAL, estoque INTEGER, categoria TEXT, ativo INTEGER DEFAULT 1, criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, email TEXT, senha TEXT, tipo TEXT DEFAULT 'cliente', criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER, status TEXT DEFAULT 'pendente', total REAL, criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS itens_pedido (id INTEGER PRIMARY KEY AUTOINCREMENT, pedido_id INTEGER, produto_id INTEGER, quantidade INTEGER, preco_unitario REAL);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], timeout=10, isolation_level=None
        )
        g.db.row_factory = sqlite3.Row
    return g.db


@contextmanager
def transaction():
    connection = get_db()
    connection.execute("BEGIN IMMEDIATE")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise


def init_app(app):
    path = app.config["DATABASE"]
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    with app.app_context():
        get_db().executescript(SCHEMA)
        get_db().close()

    @app.teardown_appcontext
    def close_db(error=None):
        connection = g.pop("db", None)
        if connection is not None:
            connection.close()
