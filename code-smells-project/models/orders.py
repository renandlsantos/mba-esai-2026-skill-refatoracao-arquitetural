from database import get_db, transaction
from errors import DomainError

DISCOUNT_TIERS = ((10000, 0.10), (5000, 0.05), (1000, 0.02))


def create_order(user_id, quantities):
    with transaction() as db:
        if not db.execute("SELECT id FROM usuarios WHERE id=?", (user_id,)).fetchone():
            raise DomainError("Usuário não encontrado", 404)
        products = {}
        for product_id, quantity in quantities.items():
            product = db.execute(
                "SELECT * FROM produtos WHERE id=?", (product_id,)
            ).fetchone()
            if product is None:
                raise DomainError("Produto não encontrado", 404)
            if product["estoque"] < quantity:
                raise DomainError("Estoque insuficiente")
            products[product_id] = product
        total = round(
            sum(products[pid]["preco"] * qty for pid, qty in quantities.items()), 2
        )
        order_id = db.execute(
            "INSERT INTO pedidos (usuario_id,status,total) VALUES (?,'pendente',?)",
            (user_id, total),
        ).lastrowid
        for product_id, quantity in quantities.items():
            db.execute(
                "UPDATE produtos SET estoque=estoque-? WHERE id=?",
                (quantity, product_id),
            )
            db.execute(
                "INSERT INTO itens_pedido (pedido_id,produto_id,quantidade,preco_unitario) VALUES (?,?,?,?)",
                (order_id, product_id, quantity, products[product_id]["preco"]),
            )
        return {"pedido_id": order_id, "total": total}


def list_orders(user_id=None):
    where, params = (
        (" WHERE usuario_id=?", (user_id,)) if user_id is not None else ("", ())
    )
    orders = [
        dict(row) for row in get_db().execute("SELECT * FROM pedidos" + where, params)
    ]
    if not orders:
        return []
    mapped = {order["id"]: order for order in orders}
    for order in orders:
        order["itens"] = []
    condition = " WHERE p.usuario_id=?" if user_id is not None else ""
    rows = get_db().execute(
        "SELECT i.*,COALESCE(pr.nome,'Desconhecido') AS produto_nome FROM itens_pedido i JOIN pedidos p ON p.id=i.pedido_id LEFT JOIN produtos pr ON pr.id=i.produto_id"
        + condition,
        params,
    )
    for row in rows:
        mapped[row["pedido_id"]]["itens"].append(
            {
                key: row[key]
                for key in (
                    "produto_id",
                    "produto_nome",
                    "quantidade",
                    "preco_unitario",
                )
            }
        )
    return orders


def update_status(order_id, status):
    cursor = get_db().execute(
        "UPDATE pedidos SET status=? WHERE id=?", (status, order_id)
    )
    if cursor.rowcount == 0:
        raise DomainError("Pedido não encontrado", 404)


def sales_report():
    row = (
        get_db()
        .execute(
            "SELECT COUNT(*) AS total,COALESCE(SUM(total),0) AS revenue,SUM(status='pendente') AS pending,SUM(status='aprovado') AS approved,SUM(status='cancelado') AS cancelled FROM pedidos"
        )
        .fetchone()
    )
    revenue = row["revenue"]
    discount = next(
        (revenue * rate for threshold, rate in DISCOUNT_TIERS if revenue > threshold), 0
    )
    return {
        "total_pedidos": row["total"],
        "faturamento_bruto": round(revenue, 2),
        "desconto_aplicavel": round(discount, 2),
        "faturamento_liquido": round(revenue - discount, 2),
        "pedidos_pendentes": row["pending"] or 0,
        "pedidos_aprovados": row["approved"] or 0,
        "pedidos_cancelados": row["cancelled"] or 0,
        "ticket_medio": round(revenue / row["total"], 2) if row["total"] else 0,
    }
