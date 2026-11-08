"""Helpers de data. Ponto único para obter o "agora" em UTC."""
from datetime import datetime, timezone

from utils.constants import DATE_FORMAT


def utcnow():
    """UTC atual como datetime naive (mesmo formato das colunas existentes).

    Substitui `datetime.utcnow()`, deprecated desde Python 3.12.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def parse_date(value):
    """Converte 'YYYY-MM-DD' em datetime; levanta ValueError/TypeError se inválido."""
    return datetime.strptime(value, DATE_FORMAT)


def format_datetime(value):
    return str(value) if value else None
