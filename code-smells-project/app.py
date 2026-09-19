import os
from flask import Flask
from config import settings
from database import init_app
from errors import register_errors
from views.routes import create_routes


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(settings())
    app.config.update(config or {})
    init_app(app)
    app.register_blueprint(create_routes())
    register_errors(app)
    return app


if __name__ == "__main__":
    create_app().run(
        host="127.0.0.1",
        port=int(os.getenv("PORT", "5000")),
        debug=False,
        load_dotenv=False,
    )
