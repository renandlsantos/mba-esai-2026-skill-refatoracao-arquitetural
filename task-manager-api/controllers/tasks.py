from models import Task, User
from controllers.validation import task_values, integer
from views.serializers import task_view
from utils.constants import VALID_STATUSES
from errors import DomainError


class TaskController:
    def __init__(self, store):
        self.store = store

    def list(self):
        return [
            task_view(task, related=True, overdue=True)
            for task in self.store.tasks(related=True)
        ]

    def get(self, task_id):
        return task_view(self.store.get(Task, task_id), overdue=True)

    def create(self, body):
        return task_view(self.store.save(Task(**task_values(body, self.store, True))))

    def update(self, task_id, body):
        task = self.store.get(Task, task_id)
        values = task_values(body, self.store)
        for key, value in values.items():
            setattr(task, key, value)
        return task_view(self.store.save(task))

    def delete(self, task_id):
        self.store.delete_task(self.store.get(Task, task_id))
        return {"message": "Task deletada com sucesso"}

    def search(self, args):
        filters = dict(args)
        if "status" in filters and filters["status"] not in VALID_STATUSES:
            raise DomainError("Status inválido")
        for key in ("priority", "user_id"):
            if key in filters:
                try:
                    value = int(filters[key])
                except (ValueError, TypeError):
                    raise DomainError(f"{key} inválido")
                filters[key] = integer(value, key, 1, 5 if key == "priority" else None)
        return [task_view(task) for task in self.store.tasks(filters)]

    def user_tasks(self, user_id):
        self.store.get(User, user_id)
        keys = (
            "id",
            "title",
            "description",
            "status",
            "priority",
            "created_at",
            "due_date",
            "overdue",
        )
        return [
            {
                key: value
                for key, value in task_view(task, overdue=True).items()
                if key in keys
            }
            for task in self.store.tasks({"user_id": user_id})
        ]
