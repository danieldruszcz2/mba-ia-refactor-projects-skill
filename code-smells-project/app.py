"""Composition root: monta config, logging, banco, CORS, error handlers e rotas.

Start: `python app.py` (ou `flask --app app run`, que usa `create_app`).
"""
import logging

from flask import Flask
from flask_cors import CORS

from config.settings import load_config
from middlewares.error_handler import register_error_handlers
from models.database import close_connection, init_db
from routes.pedido_routes import pedido_bp
from routes.produto_routes import produto_bp
from routes.sistema_routes import sistema_bp
from routes.usuario_routes import usuario_bp

logger = logging.getLogger(__name__)


def create_app(config_overrides=None):
    config = load_config()
    config.update(config_overrides or {})

    logging.basicConfig(
        level=config["LOG_LEVEL"],
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    app = Flask(__name__)
    app.config.from_mapping(config)

    if config["CORS_ORIGINS"]:
        CORS(app, origins=config["CORS_ORIGINS"])

    init_db(config["DATABASE_PATH"])
    app.teardown_appcontext(close_connection)

    register_error_handlers(app)
    for blueprint in (sistema_bp, produto_bp, usuario_bp, pedido_bp):
        app.register_blueprint(blueprint)

    return app


if __name__ == "__main__":
    app = create_app()
    logger.info("Servidor iniciado em http://%s:%s", app.config["HOST"], app.config["PORT"])
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
