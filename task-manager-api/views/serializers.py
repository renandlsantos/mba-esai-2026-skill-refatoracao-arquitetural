def user_view(user):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "active": user.active,
        "created_at": str(user.created_at),
    }


def task_view(task, related=False, overdue=False):
    value = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "user_id": task.user_id,
        "category_id": task.category_id,
        "created_at": str(task.created_at),
        "updated_at": str(task.updated_at),
        "due_date": str(task.due_date) if task.due_date else None,
        "tags": task.tags.split(",") if task.tags else [],
    }
    if overdue:
        value["overdue"] = task.is_overdue()
    if related:
        value["user_name"] = task.user.name if task.user else None
        value["category_name"] = task.category.name if task.category else None
    return value


def category_view(category):
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "color": category.color,
        "created_at": str(category.created_at),
    }
