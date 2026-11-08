import logging

from flask import jsonify, request

from models import usuario_model
from utils import validators
from utils.errors import NotFoundError, UnauthorizedError

logger = logging.getLogger(__name__)


def listar_usuarios():
    return jsonify({"dados": usuario_model.listar(), "sucesso": True}), 200


def buscar_usuario(usuario_id):
    usuario = usuario_model.buscar_por_id(usuario_id)
    if not usuario:
        raise NotFoundError("Usuário não encontrado")
    return jsonify({"dados": usuario, "sucesso": True}), 200


def criar_usuario():
    dados = validators.validar_usuario(request.get_json(silent=True))
    usuario_id = usuario_model.criar(dados["nome"], dados["email"], dados["senha"])
    logger.info("Usuário criado: id=%s", usuario_id)
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


def login():
    email, senha = validators.validar_login(request.get_json(silent=True))
    usuario = usuario_model.autenticar(email, senha)
    if not usuario:
        logger.info("Login falhou")
        raise UnauthorizedError("Email ou senha inválidos", {"sucesso": False})
    logger.info("Login bem-sucedido: id=%s", usuario["id"])
    return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
