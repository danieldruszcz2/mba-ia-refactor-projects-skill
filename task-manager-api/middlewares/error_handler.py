"""Tratamento centralizado de erros: toda falha vira JSON `{"error": ...}`."""
import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from models.database import db
from utils.errors import AppError

logger = logging.getLogger(__name__)

INTERNAL_ERROR = 'Erro interno'


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({'error': error.message}), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({'error': error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        db.session.rollback()
        logger.exception('Erro não tratado: %s', error)
        return jsonify({'error': INTERNAL_ERROR}), 500
