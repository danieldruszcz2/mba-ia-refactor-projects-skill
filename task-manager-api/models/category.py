from sqlalchemy import func

from models.database import db, transaction
from utils.constants import DEFAULT_CATEGORY_COLOR
from utils.dates import utcnow


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    color = db.Column(db.String(7), default=DEFAULT_CATEGORY_COLOR)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'created_at': str(self.created_at),
        }

    # ---- consultas ----------------------------------------------------------

    @classmethod
    def get_by_id(cls, category_id):
        return db.session.get(cls, category_id)

    @classmethod
    def list_all(cls):
        return cls.query.order_by(cls.id).all()

    @classmethod
    def count(cls):
        return cls.query.count()

    @staticmethod
    def task_counts():
        """{category_id: quantidade de tasks} numa única query agregada."""
        from models.task import Task
        rows = (db.session.query(Task.category_id, func.count(Task.id))
                .group_by(Task.category_id).all())
        return {category_id: total for category_id, total in rows}

    # ---- escrita ------------------------------------------------------------

    def save(self):
        with transaction() as session:
            session.add(self)
        return self

    def delete(self):
        # O relacionamento (backref `tasks`) zera category_id das tasks no mesmo flush.
        with transaction() as session:
            session.delete(self)
