"""Tratamento de erros centralizado: formato único {"erro": mensagem}."""
import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from utils.errors import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        body = {"erro": err.message}
        body.update(err.extra)
        return jsonify(body), err.status

    @app.errorhandler(HTTPException)
    def handle_http_error(err):
        return jsonify({"erro": err.description or err.name}), err.code

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        logger.exception("Erro não tratado")
        return jsonify({"erro": "Erro interno do servidor"}), 500
