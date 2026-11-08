"""Casos de uso de usuários e autenticação."""
import logging

from models.task import Task
from models.user import User
from utils import validators as v
from utils.constants import PRIVILEGED_ROLES, ROLE_USER
from utils.dates import utcnow
from utils.errors import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError, ValidationError
from utils.security import generate_token

logger = logging.getLogger(__name__)

USER_NOT_FOUND = 'Usuário não encontrado'
INVALID_CREDENTIALS = 'Credenciais inválidas'


def _get_user_or_404(user_id):
    user = User.get_by_id(user_id)
    if not user:
        raise NotFoundError(USER_NOT_FOUND)
    return user


def _ensure_email_available(email, current_user_id=None):
    existing = User.find_by_email(email)
    if existing and existing.id != current_user_id:
        raise ConflictError('Email já cadastrado')


def list_users():
    task_counts = {user_id: total for user_id, (total, _) in Task.totals_by_user().items()}
    result = []
    for user in User.list_all():
        data = user.to_dict()
        data['task_count'] = task_counts.get(user.id, 0)
        result.append(data)
    return result


def get_user(user_id):
    user = _get_user_or_404(user_id)
    data = user.to_dict()
    data['tasks'] = [task.to_dict() for task in Task.list_by_user(user_id)]
    return data


def create_user(data, ensure_admin):
    """`ensure_admin` é fornecido pela camada de auth e levanta 403 se o chamador não for admin."""
    data = v.require_payload(data)
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
    v.validate_name(name)
    v.validate_email(email)
    v.validate_password(password)
    _ensure_email_available(email)
    v.validate_role(role)
    if role in PRIVILEGED_ROLES:
        ensure_admin()

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    user.save()
    logger.info('Usuário criado: %s', user.id)
    return user.to_dict()


def update_user(user_id, data, ensure_admin):
    user = _get_user_or_404(user_id)
    data = v.require_payload(data)

    if 'name' in data:
        user.name = v.validate_name(data['name'])
    if 'email' in data:
        v.validate_email(data['email'])
        _ensure_email_available(data['email'], user_id)
        user.email = data['email']
    if 'password' in data:
        user.set_password(v.validate_password(data['password'], 'Senha muito curta'))
    if 'role' in data:
        role = v.validate_role(data['role'])
        if role != user.role and (role in PRIVILEGED_ROLES or user.has_privileged_role()):
            ensure_admin()
        user.role = role
    if 'active' in data:
        user.active = v.validate_active(data['active'])

    user.save()
    return user.to_dict()


def delete_user(user_id):
    user = _get_user_or_404(user_id)
    user.delete_with_tasks()
    logger.info('Usuário deletado: %s', user_id)
    return {'message': 'Usuário deletado com sucesso'}


def get_user_tasks(user_id):
    _get_user_or_404(user_id)
    now = utcnow()
    return [task.to_user_task_dict(now) for task in Task.list_by_user(user_id)]


def login(data, secret_key):
    data = v.require_payload(data)
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        raise ValidationError('Email e senha são obrigatórios')
    if not isinstance(email, str) or not isinstance(password, str):
        raise ValidationError(v.INVALID_DATA)

    user = User.find_by_email(email)
    if not user or not user.check_password(password):
        raise UnauthorizedError(INVALID_CREDENTIALS)
    if not user.active:
        raise ForbiddenError('Usuário inativo')

    return {
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': generate_token(secret_key, user.id),
    }
