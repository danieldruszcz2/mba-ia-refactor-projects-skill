"""Notificações de pedido. Hoje apenas registra em log; ponto único para integrar email/SMS/push reais."""
import logging

logger = logging.getLogger(__name__)


def pedido_criado(pedido_id, usuario_id):
    logger.info("EMAIL: Pedido %s criado para usuario %s", pedido_id, usuario_id)
    logger.info("SMS: Seu pedido foi recebido! (pedido %s)", pedido_id)
    logger.info("PUSH: Novo pedido recebido pelo sistema (pedido %s)", pedido_id)


def pedido_aprovado(pedido_id):
    logger.info("NOTIFICAÇÃO: Pedido %s foi aprovado! Preparar envio.", pedido_id)


def pedido_cancelado(pedido_id):
    logger.info("NOTIFICAÇÃO: Pedido %s cancelado. Devolver estoque.", pedido_id)
