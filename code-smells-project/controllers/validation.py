import math
import re
from errors import DomainError

CATEGORIES = ("informatica", "moveis", "vestuario", "geral", "eletronicos", "livros")
STATUSES = ("pendente", "aprovado", "enviado", "entregue", "cancelado")


def object_body(value):
    if not isinstance(value, dict):
        raise DomainError("Dados inválidos: objeto JSON esperado")
    return value


def text(value, name, minimum=1, maximum=200):
    if not isinstance(value, str) or not minimum <= len(value.strip()) <= maximum:
        raise DomainError(f"{name} inválido")
    return value.strip()


def integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise DomainError(f"{name} inválido")
    return value


def number(value, name):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise DomainError(f"{name} inválido")
    return value


def product(body):
    body = object_body(body)
    category = body.get("categoria", "geral")
    if category not in CATEGORIES:
        raise DomainError("Categoria inválida")
    description = body.get("descricao", "")
    if not isinstance(description, str):
        raise DomainError("Descrição inválida")
    return (
        text(body.get("nome"), "Nome", 2),
        description,
        number(body.get("preco"), "Preço"),
        integer(body.get("estoque"), "Estoque"),
        category,
    )


def email(value):
    value = text(value, "Email", maximum=254)
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
        raise DomainError("Email inválido")
    return value.lower()
