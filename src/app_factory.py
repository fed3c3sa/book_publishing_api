"""
Flask application factory for the Children's Book Generator.

This module provides a factory function for creating Flask applications
with proper dependency injection and service configuration.
"""

from flask import Flask
from flask_cors import CORS

from .api.routes import create_api_blueprint
from .services.dependency_container import DependencyContainer
from .exceptions import BookGeneratorError


def create_app() -> Flask:
    """
    Create and configure the Flask application.
    
    Returns:
        Configured Flask application instance
    """
    from .utils.config import PROJECT_ROOT
    
    # Configure Flask with proper template and static directories
    app = Flask(
        __name__,
        template_folder=str(PROJECT_ROOT / "templates"),
        static_folder=str(PROJECT_ROOT / "assets"),
        static_url_path="/assets"
    )
    CORS(app)
    
    # Configure upload settings
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Initialize dependency container
    container = DependencyContainer()
    
    # Store container in app for access in routes
    app.container = container
    
    # Register API blueprint
    api_blueprint = create_api_blueprint(container)
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    # Register static routes
    register_static_routes(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app


def register_static_routes(app: Flask) -> None:
    """Register static file routes."""
    from flask import render_template, send_from_directory
    from .utils.config import PROJECT_ROOT
    
    @app.route('/')
    def index():
        """Serve the main frontend page."""
        return render_template('index.html')
    
    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        """Serve static assets from the assets directory."""
        assets_dir = PROJECT_ROOT / "assets"
        return send_from_directory(str(assets_dir), filename)


def register_error_handlers(app: Flask) -> None:
    """Register error handlers for the application."""
    from flask import jsonify
    
    @app.errorhandler(BookGeneratorError)
    def handle_book_generator_error(error: BookGeneratorError):
        """Handle custom book generator errors."""
        response = {
            'success': False,
            'error': error.message,
            'error_code': error.error_code,
            'details': error.details
        }
        return jsonify(response), 400
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors."""
        return jsonify({
            'success': False,
            'error': 'Resource not found',
            'error_code': 'NOT_FOUND'
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 errors."""
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'error_code': 'INTERNAL_ERROR'
        }), 500