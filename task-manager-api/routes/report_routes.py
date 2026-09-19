from flask import Blueprint, request


def create_routes(controller):
    routes = Blueprint("reports", __name__)
    routes.add_url_rule(
        "/reports/summary", "summary", controller.summary, methods=["GET"]
    )
    routes.add_url_rule(
        "/reports/user/<int:user_id>", "user", controller.user_report, methods=["GET"]
    )
    routes.add_url_rule(
        "/categories", "categories", controller.categories, methods=["GET"]
    )
    routes.add_url_rule(
        "/categories",
        "create_category",
        lambda: (controller.save_category(request.get_json()), 201),
        methods=["POST"],
    )
    routes.add_url_rule(
        "/categories/<int:category_id>",
        "update_category",
        lambda category_id: controller.save_category(request.get_json(), category_id),
        methods=["PUT"],
    )
    routes.add_url_rule(
        "/categories/<int:category_id>",
        "delete_category",
        controller.delete_category,
        methods=["DELETE"],
    )
    return routes
