from database import get_db
from errors import DomainError


def get_product(product_id):
    row = (
        get_db()
        .execute("SELECT * FROM produtos WHERE id = ?", (product_id,))
        .fetchone()
    )
    if row is None:
        raise DomainError("Produto não encontrado", 404)
    return dict(row)


def list_products(filters=None):
    filters = filters or {}
    query, params = "SELECT * FROM produtos WHERE 1=1", []
    if filters.get("q"):
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        params += ["%" + filters["q"] + "%"] * 2
    if filters.get("categoria"):
        query += " AND categoria = ?"
        params.append(filters["categoria"])
    for key, operator in [("preco_min", ">="), ("preco_max", "<=")]:
        if key in filters:
            query += f" AND preco {operator} ?"
            params.append(filters[key])
    return [dict(row) for row in get_db().execute(query, params).fetchall()]


def create_product(values):
    return (
        get_db()
        .execute(
            "INSERT INTO produtos (nome,descricao,preco,estoque,categoria) VALUES (?,?,?,?,?)",
            values,
        )
        .lastrowid
    )


def update_product(product_id, values):
    get_product(product_id)
    get_db().execute(
        "UPDATE produtos SET nome=?,descricao=?,preco=?,estoque=?,categoria=? WHERE id=?",
        (*values, product_id),
    )


def delete_product(product_id):
    get_product(product_id)
    get_db().execute("DELETE FROM produtos WHERE id=?", (product_id,))
