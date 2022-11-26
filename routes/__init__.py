from .search import search_bp
from .analysis import analysis_bp

def init_app(app):
    app.register_blueprint(search_bp)
    app.register_blueprint(analysis_bp)