"""Tratamento centralizado de erros: formato único {"erro": ...}, sem vazar detalhes internos."""
import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from utils.errors import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        payload = {"erro": error.mensagem}
        payload.update(error.extra)
        return jsonify(payload), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({"erro": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.exception("Erro inesperado ao processar requisição")
        return jsonify({"erro": "Erro interno do servidor"}), 500
