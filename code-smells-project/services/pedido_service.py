"""Regras de negócio de pedidos e do relatório de vendas."""
from models import pedido_model
from services import notificacao_service
from utils.constants import FAIXAS_DESCONTO


def criar_pedido(usuario_id, itens):
    resultado = pedido_model.criar(usuario_id, itens)
    notificacao_service.pedido_criado(resultado["pedido_id"], usuario_id)
    return resultado


def atualizar_status(pedido_id, novo_status):
    pedido_model.atualizar_status(pedido_id, novo_status)
    notificacao_service.status_alterado(pedido_id, novo_status)


def calcular_desconto(faturamento):
    for faturamento_minimo, taxa in FAIXAS_DESCONTO:
        if faturamento > faturamento_minimo:
            return faturamento * taxa
    return 0


def gerar_relatorio_vendas():
    totais = pedido_model.totais_de_vendas()
    total_pedidos = totais["total_pedidos"]
    faturamento = totais["faturamento"]
    desconto = calcular_desconto(faturamento)

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": totais["pendentes"],
        "pedidos_aprovados": totais["aprovados"],
        "pedidos_cancelados": totais["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
