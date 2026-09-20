import os
from pathlib import Path
from flask import Flask
from database import db
from config import settings
from errors import register_errors
from repositories.store import Store
from controllers.tasks import TaskController
from controllers.users import UserController
from controllers.reports import ReportController
from routes import task_routes, user_routes, report_routes
from utils.clock import utc_now


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(settings())
    app.config.update(config or {})
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    store = Store()
    tasks = TaskController(store)
    users = UserController(store)
    reports = ReportController(store)
    app.register_blueprint(task_routes.create_routes(tasks, reports))
    app.register_blueprint(user_routes.create_routes(users, tasks))
    app.register_blueprint(report_routes.create_routes(reports))
    app.add_url_rule(
        "/health", "health", lambda: {"status": "ok", "timestamp": str(utc_now())}
    )
    app.add_url_rule(
        "/", "index", lambda: {"message": "Task Manager API", "version": "1.0"}
    )
    register_errors(app)
    return app


if __name__ == "__main__":
    create_app().run(
        host="127.0.0.1",
        port=int(os.getenv("PORT", "5000")),
        debug=False,
        load_dotenv=False,
    )
