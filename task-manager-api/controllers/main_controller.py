"""Endpoints gerais (raiz e health check)."""
from datetime import datetime


def index():
    return {'message': 'Task Manager API', 'version': '1.0'}


def health():
    return {'status': 'ok', 'timestamp': str(datetime.now())}
