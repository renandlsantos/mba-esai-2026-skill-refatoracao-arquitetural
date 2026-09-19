import hashlib
import hmac
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from utils.clock import utc_now


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="user")
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        if self.password.startswith(("scrypt:", "pbkdf2:")):
            return check_password_hash(self.password, password)
        if current_app.config["ALLOW_LEGACY_PASSWORDS"] and len(self.password) == 32:
            # Explicit opt-in migration after successful legacy verification only.
            valid = hmac.compare_digest(
                self.password,
                hashlib.md5(password.encode(), usedforsecurity=False).hexdigest(),
            )
            if valid:
                self.set_password(password)
            return valid
        return False
