"""Notificações de pedidos (simuladas via logger até existir integração real)."""
import logging

from utils.constants import STATUS_APROVADO, STATUS_CANCELADO

logger = logging.getLogger(__name__)


def pedido_criado(pedido_id, usuario_id):
    logger.info("Notificação [email/sms/push]: pedido %s criado para usuario %s", pedido_id, usuario_id)


def status_alterado(pedido_id, novo_status):
    if novo_status == STATUS_APROVADO:
        logger.info("Notificação: pedido %s aprovado, preparar envio", pedido_id)
    elif novo_status == STATUS_CANCELADO:
        logger.info("Notificação: pedido %s cancelado", pedido_id)
