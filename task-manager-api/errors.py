from flask import jsonify
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from database import db


class DomainError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def register_errors(app):
    @app.errorhandler(Exception)
    def handle(error):
        db.session.rollback()
        if isinstance(error, DomainError):
            return jsonify(error=str(error)), error.status
        if isinstance(error, HTTPException):
            return jsonify(error=error.description), error.code
        if isinstance(error, IntegrityError):
            return jsonify(error="Conflito de dados"), 409
        app.logger.error("Request failed: %s", type(error).__name__)
        return jsonify(error="Erro interno"), 500
