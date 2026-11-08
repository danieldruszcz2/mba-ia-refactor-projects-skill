"""Casos de uso de tasks."""
import logging

from models.category import Category
from models.task import Task
from models.user import User
from utils import validators as v
from utils.constants import DEFAULT_PRIORITY, TASK_STATUS_DONE, TASK_STATUS_PENDING, TASK_STATUSES
from utils.dates import utcnow
from utils.errors import NotFoundError, ValidationError
from utils.stats import percentage

logger = logging.getLogger(__name__)

TASK_NOT_FOUND = 'Task não encontrada'


def _get_task_or_404(task_id):
    task = Task.get_by_id(task_id)
    if not task:
        raise NotFoundError(TASK_NOT_FOUND)
    return task


def _ensure_user_exists(user_id):
    if user_id and not User.get_by_id(user_id):
        raise NotFoundError('Usuário não encontrado')


def _ensure_category_exists(category_id):
    if category_id and not Category.get_by_id(category_id):
        raise NotFoundError('Categoria não encontrada')


def list_tasks():
    now = utcnow()
    return [task.to_list_dict(now) for task in Task.list_with_relations()]


def get_task(task_id):
    return _get_task_or_404(task_id).to_detail_dict()


def create_task(data):
    data = v.require_payload(data)

    title = data.get('title')
    if not title:
        raise ValidationError('Título é obrigatório')
    v.validate_title(title)

    description = v.validate_description(data.get('description', ''))
    status = v.validate_status(data.get('status', TASK_STATUS_PENDING))
    priority = v.validate_priority(data.get('priority', DEFAULT_PRIORITY))
    user_id = data.get('user_id')
    category_id = data.get('category_id')
    _ensure_user_exists(user_id)
    _ensure_category_exists(category_id)

    task = Task(
        title=title,
        description=description,
        status=status,
        priority=priority,
        user_id=user_id,
        category_id=category_id,
        due_date=v.validate_due_date(data.get('due_date')),
        tags=v.normalize_tags(data.get('tags')),
    )
    task.save()
    logger.info('Task criada: %s - %s', task.id, task.title)
    return task.to_dict()


def update_task(task_id, data):
    task = _get_task_or_404(task_id)
    data = v.require_payload(data)

    if 'title' in data:
        task.title = v.validate_title(data['title'])
    if 'description' in data:
        task.description = v.validate_description(data['description'])
    if 'status' in data:
        task.status = v.validate_status(data['status'])
    if 'priority' in data:
        task.priority = v.validate_priority(data['priority'])
    if 'user_id' in data:
        _ensure_user_exists(data['user_id'])
        task.user_id = data['user_id']
    if 'category_id' in data:
        _ensure_category_exists(data['category_id'])
        task.category_id = data['category_id']
    if 'due_date' in data:
        task.due_date = v.validate_due_date(data['due_date'])
    if 'tags' in data:
        task.tags = v.normalize_tags(data['tags'])

    task.updated_at = utcnow()
    task.save()
    logger.info('Task atualizada: %s', task.id)
    return task.to_dict()


def delete_task(task_id):
    task = _get_task_or_404(task_id)
    task.delete()
    logger.info('Task deletada: %s', task_id)
    return {'message': 'Task deletada com sucesso'}


def search_tasks(args):
    priority = args.get('priority', '')
    user_id = args.get('user_id', '')
    tasks = Task.search(
        text=args.get('q', ''),
        status=args.get('status', ''),
        priority=v.parse_int(priority, 'Prioridade inválida') if priority else None,
        user_id=v.parse_int(user_id, 'user_id inválido') if user_id else None,
    )
    return [task.to_dict() for task in tasks]


def task_stats():
    by_status = Task.count_by_status()
    total = Task.count()
    done = by_status.get(TASK_STATUS_DONE, 0)
    stats = {status: by_status.get(status, 0) for status in TASK_STATUSES}
    stats.update({
        'total': total,
        'overdue': Task.count_overdue(utcnow()),
        'completion_rate': percentage(done, total),
    })
    return stats
