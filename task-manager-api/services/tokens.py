from flask import current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired


def serializer():
    return URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"], salt="task-manager-auth"
    )


def issue_token(user_id):
    return serializer().dumps({"user_id": user_id})


def verify_token(token, max_age=3600):
    try:
        return serializer().loads(token, max_age=max_age).get("user_id")
    except (BadSignature, SignatureExpired):
        return None
