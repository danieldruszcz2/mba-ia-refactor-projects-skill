import logging

from flask import current_app, jsonify, request

from models import sistema_model
from utils.constants import API_VERSION
from utils.errors import ValidationError

logger = logging.getLogger(__name__)


def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": API_VERSION,
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


def health_check():
    try:
        counts = sistema_model.contagens()
    except Exception:
        logger.exception("Health check: falha ao acessar o banco")
        return jsonify({"status": "erro", "detalhes": "Falha ao acessar o banco de dados"}), 500
    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": counts,
        "versao": API_VERSION,
        "ambiente": current_app.config["ENVIRONMENT"],
    }), 200


def reset_database():
    sistema_model.resetar()
    logger.warning("Banco de dados resetado via /admin/reset-db")
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200


def executar_query():
    dados = request.get_json(silent=True)
    sql = dados.get("sql", "") if isinstance(dados, dict) else ""
    if not sql or not isinstance(sql, str):
        raise ValidationError("Query não informada")
    if not sql.strip().upper().startswith("SELECT"):
        raise ValidationError("Apenas consultas SELECT são permitidas")
    try:
        resultado = sistema_model.consultar_somente_leitura(sql)
    except Exception:
        logger.exception("Falha na consulta administrativa")
        raise ValidationError("Query inválida")
    logger.warning("Consulta administrativa executada")
    return jsonify({"dados": resultado, "sucesso": True}), 200
