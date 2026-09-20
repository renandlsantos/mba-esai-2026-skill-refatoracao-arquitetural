import sqlite3
from flask import jsonify
from werkzeug.exceptions import HTTPException


class DomainError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def register_errors(app):
    @app.errorhandler(Exception)
    def handle(error):
        if isinstance(error, DomainError):
            return jsonify(erro=str(error), sucesso=False), error.status
        if isinstance(error, HTTPException):
            return jsonify(erro=error.description, sucesso=False), error.code
        if isinstance(error, sqlite3.IntegrityError):
            # Trigger failures and constraints are internal unless mapped by a use case.
            app.logger.error("Persistence operation failed: %s", type(error).__name__)
        else:
            app.logger.error("Request failed: %s", type(error).__name__)
        return jsonify(erro="Erro interno", sucesso=False), 500
