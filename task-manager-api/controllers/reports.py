from collections import Counter, defaultdict
from datetime import timedelta
from models import User, Category
from views.serializers import category_view
from controllers.validation import category_values
from utils.clock import utc_now
from utils.constants import VALID_STATUSES


def statistics(tasks):
    statuses = Counter(task.status for task in tasks)
    total = len(tasks)
    done = statuses["done"]
    return {
        "total": total,
        **{key: statuses[key] for key in VALID_STATUSES},
        "overdue": sum(task.is_overdue() for task in tasks),
        "completion_rate": round(done / total * 100, 2) if total else 0,
    }


class ReportController:
    def __init__(self, store):
        self.store = store

    def stats(self):
        return statistics(self.store.tasks())

    def summary(self):
        tasks = self.store.tasks()
        users = self.store.users()
        categories = self.store.categories()
        now = utc_now()
        recent = now - timedelta(days=7)
        status = Counter(task.status for task in tasks)
        priority = Counter(task.priority for task in tasks)
        by_user = defaultdict(list)
        for task in tasks:
            by_user[task.user_id].append(task)
        overdue = [task for task in tasks if task.is_overdue(now)]
        productivity = []
        for user in users:
            user_tasks = by_user[user.id]
            done = sum(task.status == "done" for task in user_tasks)
            total = len(user_tasks)
            productivity.append(
                {
                    "user_id": user.id,
                    "user_name": user.name,
                    "total_tasks": total,
                    "completed_tasks": done,
                    "completion_rate": round(done / total * 100, 2) if total else 0,
                }
            )
        return {
            "generated_at": str(now),
            "overview": {
                "total_tasks": len(tasks),
                "total_users": len(users),
                "total_categories": len(categories),
            },
            "tasks_by_status": {key: status[key] for key in VALID_STATUSES},
            "tasks_by_priority": {
                name: priority[i]
                for i, name in enumerate(
                    ("critical", "high", "medium", "low", "minimal"), 1
                )
            },
            "overdue": {
                "count": len(overdue),
                "tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "due_date": str(task.due_date),
                        "days_overdue": (now - task.due_date).days,
                    }
                    for task in overdue
                ],
            },
            "recent_activity": {
                "tasks_created_last_7_days": sum(
                    task.created_at >= recent for task in tasks
                ),
                "tasks_completed_last_7_days": sum(
                    task.status == "done" and task.updated_at >= recent
                    for task in tasks
                ),
            },
            "user_productivity": productivity,
        }

    def user_report(self, user_id):
        user = self.store.get(User, user_id)
        tasks = self.store.tasks({"user_id": user_id})
        stats = statistics(tasks)
        stats["total_tasks"] = stats.pop("total")
        stats["high_priority"] = sum(task.priority <= 2 for task in tasks)
        return {
            "user": {"id": user.id, "name": user.name, "email": user.email},
            "statistics": stats,
        }

    def categories(self):
        return [
            {**category_view(category), "task_count": count}
            for category, count in self.store.categories_with_counts()
        ]

    def save_category(self, body, category_id=None):
        values = category_values(body, category_id is None)
        category = (
            self.store.get(Category, category_id)
            if category_id is not None
            else Category()
        )
        for key, value in values.items():
            setattr(category, key, value)
        return category_view(self.store.save(category))

    def delete_category(self, category_id):
        self.store.delete_category(self.store.get(Category, category_id))
        return {"message": "Categoria deletada"}
