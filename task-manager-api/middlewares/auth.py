"""Autenticação por token assinado e autorização de operações administrativas."""
from functools import wraps

from flask import current_app, request

from models.user import User
from utils.errors import ForbiddenError
from utils.security import read_token


def current_user():
    """Usuário do header `Authorization: Bearer <token>`, ou None."""
    header = request.headers.get('Authorization', '')
    scheme, _, token = header.partition(' ')
    if scheme.lower() != 'bearer' or not token:
        return None
    cfg = current_app.config
    user_id = read_token(cfg['SECRET_KEY'], token.strip(), cfg['TOKEN_MAX_AGE_SECONDS'])
    if user_id is None:
        return None
    user = User.get_by_id(user_id)
    return user if user and user.active else None


def ensure_admin():
    """Levanta 403 se as operações admin estão desligadas ou o chamador não é admin."""
    if not current_app.config['ENABLE_ADMIN_ROUTES']:
        raise ForbiddenError('Operações administrativas desabilitadas')
    user = current_user()
    if user is None or not user.is_admin():
        raise ForbiddenError('Acesso negado')
    return user


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        ensure_admin()
        return view(*args, **kwargs)
    return wrapper
