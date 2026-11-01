from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import joinedload

from models.database import db, transaction
from utils.constants import CLOSED_STATUSES, DEFAULT_PRIORITY, STATUS_DONE, STATUS_PENDING
from utils.dates import utc_now


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default=STATUS_PENDING)
    priority = db.Column(db.Integer, default=DEFAULT_PRIORITY)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')

    # ---- regras da entidade -------------------------------------------------

    def is_overdue(self, now=None):
        if not self.due_date or self.status in CLOSED_STATUSES:
            return False
        return self.due_date < (now or utc_now())

    # ---- serialização (contrato JSON) ---------------------------------------

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
            'due_date': str(self.due_date) if self.due_date else None,
            'tags': self.tags.split(',') if self.tags else [],
        }

    def to_dict_with_overdue(self, now=None):
        data = self.to_dict()
        data['overdue'] = self.is_overdue(now)
        return data

    def to_list_item(self, now=None):
        """Item de GET /tasks: inclui atraso e nomes de usuário/categoria."""
        data = self.to_dict_with_overdue(now)
        data['user_name'] = self.user.name if self.user else None
        data['category_name'] = self.category.name if self.category else None
        return data

    def to_user_task_item(self, now=None):
        """Item de GET /users/<id>/tasks (subconjunto de campos)."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'created_at': str(self.created_at),
            'due_date': str(self.due_date) if self.due_date else None,
            'overdue': self.is_overdue(now),
        }

    # ---- persistência --------------------------------------------------------

    def save(self):
        with transaction() as session:
            session.add(self)
        return self

    def delete(self):
        with transaction() as session:
            session.delete(self)

    # ---- consultas -----------------------------------------------------------

    @classmethod
    def get_by_id(cls, task_id):
        return db.session.get(cls, task_id)

    @classmethod
    def list_with_relations(cls):
        stmt = (select(cls)
                .options(joinedload(cls.user), joinedload(cls.category))
                .order_by(cls.id))
        return db.session.scalars(stmt).all()

    @classmethod
    def list_by_user(cls, user_id):
        return db.session.scalars(select(cls).where(cls.user_id == user_id).order_by(cls.id)).all()

    @classmethod
    def search(cls, text=None, status=None, priority=None, user_id=None):
        stmt = select(cls)
        if text:
            pattern = f'%{text}%'  # valor vai como parâmetro ligado, não na string SQL
            stmt = stmt.where(or_(cls.title.like(pattern), cls.description.like(pattern)))
        if status:
            stmt = stmt.where(cls.status == status)
        if priority is not None:
            stmt = stmt.where(cls.priority == priority)
        if user_id is not None:
            stmt = stmt.where(cls.user_id == user_id)
        return db.session.scalars(stmt.order_by(cls.id)).all()

    @classmethod
    def count_all(cls):
        return db.session.scalar(select(func.count(cls.id)))

    @classmethod
    def count_by_status(cls):
        rows = db.session.execute(select(cls.status, func.count(cls.id)).group_by(cls.status))
        return {status: count for status, count in rows}

    @classmethod
    def count_by_priority(cls):
        rows = db.session.execute(select(cls.priority, func.count(cls.id)).group_by(cls.priority))
        return {priority: count for priority, count in rows}

    @classmethod
    def _overdue_condition(cls, now):
        return (cls.due_date.is_not(None)) & (cls.due_date < now) & (cls.status.not_in(CLOSED_STATUSES))

    @classmethod
    def list_overdue(cls, now):
        return db.session.scalars(select(cls).where(cls._overdue_condition(now)).order_by(cls.id)).all()

    @classmethod
    def count_overdue(cls, now):
        return db.session.scalar(select(func.count(cls.id)).where(cls._overdue_condition(now)))

    @classmethod
    def count_created_since(cls, since):
        return db.session.scalar(select(func.count(cls.id)).where(cls.created_at >= since))

    @classmethod
    def count_done_updated_since(cls, since):
        return db.session.scalar(
            select(func.count(cls.id)).where(cls.status == STATUS_DONE, cls.updated_at >= since))

    @classmethod
    def count_by_user(cls):
        """{user_id: (total, concluídas)} numa única agregação."""
        done = func.sum(case((cls.status == STATUS_DONE, 1), else_=0))
        rows = db.session.execute(
            select(cls.user_id, func.count(cls.id), done)
            .where(cls.user_id.is_not(None))
            .group_by(cls.user_id))
        return {user_id: (total, completed or 0) for user_id, total, completed in rows}

    @classmethod
    def count_by_category(cls):
        rows = db.session.execute(
            select(cls.category_id, func.count(cls.id))
            .where(cls.category_id.is_not(None))
            .group_by(cls.category_id))
        return {category_id: count for category_id, count in rows}
