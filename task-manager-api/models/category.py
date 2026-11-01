from sqlalchemy import func, select

from models.database import db, transaction
from utils.constants import DEFAULT_COLOR
from utils.dates import utc_now


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    color = db.Column(db.String(7), default=DEFAULT_COLOR)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'created_at': str(self.created_at),
        }

    def save(self):
        with transaction() as session:
            session.add(self)
        return self

    def delete(self):
        # O relacionamento Task.category (backref sem cascade de delete) faz o ORM
        # desassociar as tasks (category_id = NULL) na mesma transação.
        with transaction() as session:
            session.delete(self)

    @classmethod
    def get_by_id(cls, category_id):
        return db.session.get(cls, category_id)

    @classmethod
    def list_all(cls):
        return db.session.scalars(select(cls).order_by(cls.id)).all()

    @classmethod
    def count_all(cls):
        return db.session.scalar(select(func.count(cls.id)))
