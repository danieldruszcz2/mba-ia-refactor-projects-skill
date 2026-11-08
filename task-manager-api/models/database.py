"""Instância do ORM, transações e inicialização do schema."""
from contextlib import contextmanager

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


@contextmanager
def transaction():
    """Agrupa escritas: commit no fim, rollback se qualquer etapa falhar."""
    try:
        yield db.session
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def init_db(app):
    db.init_app(app)
    with app.app_context():
        # Importa os models para registrá-los no metadata antes do create_all.
        import models  # noqa: F401
        db.create_all()
