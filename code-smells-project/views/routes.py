from flask import Blueprint, request, jsonify
from controllers.shop import ShopController
from controllers import admin


def create_routes(controller=None):
    controller = controller or ShopController()
    routes = Blueprint("shop", __name__)

    def ok(data=None, message=None, status=200):
        body = {"sucesso": True}
        if data is not None:
            body["dados"] = data
        if message:
            body["mensagem"] = message
        return jsonify(body), status

    @routes.get("/")
    def index():
        return jsonify(
            mensagem="Bem-vindo à API da Loja",
            versao="1.0.0",
            endpoints={
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        )

    @routes.get("/health")
    def health():
        return jsonify(admin.health())

    @routes.get("/produtos")
    def list_products():
        return ok(controller.list_products())

    @routes.get("/produtos/busca")
    def search_products():
        result = controller.search_products(request.args)
        return jsonify(dados=result, total=len(result), sucesso=True)

    @routes.get("/produtos/<int:product_id>")
    def get_product(product_id):
        return ok(controller.get_product(product_id))

    @routes.post("/produtos")
    def create_product():
        return ok(
            {"id": controller.create_product(request.get_json())}, "Produto criado", 201
        )

    @routes.put("/produtos/<int:product_id>")
    def update_product(product_id):
        controller.update_product(product_id, request.get_json())
        return ok(message="Produto atualizado")

    @routes.delete("/produtos/<int:product_id>")
    def delete_product(product_id):
        controller.delete_product(product_id)
        return ok(message="Produto deletado")

    @routes.get("/usuarios")
    def list_users():
        return ok(controller.list_users())

    @routes.get("/usuarios/<int:user_id>")
    def get_user(user_id):
        return ok(controller.get_user(user_id))

    @routes.post("/usuarios")
    def create_user():
        return ok({"id": controller.create_user(request.get_json())}, status=201)

    @routes.post("/login")
    def login():
        return ok(controller.login(request.get_json()), "Login OK")

    @routes.post("/pedidos")
    def create_order():
        return ok(
            controller.create_order(request.get_json()),
            "Pedido criado com sucesso",
            201,
        )

    @routes.get("/pedidos")
    def list_orders():
        return ok(controller.list_orders())

    @routes.get("/pedidos/usuario/<int:user_id>")
    def user_orders(user_id):
        return ok(controller.list_orders(user_id))

    @routes.put("/pedidos/<int:order_id>/status")
    def update_status(order_id):
        controller.update_status(order_id, request.get_json())
        return ok(message="Status atualizado")

    @routes.get("/relatorios/vendas")
    def sales_report():
        return ok(controller.sales_report())

    @routes.post("/admin/query")
    def query():
        admin.authorize(request.headers.get("Authorization"))
        return ok(admin.query(request.get_json()))

    @routes.post("/admin/reset-db")
    def reset():
        admin.authorize(request.headers.get("Authorization"))
        admin.reset()
        return ok(message="Banco de dados resetado")

    return routes
