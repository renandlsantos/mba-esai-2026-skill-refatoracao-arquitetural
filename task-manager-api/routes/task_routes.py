from flask import Blueprint, request


def create_routes(controller, reports):
    routes = Blueprint("tasks", __name__)
    routes.add_url_rule("/tasks", "list", lambda: controller.list(), methods=["GET"])
    routes.add_url_rule("/tasks/<int:task_id>", "get", controller.get, methods=["GET"])
    routes.add_url_rule(
        "/tasks",
        "create",
        lambda: (controller.create(request.get_json()), 201),
        methods=["POST"],
    )
    routes.add_url_rule(
        "/tasks/<int:task_id>",
        "update",
        lambda task_id: controller.update(task_id, request.get_json()),
        methods=["PUT"],
    )
    routes.add_url_rule(
        "/tasks/<int:task_id>", "delete", controller.delete, methods=["DELETE"]
    )
    routes.add_url_rule(
        "/tasks/search",
        "search",
        lambda: controller.search(request.args),
        methods=["GET"],
    )
    routes.add_url_rule("/tasks/stats", "stats", reports.stats, methods=["GET"])
    return routes
