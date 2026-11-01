"""Validação de entrada reutilizada por create e update (lança ValidationError → 400)."""
import re
from datetime import datetime

from utils.constants import (
    COLOR_PATTERN, DATE_FORMAT, EMAIL_PATTERN, MAX_PRIORITY, MAX_TITLE_LENGTH,
    MIN_PASSWORD_LENGTH, MIN_PRIORITY, MIN_TITLE_LENGTH, TASK_STATUSES, USER_ROLES,
)
from utils.errors import ValidationError


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def require_json_object(data, allow_empty=False):
    if not isinstance(data, dict) or (not data and not allow_empty):
        raise ValidationError('Dados inválidos')
    return data


def validate_title(title):
    if not isinstance(title, str):
        raise ValidationError('Título inválido')
    if len(title) < MIN_TITLE_LENGTH:
        raise ValidationError('Título muito curto')
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError('Título muito longo')
    return title


def validate_status(status):
    if status not in TASK_STATUSES:
        raise ValidationError('Status inválido')
    return status


def validate_priority(priority):
    if not _is_int(priority):
        raise ValidationError('Prioridade inválida')
    if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
        raise ValidationError('Prioridade deve ser entre 1 e 5')
    return priority


def validate_optional_id(value, field):
    """IDs de relacionamento: ausente/nulo/0 significa "sem vínculo"."""
    if not value:
        return value
    if not _is_int(value):
        raise ValidationError(f'{field} inválido')
    return value


def parse_due_date(value):
    try:
        return datetime.strptime(value, DATE_FORMAT)
    except (TypeError, ValueError):
        raise ValidationError('Formato de data inválido. Use YYYY-MM-DD')


def normalize_tags(tags):
    """Lista de strings → 'a,b'; string e None são mantidos como estão."""
    if tags is None or isinstance(tags, str):
        return tags
    if isinstance(tags, list) and all(isinstance(tag, str) for tag in tags):
        return ','.join(tags)
    raise ValidationError('Tags inválidas')


def validate_name(name):
    if not name or not isinstance(name, str):
        raise ValidationError('Nome é obrigatório')
    return name


def validate_email(email):
    if not isinstance(email, str) or not re.match(EMAIL_PATTERN, email):
        raise ValidationError('Email inválido')
    return email


def validate_password(password, too_short_message):
    if not isinstance(password, str):
        raise ValidationError('Senha inválida')
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(too_short_message)
    return password


def validate_role(role):
    if role not in USER_ROLES:
        raise ValidationError('Role inválido')
    return role


def validate_bool(value, field):
    if not isinstance(value, bool):
        raise ValidationError(f'Campo {field} deve ser booleano')
    return value


def validate_color(color):
    if not isinstance(color, str) or not re.match(COLOR_PATTERN, color):
        raise ValidationError('Cor inválida')
    return color


def parse_int_query_param(value, field):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError(f'Parâmetro {field} inválido')
