"""Constantes de domínio."""

TASK_STATUS_PENDING = 'pending'
TASK_STATUS_IN_PROGRESS = 'in_progress'
TASK_STATUS_DONE = 'done'
TASK_STATUS_CANCELLED = 'cancelled'
TASK_STATUSES = (TASK_STATUS_PENDING, TASK_STATUS_IN_PROGRESS, TASK_STATUS_DONE, TASK_STATUS_CANCELLED)
# Tasks nesses status nunca são consideradas atrasadas.
TASK_CLOSED_STATUSES = (TASK_STATUS_DONE, TASK_STATUS_CANCELLED)

MIN_PRIORITY = 1
MAX_PRIORITY = 5
DEFAULT_PRIORITY = 3
# Prioridades <= este valor contam como "alta prioridade" no relatório por usuário.
HIGH_PRIORITY_THRESHOLD = 2
PRIORITY_LABELS = {1: 'critical', 2: 'high', 3: 'medium', 4: 'low', 5: 'minimal'}

MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 200

ROLE_USER = 'user'
ROLE_ADMIN = 'admin'
ROLE_MANAGER = 'manager'
USER_ROLES = (ROLE_USER, ROLE_ADMIN, ROLE_MANAGER)
# Atribuir ou alterar estes roles exige um administrador autenticado.
PRIVILEGED_ROLES = (ROLE_ADMIN, ROLE_MANAGER)

MIN_PASSWORD_LENGTH = 4
EMAIL_PATTERN = r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$'

DEFAULT_CATEGORY_COLOR = '#000000'

DATE_FORMAT = '%Y-%m-%d'
RECENT_ACTIVITY_DAYS = 7
