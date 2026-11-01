from datetime import datetime


def index():
    return {'message': 'Task Manager API', 'version': '1.0'}, 200


def health():
    return {'status': 'ok', 'timestamp': str(datetime.now())}, 200
