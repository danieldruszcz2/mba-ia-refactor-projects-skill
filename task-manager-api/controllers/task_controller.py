"""Casos de uso de tasks. Retornam (dados serializáveis, status HTTP)."""
import logging

from models import Category, Task, User
from utils.constants import DEFAULT_PRIORITY, STATUS_DONE, STATUS_PENDING, TASK_STATUSES
from utils.dates import utc_now
from utils.errors import NotFoundError, ValidationError
from utils.stats import calculate_percentage
from utils.validators import (
    normalize_tags, parse_due_date, parse_int_query_param, require_json_object,
    validate_optional_id, validate_priority, validate_status, validate_title,
)

logger = logging.getLogger(__name__)


def _get_task_or_404(task_id):
    task = Task.get_by_id(task_id)
    if not task:
        raise NotFoundError('Task não encontrada')
    return task


def _validated_user_id(value):
    user_id = validate_optional_id(value, 'user_id')
    if user_id and not User.get_by_id(user_id):
        raise NotFoundError('Usuário não encontrado')
    return user_id


def _validated_category_id(value):
    category_id = validate_optional_id(value, 'category_id')
    if category_id and not Category.get_by_id(category_id):
        raise NotFoundError('Categoria não encontrada')
    return category_id


def list_tasks():
    now = utc_now()
    return [task.to_list_item(now) for task in Task.list_with_relations()], 200


def get_task(task_id):
    return _get_task_or_404(task_id).to_dict_with_overdue(), 200


def create_task(data):
    data = require_json_object(data)
    title = data.get('title')
    if not title:
        raise ValidationError('Título é obrigatório')

    task = Task(
        title=validate_title(title),
        description=data.get('description', ''),
        status=validate_status(data.get('status', STATUS_PENDING)),
        priority=validate_priority(data.get('priority', DEFAULT_PRIORITY)),
        user_id=_validated_user_id(data.get('user_id')),
        category_id=_validated_category_id(data.get('category_id')),
    )
    if data.get('due_date'):
        task.due_date = parse_due_date(data['due_date'])
    if data.get('tags'):
        task.tags = normalize_tags(data['tags'])

    task.save()
    logger.info('Task criada: %s', task.id)
    return task.to_dict(), 201


def update_task(task_id, data):
    task = _get_task_or_404(task_id)
    data = require_json_object(data)

    if 'title' in data:
        task.title = validate_title(data['title'])
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        task.status = validate_status(data['status'])
    if 'priority' in data:
        task.priority = validate_priority(data['priority'])
    if 'user_id' in data:
        task.user_id = _validated_user_id(data['user_id'])
    if 'category_id' in data:
        task.category_id = _validated_category_id(data['category_id'])
    if 'due_date' in data:
        task.due_date = parse_due_date(data['due_date']) if data['due_date'] else None
    if 'tags' in data:
        task.tags = normalize_tags(data['tags'])

    task.updated_at = utc_now()
    task.save()
    logger.info('Task atualizada: %s', task.id)
    return task.to_dict(), 200


def delete_task(task_id):
    task = _get_task_or_404(task_id)
    task.delete()
    logger.info('Task deletada: %s', task_id)
    return {'message': 'Task deletada com sucesso'}, 200


def search_tasks(args):
    priority = args.get('priority', '')
    user_id = args.get('user_id', '')
    tasks = Task.search(
        text=args.get('q', ''),
        status=args.get('status', ''),
        priority=parse_int_query_param(priority, 'priority') if priority else None,
        user_id=parse_int_query_param(user_id, 'user_id') if user_id else None,
    )
    return [task.to_dict() for task in tasks], 200


def task_stats():
    total = Task.count_all()
    by_status = Task.count_by_status()
    stats = {status: by_status.get(status, 0) for status in TASK_STATUSES}
    stats['total'] = total
    stats['overdue'] = Task.count_overdue(utc_now())
    stats['completion_rate'] = calculate_percentage(by_status.get(STATUS_DONE, 0), total)
    return stats, 200
