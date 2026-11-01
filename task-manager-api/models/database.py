"""Instância do SQLAlchemy, inicialização do schema e helper de transação."""
from contextlib import contextmanager

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Chamado pelo composition root: liga o db à app e cria as tabelas."""
    db.init_app(app)
    with app.app_context():
        import models  # noqa: F401 — registra as entidades no metadata
        db.create_all()


@contextmanager
def transaction():
    """Commit no sucesso; rollback e re-raise em qualquer erro."""
    try:
        yield db.session
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
