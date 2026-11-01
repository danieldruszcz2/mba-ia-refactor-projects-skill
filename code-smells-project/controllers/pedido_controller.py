"""Casos de uso de pedidos e relatório de vendas."""
from models import pedido_model
from services import pedido_service
from utils.validators import validar_pedido, validar_status_pedido


def criar_pedido(dados):
    usuario_id, itens = validar_pedido(dados)
    resultado = pedido_service.criar_pedido(usuario_id, itens)
    return {"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}, 201


def listar_pedidos_usuario(usuario_id):
    return {"dados": pedido_model.listar(usuario_id=usuario_id), "sucesso": True}, 200


def listar_todos_pedidos():
    return {"dados": pedido_model.listar(), "sucesso": True}, 200


def atualizar_status_pedido(pedido_id, dados):
    novo_status = validar_status_pedido(dados)
    pedido_service.atualizar_status(pedido_id, novo_status)
    return {"sucesso": True, "mensagem": "Status atualizado"}, 200


def relatorio_vendas():
    return {"dados": pedido_service.gerar_relatorio_vendas(), "sucesso": True}, 200
