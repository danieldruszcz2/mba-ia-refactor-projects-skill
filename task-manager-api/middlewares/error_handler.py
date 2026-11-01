"""Tratamento centralizado de erros: sempre responde JSON no formato {'error': ...}."""
import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from models.database import db
from utils.errors import DomainError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(DomainError)
    def handle_domain_error(error):
        db.session.rollback()
        return jsonify({'error': error.message}), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        db.session.rollback()
        return jsonify({'error': error.name}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        db.session.rollback()
        logger.exception('Erro inesperado ao processar a requisição')
        return jsonify({'error': 'Erro interno'}), 500
