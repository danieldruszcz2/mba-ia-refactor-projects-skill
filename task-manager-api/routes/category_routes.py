from flask import Blueprint, request

from controllers import category_controller
from routes import respond

category_bp = Blueprint('categories', __name__)


@category_bp.get('/categories')
def get_categories():
    return respond(category_controller.list_categories())


@category_bp.post('/categories')
def create_category():
    return respond(category_controller.create_category(request.get_json()))


@category_bp.put('/categories/<int:cat_id>')
def update_category(cat_id):
    return respond(category_controller.update_category(cat_id, request.get_json()))


@category_bp.delete('/categories/<int:cat_id>')
def delete_category(cat_id):
    return respond(category_controller.delete_category(cat_id))
