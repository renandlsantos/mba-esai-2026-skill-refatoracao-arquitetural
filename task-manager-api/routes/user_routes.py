from flask import Blueprint, request


def create_routes(controller, tasks):
    routes = Blueprint("users", __name__)
    routes.add_url_rule("/users", "list", controller.list, methods=["GET"])
    routes.add_url_rule("/users/<int:user_id>", "get", controller.get, methods=["GET"])
    routes.add_url_rule(
        "/users",
        "create",
        lambda: (controller.save(request.get_json()), 201),
        methods=["POST"],
    )
    routes.add_url_rule(
        "/users/<int:user_id>",
        "update",
        lambda user_id: controller.save(request.get_json(), user_id),
        methods=["PUT"],
    )
    routes.add_url_rule(
        "/users/<int:user_id>", "delete", controller.delete, methods=["DELETE"]
    )
    routes.add_url_rule(
        "/users/<int:user_id>/tasks", "tasks", tasks.user_tasks, methods=["GET"]
    )
    routes.add_url_rule(
        "/login",
        "login",
        lambda: controller.login(request.get_json()),
        methods=["POST"],
    )
    return routes
