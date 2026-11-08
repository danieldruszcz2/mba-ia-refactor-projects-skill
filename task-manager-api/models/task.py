from sqlalchemy import case, func
from sqlalchemy.orm import joinedload

from models.database import db, transaction
from utils.constants import (
    DEFAULT_PRIORITY, TASK_CLOSED_STATUSES, TASK_STATUS_DONE, TASK_STATUS_PENDING,
)
from utils.dates import format_datetime, utcnow


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default=TASK_STATUS_PENDING)
    priority = db.Column(db.Integer, default=DEFAULT_PRIORITY)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')

    # ---- regras do registro -------------------------------------------------

    def is_overdue(self, now=None):
        if not self.due_date or self.status in TASK_CLOSED_STATUSES:
            return False
        return self.due_date < (now or utcnow())

    def days_overdue(self, now=None):
        return ((now or utcnow()) - self.due_date).days

    # ---- serialização -------------------------------------------------------

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'due_date': format_datetime(self.due_date),
            'tags': self.tags.split(',') if self.tags else [],
        }

    def to_detail_dict(self, now=None):
        data = self.to_dict()
        data['overdue'] = self.is_overdue(now)
        return data

    def to_list_dict(self, now=None):
        """Representação da listagem geral: inclui nomes de usuário e categoria."""
        data = self.to_detail_dict(now)
        data['user_name'] = self.user.name if self.user else None
        data['category_name'] = self.category.name if self.category else None
        return data

    def to_user_task_dict(self, now=None):
        """Representação resumida usada em GET /users/<id>/tasks."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'created_at': str(self.created_at),
            'due_date': format_datetime(self.due_date),
            'overdue': self.is_overdue(now),
        }

    def to_overdue_dict(self, now=None):
        return {
            'id': self.id,
            'title': self.title,
            'due_date': str(self.due_date),
            'days_overdue': self.days_overdue(now),
        }

    # ---- consultas ----------------------------------------------------------

    @classmethod
    def get_by_id(cls, task_id):
        return db.session.get(cls, task_id)

    @classmethod
    def list_with_relations(cls):
        return (cls.query.options(joinedload(cls.user), joinedload(cls.category))
                .order_by(cls.id).all())

    @classmethod
    def list_by_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).order_by(cls.id).all()

    @classmethod
    def search(cls, text=None, status=None, priority=None, user_id=None):
        query = cls.query
        if text:
            pattern = f'%{text}%'
            query = query.filter(db.or_(cls.title.like(pattern), cls.description.like(pattern)))
        if status:
            query = query.filter(cls.status == status)
        if priority is not None:
            query = query.filter(cls.priority == priority)
        if user_id is not None:
            query = query.filter(cls.user_id == user_id)
        return query.order_by(cls.id).all()

    @classmethod
    def count(cls):
        return cls.query.count()

    @classmethod
    def count_by_status(cls):
        rows = db.session.query(cls.status, func.count(cls.id)).group_by(cls.status).all()
        return {status: total for status, total in rows}

    @classmethod
    def count_by_priority(cls):
        rows = db.session.query(cls.priority, func.count(cls.id)).group_by(cls.priority).all()
        return {priority: total for priority, total in rows}

    @classmethod
    def _overdue_query(cls, now):
        return cls.query.filter(
            cls.due_date.isnot(None),
            cls.due_date < now,
            cls.status.notin_(TASK_CLOSED_STATUSES),
        )

    @classmethod
    def count_overdue(cls, now):
        return cls._overdue_query(now).count()

    @classmethod
    def list_overdue(cls, now):
        return cls._overdue_query(now).order_by(cls.id).all()

    @classmethod
    def count_created_since(cls, since):
        return cls.query.filter(cls.created_at >= since).count()

    @classmethod
    def count_done_since(cls, since):
        return cls.query.filter(cls.status == TASK_STATUS_DONE, cls.updated_at >= since).count()

    @classmethod
    def totals_by_user(cls):
        """{user_id: (total, concluídas)} numa única query agregada."""
        done = func.sum(case((cls.status == TASK_STATUS_DONE, 1), else_=0))
        rows = (db.session.query(cls.user_id, func.count(cls.id), done)
                .group_by(cls.user_id).all())
        return {user_id: (total, int(completed or 0)) for user_id, total, completed in rows}

    @classmethod
    def delete_by_user(cls, user_id):
        cls.query.filter_by(user_id=user_id).delete(synchronize_session=False)

    # ---- escrita ------------------------------------------------------------

    def save(self):
        with transaction() as session:
            session.add(self)
        return self

    def delete(self):
        with transaction() as session:
            session.delete(self)
