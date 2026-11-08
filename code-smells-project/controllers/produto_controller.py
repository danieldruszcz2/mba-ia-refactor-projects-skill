import logging

from flask import jsonify, request

from models import produto_model
from utils import validators
from utils.errors import NotFoundError

logger = logging.getLogger(__name__)


def listar_produtos():
    produtos = produto_model.listar()
    logger.info("Listando %d produtos", len(produtos))
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar_produto(produto_id):
    produto = produto_model.buscar_por_id(produto_id)
    if not produto:
        raise NotFoundError("Produto não encontrado", {"sucesso": False})
    return jsonify({"dados": produto, "sucesso": True}), 200


def criar_produto():
    dados = validators.validar_produto(request.get_json(silent=True), completo=True)
    produto_id = produto_model.criar(**dados)
    logger.info("Produto criado com ID: %s", produto_id)
    return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar_produto(produto_id):
    if not produto_model.buscar_por_id(produto_id):
        raise NotFoundError("Produto não encontrado")
    dados = validators.validar_produto(request.get_json(silent=True), completo=False)
    produto_model.atualizar(produto_id, **dados)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(produto_id):
    if not produto_model.buscar_por_id(produto_id):
        raise NotFoundError("Produto não encontrado")
    produto_model.deletar(produto_id)
    logger.info("Produto %s deletado", produto_id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria") or None
    preco_min = validators.numero_opcional(request.args.get("preco_min"), "preco_min")
    preco_max = validators.numero_opcional(request.args.get("preco_max"), "preco_max")
    resultados = produto_model.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
