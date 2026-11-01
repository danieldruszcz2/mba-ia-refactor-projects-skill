from flask import Blueprint

from controllers import main_controller
from routes import respond

main_bp = Blueprint('main', __name__)


@main_bp.get('/')
def index():
    return respond(main_controller.index())


@main_bp.get('/health')
def health():
    return respond(main_controller.health())
