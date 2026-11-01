from flask import Blueprint, jsonify, request

from controllers import pedido_controller

pedido_bp = Blueprint("pedidos", __name__)


@pedido_bp.post("/pedidos")
def criar_pedido():
    payload, status = pedido_controller.criar_pedido(request.get_json(silent=True))
    return jsonify(payload), status


@pedido_bp.get("/pedidos")
def listar_todos_pedidos():
    payload, status = pedido_controller.listar_todos_pedidos()
    return jsonify(payload), status


@pedido_bp.get("/pedidos/usuario/<int:usuario_id>")
def listar_pedidos_usuario(usuario_id):
    payload, status = pedido_controller.listar_pedidos_usuario(usuario_id)
    return jsonify(payload), status


@pedido_bp.put("/pedidos/<int:pedido_id>/status")
def atualizar_status_pedido(pedido_id):
    payload, status = pedido_controller.atualizar_status_pedido(pedido_id, request.get_json(silent=True))
    return jsonify(payload), status


@pedido_bp.get("/relatorios/vendas")
def relatorio_vendas():
    payload, status = pedido_controller.relatorio_vendas()
    return jsonify(payload), status
