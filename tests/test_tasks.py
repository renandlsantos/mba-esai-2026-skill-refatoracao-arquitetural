import atexit, os
import json, sys, tempfile, unittest, warnings
from pathlib import Path

root = Path(__file__).resolve().parents[1]
target = root / "task-manager-api"
if "def create_app(" not in (target / "app.py").read_text():
    raise RuntimeError(
        "Baseline lacks factory; do not import its boot-time database mutation"
    )
sys.path.insert(0, str(target))
from app import create_app
from database import db
from sqlalchemy import event
from sqlalchemy.exc import LegacyAPIWarning

warnings.simplefilter("error", LegacyAPIWarning)
warnings.simplefilter("error", DeprecationWarning)

COVERED = []


@atexit.register
def save_coverage():
    if os.getenv("COVERAGE_OUTPUT"):
        Path(os.environ["COVERAGE_OUTPUT"]).write_text(
            json.dumps(COVERED, indent=2) + "\n"
        )


class TaskTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite:///"
                + str(Path(self.tmp.name) / "test.db"),
                "SECRET_KEY": "test-signing-key",
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.engine.dispose()
        self.tmp.cleanup()

    def call(self, method, path, body=None, status=200):
        result = self.client.open(path, method=method, json=body)
        COVERED.append({"method": method, "path": path, "status": result.status_code})
        self.assertEqual(result.status_code, status, (path, result.get_json()))
        return result.get_json()

    def user(self, email="user@example.test"):
        return self.call(
            "POST",
            "/users",
            {"name": "Synthetic", "email": email, "password": "test-only"},
            201,
        )["id"]

    def category(self):
        return self.call(
            "POST", "/categories", {"name": "Synthetic", "color": "#123456"}, 201
        )["id"]

    def test_all_routes(self):
        self.call("GET", "/")
        self.call("GET", "/health")
        uid = self.user()
        cid = self.category()
        self.call("GET", "/users")
        self.call("GET", f"/users/{uid}")
        self.call("PUT", f"/users/{uid}", {"name": "Updated"})
        self.call(
            "POST", "/login", {"email": "user@example.test", "password": "test-only"}
        )
        self.call("GET", "/categories")
        self.call("PUT", f"/categories/{cid}", {"color": "#abcdef"})
        tid = self.call(
            "POST",
            "/tasks",
            {
                "title": "Synthetic task",
                "user_id": uid,
                "category_id": cid,
                "due_date": "2000-01-01",
                "tags": ["one", "two"],
            },
            201,
        )["id"]
        tasks = self.call("GET", "/tasks")
        self.assertTrue(tasks[0]["overdue"])
        self.assertEqual(tasks[0]["user_name"], "Updated")
        self.call("GET", f"/tasks/{tid}")
        self.call("PUT", f"/tasks/{tid}", {"status": "done"})
        self.call("GET", "/tasks/search?q=Synthetic&priority=3")
        stats = self.call("GET", "/tasks/stats")
        self.assertEqual(stats["done"], 1)
        self.call("GET", f"/users/{uid}/tasks")
        summary = self.call("GET", "/reports/summary")
        self.assertEqual(summary["overview"]["total_tasks"], 1)
        self.call("GET", f"/reports/user/{uid}")
        self.call("DELETE", f"/tasks/{tid}")
        self.call("DELETE", f"/categories/{cid}")
        self.call("DELETE", f"/users/{uid}")

    def test_credentials_tokens_and_duplicate_email(self):
        uid = self.user()
        self.call(
            "POST",
            "/users",
            {"name": "Other", "email": "user@example.test", "password": "test-only"},
            409,
        )
        login = self.call(
            "POST", "/login", {"email": "user@example.test", "password": "test-only"}
        )
        for data in [
            login,
            self.call("GET", "/users"),
            self.call("GET", f"/users/{uid}"),
        ]:
            self.assertNotIn("password", json.dumps(data))
            self.assertNotIn("scrypt:", json.dumps(data))
        from services.tokens import verify_token

        with self.app.app_context():
            self.assertEqual(verify_token(login["token"]), uid)
            self.assertIsNone(verify_token(login["token"] + "tampered"))
            self.assertIsNone(verify_token(login["token"], max_age=-1))
        self.call(
            "POST", "/login", {"email": "user@example.test", "password": "wrong"}, 401
        )
        self.call("PUT", f"/users/{uid}", {"active": False})
        self.call(
            "POST",
            "/login",
            {"email": "user@example.test", "password": "test-only"},
            403,
        )

    def test_validation_and_atomic_update(self):
        uid = self.user()
        tid = self.call("POST", "/tasks", {"title": "Original"}, 201)["id"]
        for body in [
            [],
            {"title": "task", "priority": True},
            {"title": "task", "priority": "x"},
            {"title": "task", "tags": [2]},
            {"title": "task", "due_date": "2026-99-01"},
        ]:
            self.call("POST", "/tasks", body, 400)
        self.call("POST", "/tasks", {"title": "task", "user_id": 999}, 404)
        self.call("PUT", f"/tasks/{tid}", {"title": "Changed", "priority": 99}, 400)
        self.assertEqual(self.call("GET", f"/tasks/{tid}")["title"], "Original")
        self.call("PUT", f"/users/{uid}", {"name": "Changed", "active": "yes"}, 400)
        self.assertEqual(self.call("GET", f"/users/{uid}")["name"], "Synthetic")
        self.call("POST", "/categories", {"name": "test", "color": "#zzzzzz"}, 400)
        self.call("GET", "/tasks/search?priority=x", status=400)
        self.call("GET", "/not-found", status=404)
        self.call("PATCH", "/tasks", {}, 405)
        response = self.client.post(
            "/tasks", data="{broken", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_explicit_seed_legacy_migration_and_disabled_notifications(self):
        import hashlib
        from models import User
        from seed import seed_data
        from services.notification_service import NotificationService
        from unittest.mock import patch

        with patch("smtplib.SMTP") as smtp:
            self.assertFalse(
                NotificationService().send_email(
                    "synthetic@example.test", "test", "body"
                )
            )
            smtp.assert_not_called()
        seed_data(self.app, "test-only")
        self.assertEqual(len(self.call("GET", "/tasks")), 1)
        with self.app.app_context():
            user = User(
                name="Legacy",
                email="legacy@example.test",
                password=hashlib.md5(
                    b"synthetic-old", usedforsecurity=False
                ).hexdigest(),
            )
            db.session.add(user)
            db.session.commit()
            self.assertFalse(user.check_password("synthetic-old"))
            self.app.config["ALLOW_LEGACY_PASSWORDS"] = True
            self.assertTrue(user.check_password("synthetic-old"))
            db.session.commit()
            self.assertTrue(user.password.startswith("scrypt:"))

    def test_n_plus_one_and_seed_guard_and_deletion(self):
        cid = self.category()
        for i in range(5):
            uid = self.user(f"user{i}@example.test")
            self.call(
                "POST",
                "/tasks",
                {"title": f"Task {i}", "user_id": uid, "category_id": cid},
                201,
            )
        with self.app.app_context():
            queries = []

            def counter(*args):
                queries.append(args[2])

            event.listen(db.engine, "before_cursor_execute", counter)
            self.call("GET", "/tasks")
            self.assertLessEqual(len(queries), 1)
            queries.clear()
            self.call("GET", "/users")
            self.assertLessEqual(len(queries), 2)
            queries.clear()
            self.call("GET", "/reports/summary")
            self.assertLessEqual(len(queries), 3)
            event.remove(db.engine, "before_cursor_execute", counter)
            from seed import seed_data

            with self.assertRaises(ValueError):
                seed_data(self.app, "test-only")
        self.call("DELETE", f"/categories/{cid}")
        self.assertTrue(
            all(x["category_id"] is None for x in self.call("GET", "/tasks"))
        )
        self.call("DELETE", f"/users/{uid}")
        self.assertEqual(len(self.call("GET", "/tasks")), 4)


if __name__ == "__main__":
    unittest.main()
