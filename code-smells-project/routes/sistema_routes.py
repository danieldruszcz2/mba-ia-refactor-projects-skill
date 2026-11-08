from flask import Blueprint

from controllers import sistema_controller
from middlewares.auth import admin_required

bp = Blueprint("sistema", __name__)

bp.add_url_rule("/", "index", sistema_controller.index, methods=["GET"])
bp.add_url_rule("/health", "health_check", sistema_controller.health_check, methods=["GET"])
bp.add_url_rule("/admin/reset-db", "reset_database", admin_required(sistema_controller.reset_database), methods=["POST"])
bp.add_url_rule("/admin/query", "executar_query", admin_required(sistema_controller.executar_query), methods=["POST"])
