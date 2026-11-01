"""Casos de uso de sistema: índice, health check e administração."""
import logging

from models import sistema_model
from utils.constants import API_VERSAO
from utils.errors import ValidationError
from utils.validators import exigir_objeto

logger = logging.getLogger(__name__)


def index():
    return {
        "mensagem": "Bem-vindo à API da Loja",
        "versao": API_VERSAO,
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    }, 200


def health_check():
    try:
        contagens = sistema_model.contar_registros()
    except Exception:
        # Health check reporta indisponibilidade no próprio formato, sem detalhes internos.
        logger.exception("Health check falhou")
        return {"status": "erro", "detalhes": "Banco de dados indisponível"}, 500
    return {
        "status": "ok",
        "database": "connected",
        "counts": contagens,
        "versao": API_VERSAO,
    }, 200


def resetar_banco():
    sistema_model.resetar_banco()
    logger.warning("Banco de dados resetado via rota administrativa")
    return {"mensagem": "Banco de dados resetado", "sucesso": True}, 200


def executar_query(dados):
    dados = exigir_objeto(dados, "Query não informada")
    query = dados.get("sql", "")
    if not query or not isinstance(query, str):
        raise ValidationError("Query não informada")
    if not query.strip().upper().startswith("SELECT"):
        raise ValidationError("Apenas consultas SELECT são permitidas")
    return {"dados": sistema_model.executar_consulta_leitura(query), "sucesso": True}, 200
