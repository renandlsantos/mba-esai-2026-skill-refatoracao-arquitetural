import re
from datetime import datetime
from errors import DomainError
from models import User, Category
from utils.constants import (
    VALID_STATUSES,
    VALID_ROLES,
    MIN_TITLE_LENGTH,
    MAX_TITLE_LENGTH,
    MIN_PASSWORD_LENGTH,
    DEFAULT_COLOR,
    DEFAULT_PRIORITY,
)


def object_body(body):
    if not isinstance(body, dict) or not body:
        raise DomainError("Objeto JSON não vazio esperado")
    return body


def text(value, name, minimum=1, maximum=200):
    if not isinstance(value, str) or not minimum <= len(value.strip()) <= maximum:
        raise DomainError(f"{name} inválido")
    return value.strip()


def integer(value, name, minimum=1, maximum=None):
    if (
        type(value) is not int
        or value < minimum
        or (maximum is not None and value > maximum)
    ):
        raise DomainError(f"{name} inválido")
    return value


def email(value):
    value = text(value, "Email", maximum=150).lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
        raise DomainError("Email inválido")
    return value


def task_values(body, store, creating=False):
    body = object_body(body)
    values = {}
    if creating or "title" in body:
        values["title"] = text(
            body.get("title"), "Título", MIN_TITLE_LENGTH, MAX_TITLE_LENGTH
        )
    if "description" in body:
        if body["description"] is not None and not isinstance(body["description"], str):
            raise DomainError("Descrição inválida")
        values["description"] = body["description"]
    elif creating:
        values["description"] = ""
    if creating or "status" in body:
        status = body.get("status", "pending")
        if status not in VALID_STATUSES:
            raise DomainError("Status inválido")
        values["status"] = status
    if creating or "priority" in body:
        values["priority"] = integer(
            body.get("priority", DEFAULT_PRIORITY), "Prioridade", 1, 5
        )
    for key, model in (("user_id", User), ("category_id", Category)):
        if key in body:
            value = body[key]
            if value is not None:
                store.get(model, integer(value, key))
            values[key] = value
    if "due_date" in body:
        value = body["due_date"]
        if value is None or value == "":
            values["due_date"] = None
        else:
            if not isinstance(value, str) or not re.fullmatch(
                r"\d{4}-\d{2}-\d{2}", value
            ):
                raise DomainError("Data inválida. Use YYYY-MM-DD")
            try:
                values["due_date"] = datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                raise DomainError("Data inválida. Use YYYY-MM-DD")
    if "tags" in body:
        tags = body["tags"]
        if isinstance(tags, list):
            if any(not isinstance(tag, str) or "," in tag for tag in tags):
                raise DomainError("Tags inválidas")
            tags = ",".join(tags)
        if tags is not None and (not isinstance(tags, str) or len(tags) > 500):
            raise DomainError("Tags inválidas")
        values["tags"] = tags
    return values


def user_values(body, creating=False):
    body = object_body(body)
    values = {}
    if creating or "name" in body:
        values["name"] = text(body.get("name"), "Nome", maximum=100)
    if creating or "email" in body:
        values["email"] = email(body.get("email"))
    if creating or "password" in body:
        values["password"] = text(
            body.get("password"), "Senha", MIN_PASSWORD_LENGTH, 1024
        )
    if creating or "role" in body:
        role = body.get("role", "user")
        if role not in VALID_ROLES:
            raise DomainError("Role inválido")
        values["role"] = role
    if "active" in body:
        if type(body["active"]) is not bool:
            raise DomainError("Active inválido")
        values["active"] = body["active"]
    return values


def category_values(body, creating=False):
    body = object_body(body)
    values = {}
    if creating or "name" in body:
        values["name"] = text(body.get("name"), "Nome", maximum=100)
    if creating or "description" in body:
        value = body.get("description", "")
        if not isinstance(value, str) or len(value) > 300:
            raise DomainError("Descrição inválida")
        values["description"] = value
    if creating or "color" in body:
        color = body.get("color", DEFAULT_COLOR)
        if not isinstance(color, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
            raise DomainError("Cor inválida")
        values["color"] = color
    return values
