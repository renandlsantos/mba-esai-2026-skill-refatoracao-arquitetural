"""Opt-in synthetic seed for an empty database; never delete existing records."""

import argparse
import os
from sqlalchemy import select, func
from database import db
from models import User, Task, Category


def seed_data(app, password):
    if not isinstance(password, str) or len(password) < 4:
        raise ValueError("Provide SEED_PASSWORD with at least four characters")
    with app.app_context():
        if any(
            db.session.scalar(select(func.count()).select_from(model))
            for model in (User, Task, Category)
        ):
            raise ValueError(
                "Seed requires an empty synthetic database; existing data preserved"
            )
        user = User(name="Demo User", email="demo@example.test", role="user")
        user.set_password(password)
        category = Category(
            name="Demo", description="Synthetic example", color="#123456"
        )
        db.session.add_all([user, category])
        db.session.flush()
        db.session.add(
            Task(title="Synthetic demo task", user_id=user.id, category_id=category.id)
        )
        db.session.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", required=True)
    parser.parse_args()
    from app import create_app

    seed_data(create_app(), os.getenv("SEED_PASSWORD"))
    print("Synthetic seed complete")
