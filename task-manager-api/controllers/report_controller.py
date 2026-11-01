"""Casos de uso de relatórios. Retornam (dados serializáveis, status HTTP)."""
from models import User
from services import report_service
from utils.errors import NotFoundError


def summary_report():
    return report_service.build_summary(), 200


def user_report(user_id):
    user = User.get_by_id(user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')
    return report_service.build_user_report(user), 200
