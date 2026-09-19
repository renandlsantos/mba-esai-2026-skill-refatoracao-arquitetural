from database import db
from utils.clock import utc_now
from utils.constants import DEFAULT_PRIORITY


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="pending")
    priority = db.Column(db.Integer, default=DEFAULT_PRIORITY)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)
    user = db.relationship("User", backref="tasks")
    category = db.relationship("Category", backref="tasks")

    def is_overdue(self, now=None):
        return (
            self.due_date is not None
            and self.due_date < (now or utc_now())
            and self.status not in ("done", "cancelled")
        )
