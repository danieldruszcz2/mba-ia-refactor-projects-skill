from flask import Blueprint, jsonify, request

from controllers import usuario_controller

usuario_bp = Blueprint("usuarios", __name__)


@usuario_bp.get("/usuarios")
def listar_usuarios():
    payload, status = usuario_controller.listar_usuarios()
    return jsonify(payload), status


@usuario_bp.get("/usuarios/<int:usuario_id>")
def buscar_usuario(usuario_id):
    payload, status = usuario_controller.buscar_usuario(usuario_id)
    return jsonify(payload), status


@usuario_bp.post("/usuarios")
def criar_usuario():
    payload, status = usuario_controller.criar_usuario(request.get_json(silent=True))
    return jsonify(payload), status


@usuario_bp.post("/login")
def login():
    payload, status = usuario_controller.login(request.get_json(silent=True))
    return jsonify(payload), status
