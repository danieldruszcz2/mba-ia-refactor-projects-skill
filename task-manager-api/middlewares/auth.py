"""Autorização de operações administrativas."""
from functools import wraps

from flask import current_app, request

from models import User
from utils.errors import ForbiddenError

_BEARER_PREFIX = 'Bearer '


def _bearer_token():
    header = request.headers.get('Authorization', '')
    if header.startswith(_BEARER_PREFIX):
        return header[len(_BEARER_PREFIX):].strip()
    return None


def require_admin():
    """403 se as rotas admin estão desligadas ou se o token não é de um admin ativo."""
    if not current_app.config['ENABLE_ADMIN_ROUTES']:
        raise ForbiddenError('Operação administrativa desabilitada')

    user_id = current_app.extensions['token_service'].verify(_bearer_token())
    user = User.get_by_id(user_id) if user_id is not None else None
    if not user or not user.active or not user.is_admin():
        raise ForbiddenError('Acesso restrito a administradores')
    return user


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        require_admin()
        return view(*args, **kwargs)
    return wrapper
