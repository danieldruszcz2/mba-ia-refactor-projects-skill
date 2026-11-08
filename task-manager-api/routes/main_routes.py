from flask import Blueprint

from controllers import main_controller

main_bp = Blueprint('main', __name__)


@main_bp.route('/health')
def health():
    return main_controller.health()


@main_bp.route('/')
def index():
    return main_controller.index()
