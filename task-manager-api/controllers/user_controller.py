"""Casos de uso de usuários e login. Retornam (dados serializáveis, status HTTP)."""
import logging

from flask import current_app

from middlewares.auth import require_admin
from models import Task, User
from utils.constants import PRIVILEGED_ROLES, ROLE_USER
from utils.dates import utc_now
from utils.errors import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError, ValidationError
from utils.validators import (
    require_json_object, validate_bool, validate_email, validate_name, validate_password,
    validate_role,
)

logger = logging.getLogger(__name__)


def _get_user_or_404(user_id):
    user = User.get_by_id(user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')
    return user


def _ensure_email_available(email, current_user_id=None):
    existing = User.get_by_email(email)
    if existing and existing.id != current_user_id:
        raise ConflictError('Email já cadastrado')


def _authorize_role_change(new_role, current_role=None):
    """Atribuir um papel privilegiado é operação administrativa."""
    if new_role in PRIVILEGED_ROLES and new_role != current_role:
        require_admin()


def list_users():
    totals_by_user = Task.count_by_user()
    result = []
    for user in User.list_all():
        data = user.to_dict()
        data['task_count'] = totals_by_user.get(user.id, (0, 0))[0]
        result.append(data)
    return result, 200


def get_user(user_id):
    user = _get_user_or_404(user_id)
    data = user.to_dict()
    data['tasks'] = [task.to_dict() for task in Task.list_by_user(user_id)]
    return data, 200


def create_user(data):
    data = require_json_object(data)
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', ROLE_USER)

    if not name:
        raise ValidationError('Nome é obrigatório')
    if not email:
        raise ValidationError('Email é obrigatório')
    if not password:
        raise ValidationError('Senha é obrigatória')

    validate_name(name)
    validate_email(email)
    validate_password(password, 'Senha deve ter no mínimo 4 caracteres')
    _ensure_email_available(email)
    validate_role(role)
    _authorize_role_change(role)

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    user.save()
    logger.info('Usuário criado: %s', user.id)
    return user.to_dict(), 201


def update_user(user_id, data):
    user = _get_user_or_404(user_id)
    data = require_json_object(data)

    if 'name' in data:
        user.name = validate_name(data['name'])
    if 'email' in data:
        validate_email(data['email'])
        _ensure_email_available(data['email'], current_user_id=user_id)
        user.email = data['email']
    if 'password' in data:
        user.set_password(validate_password(data['password'], 'Senha muito curta'))
    if 'role' in data:
        validate_role(data['role'])
        _authorize_role_change(data['role'], current_role=user.role)
        user.role = data['role']
    if 'active' in data:
        user.active = validate_bool(data['active'], 'active')

    user.save()
    return user.to_dict(), 200


def delete_user(user_id):
    user = _get_user_or_404(user_id)
    user.delete_with_tasks()
    logger.info('Usuário deletado: %s', user_id)
    return {'message': 'Usuário deletado com sucesso'}, 200


def get_user_tasks(user_id):
    _get_user_or_404(user_id)
    now = utc_now()
    return [task.to_user_task_item(now) for task in Task.list_by_user(user_id)], 200


def login(data):
    data = require_json_object(data)
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        raise ValidationError('Email e senha são obrigatórios')

    user = User.get_by_email(email)
    if not user or not user.check_password(password):
        raise UnauthorizedError('Credenciais inválidas')

    if user.has_legacy_password_hash():
        user.set_password(password)  # migração transparente MD5 → scrypt
        user.save()

    if not user.active:
        raise ForbiddenError('Usuário inativo')

    token = current_app.extensions['token_service'].issue(user.id)
    return {
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': token,
    }, 200
