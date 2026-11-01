from flask import Blueprint, jsonify, request

from controllers import sistema_controller
from middlewares.auth import admin_required

sistema_bp = Blueprint("sistema", __name__)


@sistema_bp.get("/")
def index():
    payload, status = sistema_controller.index()
    return jsonify(payload), status


@sistema_bp.get("/health")
def health_check():
    payload, status = sistema_controller.health_check()
    return jsonify(payload), status


@sistema_bp.post("/admin/reset-db")
@admin_required
def reset_database():
    payload, status = sistema_controller.resetar_banco()
    return jsonify(payload), status


@sistema_bp.post("/admin/query")
@admin_required
def executar_query():
    payload, status = sistema_controller.executar_query(request.get_json(silent=True))
    return jsonify(payload), status
