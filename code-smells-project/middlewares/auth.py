"""Proteção das rotas administrativas: flag de configuração + token de admin."""
import hmac
from functools import wraps

from flask import current_app, request

from utils.constants import ADMIN_TOKEN_HEADER
from utils.errors import ForbiddenError


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_app.config["ENABLE_ADMIN_ROUTES"]:
            raise ForbiddenError("Rotas administrativas desabilitadas")
        token_esperado = current_app.config["ADMIN_TOKEN"]
        token_recebido = request.headers.get(ADMIN_TOKEN_HEADER, "")
        if not token_esperado or not hmac.compare_digest(token_recebido, token_esperado):
            raise ForbiddenError("Acesso negado")
        return view(*args, **kwargs)

    return wrapper
