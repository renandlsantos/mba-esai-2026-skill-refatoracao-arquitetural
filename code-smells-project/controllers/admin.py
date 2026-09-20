import hmac
from flask import current_app
from database import get_db, transaction
from errors import DomainError

PUBLIC_QUERIES = {
    "SELECT 1 AS value": "SELECT 1 AS value",
    "SELECT COUNT(*) AS total FROM produtos": "SELECT COUNT(*) AS total FROM produtos",
    "SELECT COUNT(*) AS total FROM pedidos": "SELECT COUNT(*) AS total FROM pedidos",
}


def authorize(authorization):
    expected = current_app.config["ADMIN_TOKEN"]
    supplied = (
        authorization.removeprefix("Bearer ") if isinstance(authorization, str) else ""
    )
    if not expected or not hmac.compare_digest(supplied.encode(), expected.encode()):
        raise DomainError("Acesso administrativo negado", 403)


def reset():
    if not current_app.config["ALLOW_RESET"]:
        raise DomainError("Reset desabilitado", 403)
    with transaction() as db:
        for table in ("itens_pedido", "pedidos", "produtos", "usuarios"):
            db.execute(f"DELETE FROM {table}")


def query(body):
    if (
        not isinstance(body, dict)
        or not isinstance(body.get("sql"), str)
        or body["sql"] not in PUBLIC_QUERIES
    ):
        raise DomainError("Consulta não permitida", 403)
    return [dict(row) for row in get_db().execute(PUBLIC_QUERIES[body["sql"]])]


def health():
    db = get_db()
    counts = {
        name: db.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        for name in ("produtos", "usuarios", "pedidos")
    }
    return {
        "status": "ok",
        "database": "connected",
        "counts": counts,
        "versao": "1.0.0",
    }
