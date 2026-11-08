"""Proteção das rotas administrativas: flag de configuração + token."""
import hmac
from functools import wraps

from flask import current_app, request

from utils.errors import ForbiddenError


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        config = current_app.config
        if not config["ENABLE_ADMIN_ROUTES"]:
            raise ForbiddenError("Rotas administrativas desabilitadas")
        token = request.headers.get("X-Admin-Token", "")
        esperado = config["ADMIN_TOKEN"]
        if not esperado or not hmac.compare_digest(token.encode("utf-8"), esperado.encode("utf-8")):
            raise ForbiddenError("Acesso negado")
        return view(*args, **kwargs)
    return wrapper
