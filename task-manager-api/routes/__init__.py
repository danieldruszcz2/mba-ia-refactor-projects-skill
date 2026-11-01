from flask import jsonify


def respond(result):
    """Converte o retorno (dados, status) de um controller em resposta JSON."""
    data, status = result
    return jsonify(data), status


def register_routes(app):
    from routes.category_routes import category_bp
    from routes.main_routes import main_bp
    from routes.report_routes import report_bp
    from routes.task_routes import task_bp
    from routes.user_routes import user_bp

    for blueprint in (main_bp, task_bp, user_bp, report_bp, category_bp):
        app.register_blueprint(blueprint)
