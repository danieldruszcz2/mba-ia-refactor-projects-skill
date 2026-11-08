"""Casos de uso de categorias."""
from models.category import Category
from utils import validators as v
from utils.constants import DEFAULT_CATEGORY_COLOR
from utils.errors import NotFoundError, ValidationError


def _get_category_or_404(category_id):
    category = Category.get_by_id(category_id)
    if not category:
        raise NotFoundError('Categoria não encontrada')
    return category


def list_categories():
    task_counts = Category.task_counts()
    result = []
    for category in Category.list_all():
        data = category.to_dict()
        data['task_count'] = task_counts.get(category.id, 0)
        result.append(data)
    return result


def create_category(data):
    data = v.require_payload(data)
    name = data.get('name')
    if not name:
        raise ValidationError('Nome é obrigatório')

    category = Category(
        name=v.validate_name(name),
        description=v.validate_optional_text(data.get('description', ''), 'Descrição inválida'),
        color=v.validate_optional_text(data.get('color', DEFAULT_CATEGORY_COLOR), 'Cor inválida'),
    )
    category.save()
    return category.to_dict()


def update_category(category_id, data):
    category = _get_category_or_404(category_id)
    data = v.require_payload(data)

    if 'name' in data:
        category.name = v.validate_name(data['name'])
    if 'description' in data:
        category.description = v.validate_optional_text(data['description'], 'Descrição inválida')
    if 'color' in data:
        category.color = v.validate_optional_text(data['color'], 'Cor inválida')

    category.save()
    return category.to_dict()


def delete_category(category_id):
    _get_category_or_404(category_id).delete()
    return {'message': 'Categoria deletada'}
