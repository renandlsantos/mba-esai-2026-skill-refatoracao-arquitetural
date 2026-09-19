import atexit, os
import json, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code-smells-project"))
from app import create_app
from database import get_db

COVERED = []


@atexit.register
def save_coverage():
    if os.getenv("COVERAGE_OUTPUT"):
        Path(os.environ["COVERAGE_OUTPUT"]).write_text(
            json.dumps(COVERED, indent=2) + "\n"
        )


class ShopTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE": str(Path(self.tmp.name) / "test.db"),
                "ADMIN_TOKEN": "test-admin",
                "ALLOW_RESET": True,
            }
        )
        self.client = self.app.test_client()
        self.admin = {"Authorization": "Bearer test-admin"}

    def tearDown(self):
        self.tmp.cleanup()

    def request(self, method, path, body=None, expected=200, admin=False):
        response = self.client.open(
            path, method=method, json=body, headers=self.admin if admin else {}
        )
        COVERED.append({"method": method, "path": path, "status": response.status_code})
        self.assertEqual(response.status_code, expected, (path, response.get_json()))
        return response.get_json()

    def user(self):
        return self.request(
            "POST",
            "/usuarios",
            {"nome": "Synthetic", "email": "user@example.test", "senha": "test-only"},
            201,
        )["dados"]["id"]

    def product(self, stock=5):
        return self.request(
            "POST",
            "/produtos",
            {"nome": "Produto d'água", "preco": 12.5, "estoque": stock},
            201,
        )["dados"]["id"]

    def test_all_routes_workflow(self):
        self.request("GET", "/")
        self.request("GET", "/health")
        uid = self.user()
        pid = self.product()
        self.request("GET", "/produtos")
        self.request("GET", "/produtos/busca?q=água&preco_min=0")
        self.request("GET", f"/produtos/{pid}")
        self.request(
            "PUT", f"/produtos/{pid}", {"nome": "Updated", "preco": 20, "estoque": 5}
        )
        self.request("GET", "/usuarios")
        self.request("GET", f"/usuarios/{uid}")
        self.request(
            "POST", "/login", {"email": "user@example.test", "senha": "test-only"}
        )
        oid = self.request(
            "POST",
            "/pedidos",
            {"usuario_id": uid, "itens": [{"produto_id": pid, "quantidade": 2}]},
            201,
        )["dados"]["pedido_id"]
        orders = self.request("GET", "/pedidos")["dados"]
        self.assertEqual(orders[0]["total"], 40)
        self.request("GET", f"/pedidos/usuario/{uid}")
        self.request("PUT", f"/pedidos/{oid}/status", {"status": "aprovado"})
        report = self.request("GET", "/relatorios/vendas")["dados"]
        self.assertEqual(report["faturamento_bruto"], 40)
        self.request("DELETE", f"/produtos/{pid}")
        self.request("POST", "/admin/query", {"sql": "SELECT 1 AS value"}, admin=True)
        self.request("POST", "/admin/reset-db", {}, admin=True)
        self.assertEqual(self.request("GET", "/produtos")["dados"], [])

    def test_passwords_and_sql_injection(self):
        uid = self.user()
        self.product()
        for path in ["/usuarios", f"/usuarios/{uid}", "/health"]:
            text = json.dumps(self.request("GET", path))
            self.assertNotIn("senha", text)
            self.assertNotIn("secret_key", text)
            self.assertNotIn("scrypt:", text)
        self.request("POST", "/login", {"email": "' OR 1=1 --", "senha": "wrong"}, 401)
        self.request("GET", "/produtos/busca?q=%27%20OR%201%3D1%20--")
        with self.app.app_context():
            self.assertTrue(
                get_db()
                .execute("SELECT senha FROM usuarios")
                .fetchone()[0]
                .startswith("scrypt:")
            )

    def test_invalid_inputs_and_atomic_order(self):
        uid = self.user()
        pid = self.product(3)
        for body in [
            [],
            {"nome": "ok", "preco": "x", "estoque": 1},
            {"nome": "ok", "preco": float("nan"), "estoque": 1},
            {"nome": "ok", "preco": 1, "estoque": True},
        ]:
            self.request("POST", "/produtos", body, 400)
        self.request(
            "POST",
            "/pedidos",
            {
                "usuario_id": uid,
                "itens": [
                    {"produto_id": pid, "quantidade": 2},
                    {"produto_id": pid, "quantidade": 2},
                ],
            },
            400,
        )
        self.request(
            "POST",
            "/pedidos",
            {"usuario_id": uid, "itens": [{"produto_id": pid, "quantidade": -1}]},
            400,
        )
        self.request(
            "POST",
            "/pedidos",
            {"usuario_id": 999, "itens": [{"produto_id": pid, "quantidade": 1}]},
            404,
        )
        self.assertEqual(self.request("GET", f"/produtos/{pid}")["dados"]["estoque"], 3)
        self.assertEqual(self.request("GET", "/pedidos")["dados"], [])
        with self.app.app_context():
            get_db().execute(
                "CREATE TRIGGER fail_item BEFORE INSERT ON itens_pedido BEGIN SELECT RAISE(ABORT, 'simulated'); END"
            )
        self.request(
            "POST",
            "/pedidos",
            {"usuario_id": uid, "itens": [{"produto_id": pid, "quantidade": 1}]},
            500,
        )
        self.assertEqual(self.request("GET", f"/produtos/{pid}")["dados"]["estoque"], 3)
        self.assertEqual(self.request("GET", "/pedidos")["dados"], [])

    def test_discount_boundaries_and_explicit_legacy_migration(self):
        from models.orders import sales_report
        from models.users import authenticate

        with self.app.app_context():
            db = get_db()
            for total, expected in [
                (1000, 0),
                (5000, 100),
                (10000, 500),
                (10000.01, 1000),
            ]:
                db.execute("DELETE FROM pedidos")
                db.execute(
                    "INSERT INTO pedidos(total,status) VALUES (?,'pendente')", (total,)
                )
                self.assertEqual(sales_report()["desconto_aplicavel"], expected)
            db.execute(
                "INSERT INTO usuarios(nome,email,senha,tipo) VALUES ('Legacy','legacy@example.test','synthetic-old','cliente')"
            )
            from errors import DomainError

            with self.assertRaises(DomainError):
                authenticate("legacy@example.test", "synthetic-old")
            self.app.config["ALLOW_LEGACY_PASSWORDS"] = True
            authenticate("legacy@example.test", "synthetic-old")
            self.assertTrue(
                db.execute(
                    "SELECT senha FROM usuarios WHERE email='legacy@example.test'"
                )
                .fetchone()[0]
                .startswith("scrypt:")
            )
        other_path = str(Path(self.tmp.name) / "other.db")
        other = create_app({"TESTING": True, "DATABASE": other_path})
        self.assertEqual(other.test_client().get("/usuarios").get_json()["dados"], [])

    def test_admin_guards_errors_and_bounded_queries(self):
        uid = self.user()
        pid = self.product(10)
        for _ in range(4):
            self.request(
                "POST",
                "/pedidos",
                {"usuario_id": uid, "itens": [{"produto_id": pid, "quantidade": 1}]},
                201,
            )
        from models.orders import list_orders

        with self.app.app_context():
            queries = []
            get_db().set_trace_callback(queries.append)
            self.assertEqual(len(list_orders()), 4)
            self.assertLessEqual(sum(q.startswith("SELECT") for q in queries), 2)
        self.request("POST", "/admin/reset-db", {}, 403)
        self.request(
            "POST", "/admin/query", {"sql": "SELECT senha FROM usuarios"}, 403, True
        )
        self.request("GET", "/missing", expected=404)
        self.request("PATCH", "/produtos", {}, 405)
        response = self.client.post(
            "/produtos", data="{bad", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.request("PUT", "/pedidos/999/status", {"status": "aprovado"}, 404)


if __name__ == "__main__":
    unittest.main()
