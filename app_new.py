#!/usr/bin/env python3
"""
Modular Flask Backend API for Children's Book Generator

This is the new, restructured version of the Flask app that uses
the modular architecture with dependency injection and proper separation of concerns.
"""

import os
import sys
from pathlib import Path
from flask import Flask
from flask_cors import CORS

# Project root directory
PROJECT_ROOT = Path(__file__).parent

# Add src directory to Python path
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Load environment variables
import dotenv
dotenv.load_dotenv("secrets.env")


def create_app_direct() -> Flask:
    """Create Flask app directly with correct paths."""
    from src.api.routes import create_api_blueprint
    from src.services.dependency_container import DependencyContainer
    from src.exceptions import BookGeneratorError
    from flask import render_template, send_from_directory, jsonify
    
    # Create Flask app with correct paths
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
    app.container = container
    
    # Register API blueprint
    api_blueprint = create_api_blueprint(container)
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    # Register static routes
    @app.route('/')
    def index():
        """Serve the main frontend page."""
        return render_template('index.html')
    
    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        """Serve static assets from the assets directory."""
        return send_from_directory(str(PROJECT_ROOT / "assets"), filename)
    
    # Register error handlers
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
    
    return app


def main():
    """Main entry point for the application."""
    app = create_app_direct()
    
    # Get configuration from environment
    debug = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 'yes')
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    
    print(f"Starting Children's Book Generator API...")
    print(f"Template folder: {app.template_folder}")
    print(f"Static folder: {app.static_folder}")
    print(f"Templates exist: {Path(app.template_folder).exists()}")
    print(f"Debug mode: {debug}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    
    app.run(debug=debug, host=host, port=port)


if __name__ == '__main__':
    main()