from flask import Blueprint, jsonify, request

from controllers import produto_controller

produto_bp = Blueprint("produtos", __name__)


@produto_bp.get("/produtos")
def listar_produtos():
    payload, status = produto_controller.listar_produtos()
    return jsonify(payload), status


@produto_bp.get("/produtos/busca")
def buscar_produtos():
    payload, status = produto_controller.buscar_produtos(request.args)
    return jsonify(payload), status


@produto_bp.get("/produtos/<int:produto_id>")
def buscar_produto(produto_id):
    payload, status = produto_controller.buscar_produto(produto_id)
    return jsonify(payload), status


@produto_bp.post("/produtos")
def criar_produto():
    payload, status = produto_controller.criar_produto(request.get_json(silent=True))
    return jsonify(payload), status


@produto_bp.put("/produtos/<int:produto_id>")
def atualizar_produto(produto_id):
    payload, status = produto_controller.atualizar_produto(produto_id, request.get_json(silent=True))
    return jsonify(payload), status


@produto_bp.delete("/produtos/<int:produto_id>")
def deletar_produto(produto_id):
    payload, status = produto_controller.deletar_produto(produto_id)
    return jsonify(payload), status
