from flask import Blueprint

from controllers import report_controller
from routes import respond

report_bp = Blueprint('reports', __name__)


@report_bp.get('/reports/summary')
def summary_report():
    return respond(report_controller.summary_report())


@report_bp.get('/reports/user/<int:user_id>')
def user_report(user_id):
    return respond(report_controller.user_report(user_id))
