import os
import secrets
from pathlib import Path


def settings():
    path = Path(__file__).parent / "instance" / "tasks.db"
    return {
        "SQLALCHEMY_DATABASE_URI": os.getenv("DATABASE_URL", "sqlite:///" + str(path)),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": os.getenv("SECRET_KEY") or secrets.token_hex(32),
        "ALLOW_LEGACY_PASSWORDS": os.getenv("ALLOW_LEGACY_PASSWORDS", "false").lower()
        == "true",
    }
