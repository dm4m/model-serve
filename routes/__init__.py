from .search import search_bp


def init_app(app):
    app.register_blueprint(search_bp)