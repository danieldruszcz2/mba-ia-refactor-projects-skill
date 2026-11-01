"""Script para popular o banco com dados iniciais (apaga os dados existentes)."""
from datetime import timedelta

from sqlalchemy import delete

from app import create_app
from models import Category, Task, User
from models.database import transaction
from utils.constants import (
    ROLE_ADMIN, ROLE_MANAGER, ROLE_USER, STATUS_CANCELLED, STATUS_DONE, STATUS_IN_PROGRESS,
    STATUS_PENDING,
)
from utils.dates import utc_now

# Credenciais apenas para desenvolvimento local (as senhas são gravadas com hash).
SEED_USERS = [
    {'name': 'João Silva', 'email': 'joao@email.com', 'password': '1234', 'role': ROLE_ADMIN},
    {'name': 'Maria Santos', 'email': 'maria@email.com', 'password': 'abcd', 'role': ROLE_USER},
    {'name': 'Pedro Oliveira', 'email': 'pedro@email.com', 'password': 'pass', 'role': ROLE_MANAGER},
]

SEED_CATEGORIES = [
    {'name': 'Backend', 'description': 'Tarefas de backend', 'color': '#3498db'},
    {'name': 'Frontend', 'description': 'Tarefas de frontend', 'color': '#2ecc71'},
    {'name': 'DevOps', 'description': 'Tarefas de infraestrutura', 'color': '#e74c3c'},
    {'name': 'Bug', 'description': 'Correção de bugs', 'color': '#e67e22'},
]


def _seed_tasks(users, categories):
    joao, maria, pedro = users
    backend, frontend, devops, bug = categories
    now = utc_now()
    return [
        {'title': 'Implementar autenticação JWT', 'description': 'Adicionar autenticação real com JWT', 'status': STATUS_PENDING, 'priority': 1, 'user': joao, 'category': backend, 'due_date': now - timedelta(days=3)},
        {'title': 'Criar tela de login', 'description': 'Tela de login responsiva', 'status': STATUS_IN_PROGRESS, 'priority': 2, 'user': maria, 'category': frontend, 'due_date': now + timedelta(days=5)},
        {'title': 'Configurar CI/CD', 'description': 'Pipeline com GitHub Actions', 'status': STATUS_DONE, 'priority': 2, 'user': pedro, 'category': devops, 'tags': 'devops,ci,github'},
        {'title': 'Corrigir bug no filtro de busca', 'description': 'Filtro não funciona com caracteres especiais', 'status': STATUS_PENDING, 'priority': 1, 'user': joao, 'category': bug, 'due_date': now - timedelta(days=1)},
        {'title': 'Adicionar paginação na API', 'description': 'Endpoints retornam todos os registros', 'status': STATUS_PENDING, 'priority': 3, 'user': joao, 'category': backend, 'due_date': now + timedelta(days=10)},
        {'title': 'Escrever testes unitários', 'description': 'Cobertura mínima de 80%', 'status': STATUS_PENDING, 'priority': 2, 'user': maria, 'category': backend},
        {'title': 'Documentar API com Swagger', 'description': 'Gerar documentação automática', 'status': STATUS_CANCELLED, 'priority': 4, 'user': pedro, 'category': backend},
        {'title': 'Refatorar models', 'description': 'Melhorar organização dos models', 'status': STATUS_IN_PROGRESS, 'priority': 3, 'user': maria, 'category': backend, 'tags': 'refactor,tech-debt'},
        {'title': 'Configurar monitoramento', 'description': 'Prometheus + Grafana', 'status': STATUS_PENDING, 'priority': 4, 'user': pedro, 'category': devops, 'due_date': now + timedelta(days=20)},
        {'title': 'Melhorar validações de input', 'description': 'Usar marshmallow ou pydantic', 'status': STATUS_PENDING, 'priority': 3, 'user': joao, 'category': backend, 'tags': 'improvement,validation'},
    ]


def seed_data(app):
    with app.app_context():
        with transaction() as session:
            session.execute(delete(Task))
            session.execute(delete(User))
            session.execute(delete(Category))

        with transaction() as session:
            users = []
            for user_data in SEED_USERS:
                user = User(name=user_data['name'], email=user_data['email'], role=user_data['role'])
                user.set_password(user_data['password'])
                users.append(user)
            categories = [Category(**category_data) for category_data in SEED_CATEGORIES]
            session.add_all(users + categories)
            session.flush()  # gera os ids usados pelas tasks

            for task_data in _seed_tasks(users, categories):
                session.add(Task(
                    title=task_data['title'],
                    description=task_data['description'],
                    status=task_data['status'],
                    priority=task_data['priority'],
                    user_id=task_data['user'].id,
                    category_id=task_data['category'].id,
                    due_date=task_data.get('due_date'),
                    tags=task_data.get('tags'),
                ))

        print('Seed concluído com sucesso!')
        print(f'  {User.count_all()} usuários')
        print(f'  {Category.count_all()} categorias')
        print(f'  {Task.count_all()} tasks')


if __name__ == '__main__':
    seed_data(create_app())
