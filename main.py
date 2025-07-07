#!/usr/bin/env python3
"""
Book Publishing API - Production Version
A Flask application for generating children's book covers and handling payments.
"""

import os
import sys
from pathlib import Path
import dotenv
from flask import Flask
from flask_cors import CORS

# Load environment variables
dotenv.load_dotenv("secrets.env")

# Add current directory to Python path for imports
current_dir = str(Path(__file__).parent)
sys.path.insert(0, current_dir)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure Flask
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    
    # Enable CORS
    CORS(app)
    
    # Ensure required directories exist (only in local development)
    # Skip on App Engine where filesystem is read-only
    # Check multiple App Engine environment indicators
    is_app_engine = (
        os.getenv('GAE_ENV') == 'standard' or 
        os.getenv('GAE_APPLICATION') or 
        os.getenv('GOOGLE_CLOUD_PROJECT') or
        os.path.exists('/srv')
    )
    
    if not is_app_engine:
        required_dirs = [
            'temp_uploads',
            'static/assets',
            'templates',
            'tos'
        ]
        
        for dir_path in required_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Register blueprints
    from app.routes.asset_routes import asset_bp
    from app.routes.book_routes import book_bp
    from app.routes.payment_routes import payment_bp
    from app.routes.upload_routes import upload_bp
    
    app.register_blueprint(asset_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(upload_bp)
    
    @app.route('/health')
    def health_check():
        """Health check endpoint for App Engine"""
        return {'status': 'healthy', 'service': 'book_publishing_api'}, 200
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        return {'error': 'Internal server error'}, 500
    
    return app

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Run the application
    debug_mode = os.getenv('ENVIRONMENT', 'local').lower() != 'production'
    port = int(os.getenv('PORT', 5001))
    
    print(f"Starting Book Publishing API on port {port}")
    print(f"Debug mode: {debug_mode}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'local')}")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port) 