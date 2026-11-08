from routes.category_routes import category_bp
from routes.main_routes import main_bp
from routes.report_routes import report_bp
from routes.task_routes import task_bp
from routes.user_routes import user_bp

ALL_BLUEPRINTS = (main_bp, task_bp, user_bp, report_bp, category_bp)
