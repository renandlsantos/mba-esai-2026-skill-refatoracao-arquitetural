from collections import defaultdict
from controllers import validation as validate
from models import products, users, orders
from errors import DomainError


class ShopController:
    def list_products(self):
        return products.list_products()

    def get_product(self, product_id):
        return products.get_product(product_id)

    def delete_product(self, product_id):
        products.delete_product(product_id)

    def list_users(self):
        return users.list_users()

    def get_user(self, user_id):
        return users.get_user(user_id)

    def list_orders(self, user_id=None):
        return orders.list_orders(user_id)

    def sales_report(self):
        return orders.sales_report()

    def create_product(self, body):
        return products.create_product(validate.product(body))

    def update_product(self, product_id, body):
        products.update_product(product_id, validate.product(body))

    def search_products(self, args):
        filters = dict(args)
        for key in ("preco_min", "preco_max"):
            if key in filters:
                try:
                    filters[key] = validate.number(float(filters[key]), key)
                except (ValueError, TypeError):
                    raise DomainError("Preço inválido")
        return products.list_products(filters)

    def create_user(self, body):
        body = validate.object_body(body)
        return users.create_user(
            validate.text(body.get("nome"), "Nome"),
            validate.email(body.get("email")),
            validate.text(body.get("senha"), "Senha", maximum=1024),
        )

    def login(self, body):
        body = validate.object_body(body)
        # Credentials are bound as data; arbitrary nonempty input must not become SQL.
        return users.authenticate(
            validate.text(body.get("email"), "Email", maximum=254).lower(),
            validate.text(body.get("senha"), "Senha", maximum=1024),
        )

    def create_order(self, body):
        body = validate.object_body(body)
        user_id = validate.integer(body.get("usuario_id"), "Usuário", 1)
        items = body.get("itens")
        if not isinstance(items, list) or not items:
            raise DomainError("Pedido deve ter pelo menos um item")
        quantities = defaultdict(int)
        for item in items:
            item = validate.object_body(item)
            quantities[validate.integer(item.get("produto_id"), "Produto", 1)] += (
                validate.integer(item.get("quantidade"), "Quantidade", 1)
            )
        return orders.create_order(user_id, quantities)

    def update_status(self, order_id, body):
        status = validate.object_body(body).get("status")
        if status not in validate.STATUSES:
            raise DomainError("Status inválido")
        orders.update_status(order_id, status)
