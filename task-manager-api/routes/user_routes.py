from flask import Blueprint, current_app, jsonify, request

from controllers import user_controller
from middlewares.auth import admin_required, ensure_admin

user_bp = Blueprint('users', __name__)


@user_bp.route('/users', methods=['GET'])
def get_users():
    return jsonify(user_controller.list_users()), 200


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return jsonify(user_controller.get_user(user_id)), 200


@user_bp.route('/users', methods=['POST'])
def create_user():
    return jsonify(user_controller.create_user(request.get_json(), ensure_admin)), 201


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    return jsonify(user_controller.update_user(user_id, request.get_json(), ensure_admin)), 200


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    return jsonify(user_controller.delete_user(user_id)), 200


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    return jsonify(user_controller.get_user_tasks(user_id)), 200


@user_bp.route('/login', methods=['POST'])
def login():
    result = user_controller.login(request.get_json(), current_app.config['SECRET_KEY'])
    return jsonify(result), 200
