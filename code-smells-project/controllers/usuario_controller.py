"""Casos de uso de usuários e autenticação."""
import logging

from models import usuario_model
from utils.errors import NotFoundError, UnauthorizedError
from utils.security import hash_senha, verificar_senha
from utils.validators import validar_login, validar_usuario

logger = logging.getLogger(__name__)


def listar_usuarios():
    return {"dados": usuario_model.listar(), "sucesso": True}, 200


def buscar_usuario(usuario_id):
    usuario = usuario_model.buscar_por_id(usuario_id)
    if not usuario:
        raise NotFoundError("Usuário não encontrado")
    return {"dados": usuario, "sucesso": True}, 200


def criar_usuario(dados):
    usuario = validar_usuario(dados)
    usuario_id = usuario_model.criar(usuario["nome"], usuario["email"], hash_senha(usuario["senha"]))
    logger.info("Usuário criado com ID %s", usuario_id)
    return {"dados": {"id": usuario_id}, "sucesso": True}, 201


def login(dados):
    email, senha = validar_login(dados)
    for credencial in usuario_model.buscar_credenciais_por_email(email):
        if verificar_senha(senha, credencial["senha"]):
            logger.info("Login bem-sucedido para usuario %s", credencial["id"])
            usuario = {
                "id": credencial["id"],
                "nome": credencial["nome"],
                "email": credencial["email"],
                "tipo": credencial["tipo"],
            }
            return {"dados": usuario, "sucesso": True, "mensagem": "Login OK"}, 200

    logger.info("Tentativa de login falhou")
    raise UnauthorizedError("Email ou senha inválidos", {"sucesso": False})
