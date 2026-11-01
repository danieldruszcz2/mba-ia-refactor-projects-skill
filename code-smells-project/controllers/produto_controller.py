"""Casos de uso de produtos. Recebem dados já extraídos da requisição e devolvem (payload, status)."""
import logging

from models import produto_model
from utils.errors import NotFoundError
from utils.validators import validar_filtro_preco, validar_produto

logger = logging.getLogger(__name__)


def listar_produtos():
    produtos = produto_model.listar()
    logger.debug("Listando %d produtos", len(produtos))
    return {"dados": produtos, "sucesso": True}, 200


def buscar_produto(produto_id):
    produto = produto_model.buscar_por_id(produto_id)
    if not produto:
        raise NotFoundError("Produto não encontrado", {"sucesso": False})
    return {"dados": produto, "sucesso": True}, 200


def criar_produto(dados):
    produto = validar_produto(dados)
    produto_id = produto_model.criar(**produto)
    logger.info("Produto criado com ID %s", produto_id)
    return {"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}, 201


def atualizar_produto(produto_id, dados):
    if not produto_model.buscar_por_id(produto_id):
        raise NotFoundError("Produto não encontrado")
    produto = validar_produto(dados)
    produto_model.atualizar(produto_id, **produto)
    return {"sucesso": True, "mensagem": "Produto atualizado"}, 200


def deletar_produto(produto_id):
    if not produto_model.buscar_por_id(produto_id):
        raise NotFoundError("Produto não encontrado")
    produto_model.deletar(produto_id)
    logger.info("Produto %s deletado", produto_id)
    return {"sucesso": True, "mensagem": "Produto deletado"}, 200


def buscar_produtos(parametros):
    termo = parametros.get("q", "")
    categoria = parametros.get("categoria")
    preco_min = validar_filtro_preco(parametros.get("preco_min"), "preco_min")
    preco_max = validar_filtro_preco(parametros.get("preco_max"), "preco_max")

    resultados = produto_model.buscar(termo, categoria, preco_min, preco_max)
    return {"dados": resultados, "total": len(resultados), "sucesso": True}, 200
