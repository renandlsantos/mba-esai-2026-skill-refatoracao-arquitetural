import os
from pathlib import Path


def settings():
    return {
        "DATABASE": os.getenv(
            "DATABASE_PATH", str(Path(__file__).parent / "instance" / "loja.db")
        ),
        "ADMIN_TOKEN": os.getenv("ADMIN_TOKEN", ""),
        "ALLOW_RESET": os.getenv("ALLOW_RESET", "false").lower() == "true",
        "ALLOW_LEGACY_PASSWORDS": os.getenv("ALLOW_LEGACY_PASSWORDS", "false").lower()
        == "true",
    }
