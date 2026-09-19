from sqlalchemy import select, func, or_, delete, update
from sqlalchemy.orm import joinedload, selectinload
from database import db
from models import User, Task, Category
from errors import DomainError


class Store:
    def get(self, model, entity_id):
        value = db.session.get(model, entity_id)
        if value is None:
            raise DomainError("Recurso não encontrado", 404)
        return value

    def email_user(self, email):
        return db.session.scalar(select(User).where(User.email == email))

    def tasks(self, filters=None, related=False):
        query = select(Task).order_by(Task.id)
        filters = filters or {}
        if filters.get("q"):
            term = "%" + filters["q"] + "%"
            query = query.where(or_(Task.title.like(term), Task.description.like(term)))
        for key in ("status", "priority", "user_id", "category_id"):
            if key in filters:
                query = query.where(getattr(Task, key) == filters[key])
        if related:
            query = query.options(joinedload(Task.user), joinedload(Task.category))
        return list(db.session.scalars(query))

    def users(self, with_tasks=False):
        query = select(User).order_by(User.id)
        if with_tasks:
            query = query.options(selectinload(User.tasks))
        return list(db.session.scalars(query))

    def categories(self):
        return list(db.session.scalars(select(Category).order_by(Category.id)))

    def categories_with_counts(self):
        return list(
            db.session.execute(
                select(Category, func.count(Task.id))
                .outerjoin(Task, Task.category_id == Category.id)
                .group_by(Category.id)
                .order_by(Category.id)
            )
        )

    def save(self, entity):
        db.session.add(entity)
        db.session.commit()
        return entity

    def commit(self):
        db.session.commit()

    def delete_task(self, task):
        db.session.delete(task)
        db.session.commit()

    def delete_user(self, user):
        db.session.execute(delete(Task).where(Task.user_id == user.id))
        db.session.delete(user)
        db.session.commit()

    def delete_category(self, category):
        db.session.execute(
            update(Task).where(Task.category_id == category.id).values(category_id=None)
        )
        db.session.delete(category)
        db.session.commit()
