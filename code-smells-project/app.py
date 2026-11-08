"""Composition root: monta config, logging, banco, middlewares e rotas."""
import logging

from flask import Flask
from flask_cors import CORS

from config.settings import Config
from middlewares.error_handler import register_error_handlers
from models import database
from routes import pedido_routes, produto_routes, sistema_routes, usuario_routes

logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    logging.basicConfig(
        level=app.config["LOG_LEVEL"],
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    CORS(app, origins=app.config["CORS_ORIGINS"])
    database.init_app(app)
    register_error_handlers(app)

    for blueprint in (produto_routes.bp, usuario_routes.bp, pedido_routes.bp, sistema_routes.bp):
        app.register_blueprint(blueprint)

    return app


if __name__ == "__main__":
    app = create_app()
    logger.info("Servidor iniciado em http://%s:%s", app.config["HOST"], app.config["PORT"])
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
