from sqlalchemy import func, select

from models.database import db, transaction
from models.task import Task
from utils.constants import ROLE_ADMIN, ROLE_USER
from utils.dates import utc_now
from utils.security import hash_password, is_legacy_hash, verify_password


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default=ROLE_USER)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        """Representação pública: nunca inclui o hash da senha."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at),
        }

    def set_password(self, raw_password):
        self.password = hash_password(raw_password)

    def check_password(self, raw_password):
        return verify_password(raw_password, self.password)

    def has_legacy_password_hash(self):
        return is_legacy_hash(self.password)

    def is_admin(self):
        return self.role == ROLE_ADMIN

    # ---- persistência --------------------------------------------------------

    def save(self):
        with transaction() as session:
            session.add(self)
        return self

    def delete_with_tasks(self):
        """Remove o usuário e suas tasks numa única transação."""
        with transaction() as session:
            for task in Task.list_by_user(self.id):
                session.delete(task)
            session.delete(self)

    # ---- consultas -----------------------------------------------------------

    @classmethod
    def get_by_id(cls, user_id):
        return db.session.get(cls, user_id)

    @classmethod
    def get_by_email(cls, email):
        return db.session.scalars(select(cls).where(cls.email == email)).first()

    @classmethod
    def list_all(cls):
        return db.session.scalars(select(cls).order_by(cls.id)).all()

    @classmethod
    def count_all(cls):
        return db.session.scalar(select(func.count(cls.id)))
