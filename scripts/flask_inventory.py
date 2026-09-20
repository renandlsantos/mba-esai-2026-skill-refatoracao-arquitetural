import json, sys, tempfile
from pathlib import Path

project = sys.argv[1]
sys.path.insert(0, str(Path.cwd() / project))
from app import create_app

with tempfile.TemporaryDirectory() as directory:
    path = str(Path(directory) / "inventory.db")
    config = (
        {"DATABASE": path}
        if project == "code-smells-project"
        else {"SQLALCHEMY_DATABASE_URI": "sqlite:///" + path}
    )
    app = create_app(config)
    print(
        json.dumps(
            [
                {"method": method, "rule": route.rule}
                for route in app.url_map.iter_rules()
                if route.endpoint != "static"
                for method in route.methods - {"HEAD", "OPTIONS"}
            ]
        )
    )
