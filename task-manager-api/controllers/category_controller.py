"""Casos de uso de categorias. Retornam (dados serializáveis, status HTTP)."""
from models import Category, Task
from utils.constants import DEFAULT_COLOR
from utils.errors import NotFoundError, ValidationError
from utils.validators import require_json_object, validate_color, validate_name


def _get_category_or_404(category_id):
    category = Category.get_by_id(category_id)
    if not category:
        raise NotFoundError('Categoria não encontrada')
    return category


def list_categories():
    counts = Task.count_by_category()
    result = []
    for category in Category.list_all():
        data = category.to_dict()
        data['task_count'] = counts.get(category.id, 0)
        result.append(data)
    return result, 200


def create_category(data):
    data = require_json_object(data)
    if not data.get('name'):
        raise ValidationError('Nome é obrigatório')

    category = Category(
        name=validate_name(data['name']),
        description=data.get('description', ''),
        color=validate_color(data.get('color', DEFAULT_COLOR)),
    )
    category.save()
    return category.to_dict(), 201


def update_category(category_id, data):
    category = _get_category_or_404(category_id)
    data = require_json_object(data, allow_empty=True)

    if 'name' in data:
        category.name = validate_name(data['name'])
    if 'description' in data:
        category.description = data['description']
    if 'color' in data:
        category.color = validate_color(data['color'])

    category.save()
    return category.to_dict(), 200


def delete_category(category_id):
    _get_category_or_404(category_id).delete()
    return {'message': 'Categoria deletada'}, 200
