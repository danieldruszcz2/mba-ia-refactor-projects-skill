"""Composition root: monta config, logging, banco, CORS, error handlers e rotas."""
import logging

from flask import Flask
from flask_cors import CORS

from config import Config
from middlewares.error_handler import register_error_handlers
from models.database import init_db
from routes import register_routes
from services.auth_service import TokenService


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    logging.basicConfig(
        level=app.config['LOG_LEVEL'],
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    )

    if app.config['CORS_ORIGINS']:
        CORS(app, origins=app.config['CORS_ORIGINS'])

    init_db(app)
    app.extensions['token_service'] = TokenService(
        app.config['SECRET_KEY'], app.config['TOKEN_MAX_AGE_SECONDS'])

    register_error_handlers(app)
    register_routes(app)
    return app


if __name__ == '__main__':
    application = create_app()
    application.run(
        host=application.config['HOST'],
        port=application.config['PORT'],
        debug=application.config['DEBUG'],
    )
