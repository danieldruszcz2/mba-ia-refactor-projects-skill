"""Validação de entrada — funções puras que levantam ValidationError.

Reaproveitadas por create e update para que as regras não divirjam.
"""
import re

from utils.constants import (
    EMAIL_PATTERN, MAX_PRIORITY, MAX_TITLE_LENGTH, MIN_PASSWORD_LENGTH, MIN_PRIORITY,
    MIN_TITLE_LENGTH, TASK_STATUSES, USER_ROLES,
)
from utils.dates import parse_date
from utils.errors import ValidationError

INVALID_DATA = 'Dados inválidos'


def require_payload(data):
    if not data or not isinstance(data, dict):
        raise ValidationError(INVALID_DATA)
    return data


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def parse_int(value, message):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError(message)


# ---- tasks ------------------------------------------------------------------

def validate_title(title):
    if not isinstance(title, str):
        raise ValidationError('Título deve ser um texto')
    if len(title) < MIN_TITLE_LENGTH:
        raise ValidationError('Título muito curto')
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError('Título muito longo')
    return title


def validate_description(description):
    if description is not None and not isinstance(description, str):
        raise ValidationError('Descrição inválida')
    return description


def validate_status(status):
    if not isinstance(status, str) or status not in TASK_STATUSES:
        raise ValidationError('Status inválido')
    return status


def validate_priority(priority):
    if not is_number(priority) or priority < MIN_PRIORITY or priority > MAX_PRIORITY:
        raise ValidationError(f'Prioridade deve ser entre {MIN_PRIORITY} e {MAX_PRIORITY}')
    return priority


def validate_due_date(value):
    """Retorna datetime ou None (valor vazio limpa a data)."""
    if not value:
        return None
    try:
        return parse_date(value)
    except (TypeError, ValueError):
        raise ValidationError('Formato de data inválido. Use YYYY-MM-DD')


def normalize_tags(tags):
    """Lista de strings → 'a,b'; string é mantida; vazio → None."""
    if not tags:
        return None
    if isinstance(tags, list):
        if not all(isinstance(tag, str) for tag in tags):
            raise ValidationError('Tags inválidas')
        return ','.join(tags)
    if isinstance(tags, str):
        return tags
    raise ValidationError('Tags inválidas')


# ---- users ------------------------------------------------------------------

def validate_name(name):
    if not isinstance(name, str):
        raise ValidationError('Nome inválido')
    return name


def validate_email(email):
    if not isinstance(email, str) or not re.match(EMAIL_PATTERN, email):
        raise ValidationError('Email inválido')
    return email


def validate_password(password, message=f'Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres'):
    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(message)
    return password


def validate_role(role):
    if not isinstance(role, str) or role not in USER_ROLES:
        raise ValidationError('Role inválido')
    return role


def validate_active(active):
    if not isinstance(active, bool):
        raise ValidationError('Campo active deve ser booleano')
    return active


# ---- categories -------------------------------------------------------------

def validate_optional_text(value, message):
    if value is not None and not isinstance(value, str):
        raise ValidationError(message)
    return value
