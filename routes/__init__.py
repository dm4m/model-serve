from .search import search_bp
from .novelty import novelty_bp
from .analysis import analysis_bp

def init_app(app):
    app.register_blueprint(search_bp)
    app.register_blueprint(novelty_bp)
    app.register_blueprint(analysis_bp)