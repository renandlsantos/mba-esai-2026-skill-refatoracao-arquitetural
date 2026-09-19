import hmac
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, transaction
from errors import DomainError

PUBLIC_COLUMNS = "id,nome,email,tipo,criado_em"


def list_users():
    return [
        dict(row) for row in get_db().execute(f"SELECT {PUBLIC_COLUMNS} FROM usuarios")
    ]


def get_user(user_id):
    row = (
        get_db()
        .execute(f"SELECT {PUBLIC_COLUMNS} FROM usuarios WHERE id=?", (user_id,))
        .fetchone()
    )
    if row is None:
        raise DomainError("Usuário não encontrado", 404)
    return dict(row)


def create_user(name, email, password):
    password_hash = generate_password_hash(password)
    with transaction() as db:
        if db.execute("SELECT id FROM usuarios WHERE email=?", (email,)).fetchone():
            raise DomainError("Email já cadastrado", 409)
        return db.execute(
            "INSERT INTO usuarios (nome,email,senha,tipo) VALUES (?,?,?,'cliente')",
            (name, email, password_hash),
        ).lastrowid


def authenticate(email, password):
    row = get_db().execute("SELECT * FROM usuarios WHERE email=?", (email,)).fetchone()
    if not row:
        raise DomainError("Email ou senha inválidos", 401)
    stored = row["senha"] or ""
    modern = stored.startswith(("scrypt:", "pbkdf2:"))
    valid = check_password_hash(stored, password) if modern else False
    if not modern and current_app.config["ALLOW_LEGACY_PASSWORDS"]:
        valid = hmac.compare_digest(stored.encode(), password.encode())
        if valid:
            get_db().execute(
                "UPDATE usuarios SET senha=? WHERE id=?",
                (generate_password_hash(password), row["id"]),
            )
    if not valid:
        raise DomainError("Email ou senha inválidos", 401)
    return {key: row[key] for key in ("id", "nome", "email", "tipo")}
