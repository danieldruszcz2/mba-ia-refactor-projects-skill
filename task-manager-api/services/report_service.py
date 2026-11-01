"""Regras de agregação dos relatórios (envolvem tasks, usuários e categorias)."""
from datetime import timedelta

from models import Category, Task, User
from utils.constants import (
    HIGH_PRIORITY_MAX, PRIORITY_LABELS, RECENT_ACTIVITY_DAYS, STATUS_CANCELLED, STATUS_DONE,
    STATUS_IN_PROGRESS, STATUS_PENDING, TASK_STATUSES,
)
from utils.dates import utc_now
from utils.stats import calculate_percentage


def build_summary():
    now = utc_now()
    recent_since = now - timedelta(days=RECENT_ACTIVITY_DAYS)
    tasks_by_status = Task.count_by_status()
    tasks_by_priority = Task.count_by_priority()
    overdue_tasks = Task.list_overdue(now)
    totals_by_user = Task.count_by_user()

    user_productivity = []
    for user in User.list_all():
        total, completed = totals_by_user.get(user.id, (0, 0))
        user_productivity.append({
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': calculate_percentage(completed, total),
        })

    return {
        'generated_at': str(now),
        'overview': {
            'total_tasks': Task.count_all(),
            'total_users': User.count_all(),
            'total_categories': Category.count_all(),
        },
        'tasks_by_status': {status: tasks_by_status.get(status, 0) for status in TASK_STATUSES},
        'tasks_by_priority': {
            label: tasks_by_priority.get(priority, 0) for priority, label in PRIORITY_LABELS.items()
        },
        'overdue': {
            'count': len(overdue_tasks),
            'tasks': [
                {
                    'id': task.id,
                    'title': task.title,
                    'due_date': str(task.due_date),
                    'days_overdue': (now - task.due_date).days,
                }
                for task in overdue_tasks
            ],
        },
        'recent_activity': {
            'tasks_created_last_7_days': Task.count_created_since(recent_since),
            'tasks_completed_last_7_days': Task.count_done_updated_since(recent_since),
        },
        'user_productivity': user_productivity,
    }


def build_user_report(user):
    now = utc_now()
    tasks = Task.list_by_user(user.id)
    status_counts = {status: 0 for status in TASK_STATUSES}
    overdue_count = 0
    high_priority_count = 0

    for task in tasks:
        if task.status in status_counts:
            status_counts[task.status] += 1
        if task.priority is not None and task.priority <= HIGH_PRIORITY_MAX:
            high_priority_count += 1
        if task.is_overdue(now):
            overdue_count += 1

    total = len(tasks)
    return {
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        },
        'statistics': {
            'total_tasks': total,
            'done': status_counts[STATUS_DONE],
            'pending': status_counts[STATUS_PENDING],
            'in_progress': status_counts[STATUS_IN_PROGRESS],
            'cancelled': status_counts[STATUS_CANCELLED],
            'overdue': overdue_count,
            'high_priority': high_priority_count,
            'completion_rate': calculate_percentage(status_counts[STATUS_DONE], total),
        },
    }
