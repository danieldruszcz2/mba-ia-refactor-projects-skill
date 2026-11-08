from models.database import db, transaction
from utils.constants import PRIVILEGED_ROLES, ROLE_ADMIN, ROLE_USER
from utils.dates import utcnow
from utils.security import hash_password, verify_password


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default=ROLE_USER)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        """Representação pública — nunca inclui o hash da senha."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at),
        }

    # ---- regras do registro -------------------------------------------------

    def set_password(self, password):
        self.password = hash_password(password)

    def check_password(self, password):
        """Verifica a senha; hashes legados (MD5) são atualizados para o algoritmo atual."""
        valid, needs_rehash = verify_password(self.password, password)
        if valid and needs_rehash:
            self.set_password(password)
            self.save()
        return valid

    def is_admin(self):
        return self.role == ROLE_ADMIN

    def has_privileged_role(self):
        return self.role in PRIVILEGED_ROLES

    # ---- consultas ----------------------------------------------------------

    @classmethod
    def get_by_id(cls, user_id):
        return db.session.get(cls, user_id)

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def list_all(cls):
        return cls.query.order_by(cls.id).all()

    @classmethod
    def count(cls):
        return cls.query.count()

    # ---- escrita ------------------------------------------------------------

    def save(self):
        with transaction() as session:
            session.add(self)
        return self

    def delete_with_tasks(self):
        """Remove o usuário e suas tasks numa única transação."""
        from models.task import Task
        with transaction() as session:
            Task.delete_by_user(self.id)
            session.delete(self)
