"""Characterize untouched Flask fixtures in an isolated copied directory."""

import contextlib, io, json, os, sys
from pathlib import Path

project, target, output = sys.argv[1:]
os.chdir(target)
sys.path.insert(0, target)
with contextlib.redirect_stdout(io.StringIO()):
    from app import app

    if project == "shop":
        from database import get_db

        get_db()
client = app.test_client()
rows = []


def call(method, path, payload=None):
    with contextlib.redirect_stdout(io.StringIO()):
        response = client.open(path, method=method, json=payload)
    rows.append({"method": method, "path": path, "status": response.status_code})
    return response


if project == "shop":
    call("GET", "/")
    health = call("GET", "/health").get_json()
    call("GET", "/produtos")
    call("GET", "/produtos/busca?q=Mouse")
    product = call(
        "POST", "/produtos", {"nome": "Teste", "preco": 10, "estoque": 5}
    ).get_json()["dados"]["id"]
    call("GET", f"/produtos/{product}")
    call(
        "PUT",
        f"/produtos/{product}",
        {"nome": "Teste atualizado", "preco": 12, "estoque": 5},
    )
    user = call(
        "POST",
        "/usuarios",
        {"nome": "Synthetic", "email": "synthetic@example.test", "senha": "test-only"},
    ).get_json()["dados"]["id"]
    call("GET", "/usuarios")
    user_data = call("GET", f"/usuarios/{user}").get_json()
    call("POST", "/login", {"email": "synthetic@example.test", "senha": "test-only"})
    order = call(
        "POST",
        "/pedidos",
        {"usuario_id": user, "itens": [{"produto_id": product, "quantidade": 1}]},
    ).get_json()["dados"]["pedido_id"]
    call("GET", "/pedidos")
    call("GET", f"/pedidos/usuario/{user}")
    call("PUT", f"/pedidos/{order}/status", {"status": "aprovado"})
    call("GET", "/relatorios/vendas")
    call("DELETE", f"/produtos/{product}")
    call("POST", "/admin/query", {"sql": "SELECT 1 AS value"})
    unsafe = call("POST", "/login", {"email": "' OR 1=1 --", "senha": "invalid"})
    defects = {
        "password_exposed": "senha" in user_data["dados"],
        "secret_exposed": "secret_key" in health,
        "injection_login_status": unsafe.status_code,
    }
    call("POST", "/admin/reset-db", {})
else:
    call("GET", "/")
    call("GET", "/health")
    user = call(
        "POST",
        "/users",
        {
            "name": "Synthetic",
            "email": "synthetic@example.test",
            "password": "test-only",
        },
    ).get_json()
    uid = user["id"]
    call("GET", "/users")
    call("GET", f"/users/{uid}")
    call("PUT", f"/users/{uid}", {"name": "Updated"})
    login = call(
        "POST", "/login", {"email": "synthetic@example.test", "password": "test-only"}
    ).get_json()
    category = call(
        "POST", "/categories", {"name": "Synthetic", "color": "#123456"}
    ).get_json()["id"]
    call("GET", "/categories")
    call("PUT", f"/categories/{category}", {"name": "Updated"})
    task = call(
        "POST",
        "/tasks",
        {"title": "Synthetic task", "user_id": uid, "category_id": category},
    ).get_json()["id"]
    call("GET", "/tasks")
    call("GET", f"/tasks/{task}")
    call("PUT", f"/tasks/{task}", {"status": "done"})
    for path in [
        "/tasks/search?q=Synthetic",
        "/tasks/stats",
        f"/users/{uid}/tasks",
        "/reports/summary",
        f"/reports/user/{uid}",
    ]:
        call("GET", path)
    call("DELETE", f"/tasks/{task}")
    call("DELETE", f"/categories/{category}")
    call("DELETE", f"/users/{uid}")
    defects = {
        "password_hash_exposed": "password" in user,
        "fake_token": login.get("token", "").startswith("fake-"),
    }
routes = sorted(
    [
        {"method": m, "rule": r.rule}
        for r in app.url_map.iter_rules()
        if r.endpoint != "static"
        for m in r.methods - {"HEAD", "OPTIONS"}
    ],
    key=lambda x: (x["rule"], x["method"]),
)
Path(output).write_text(
    json.dumps(
        {
            "project": project,
            "routes": routes,
            "checks": rows,
            "observed_defects": defects,
            "isolation": "copied baseline, synthetic data; no externally bound server",
        },
        indent=2,
    )
    + "\n"
)
print(project, len(rows), "checks", len(routes), "routes", defects)
