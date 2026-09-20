from models import User
from controllers.validation import user_values, object_body, text, email
from views.serializers import user_view, task_view
from services.tokens import issue_token
from errors import DomainError


class UserController:
    def __init__(self, store):
        self.store = store

    def list(self):
        return [
            {**user_view(user), "task_count": len(user.tasks)}
            for user in self.store.users(True)
        ]

    def get(self, user_id):
        return {
            **user_view(self.store.get(User, user_id)),
            "tasks": [
                task_view(task) for task in self.store.tasks({"user_id": user_id})
            ],
        }

    def save(self, body, user_id=None):
        values = user_values(body, user_id is None)
        user = self.store.get(User, user_id) if user_id is not None else User()
        if "email" in values:
            existing = self.store.email_user(values["email"])
            if existing and existing.id != user_id:
                raise DomainError("Email já cadastrado", 409)
        for key, value in values.items():
            if key == "password":
                user.set_password(value)
            else:
                setattr(user, key, value)
        return user_view(self.store.save(user))

    def delete(self, user_id):
        self.store.delete_user(self.store.get(User, user_id))
        return {"message": "Usuário deletado com sucesso"}

    def login(self, body):
        body = object_body(body)
        user = self.store.email_user(email(body.get("email")))
        password = text(body.get("password"), "Senha", maximum=1024)
        if not user or not user.check_password(password):
            raise DomainError("Credenciais inválidas", 401)
        if not user.active:
            raise DomainError("Usuário inativo", 403)
        self.store.commit()
        return {
            "message": "Login realizado com sucesso",
            "user": user_view(user),
            "token": issue_token(user.id),
        }
