"""
Asset Routes
Handles serving static assets, templates, and TOS files
"""

from flask import Blueprint, render_template, send_from_directory, redirect, request, send_file
from app.services.storage_service import CloudStorageService

asset_bp = Blueprint('assets', __name__)

# Initialize Cloud Storage service
storage_service = CloudStorageService()

@asset_bp.route('/')
def index():
    """Serve the main frontend page."""
    return render_template('index.html')

@asset_bp.route('/static/assets/<path:filename>')
def serve_assets(filename):
    """Serve static assets from the assets directory."""
    return send_from_directory('static/assets', filename)

@asset_bp.route('/assets/<path:filename>')
def serve_assets_alt(filename):
    """Alternative asset route for compatibility."""
    return send_from_directory('static/assets', filename)

@asset_bp.route('/tos/<path:filename>')
def serve_tos(filename):
    """Serve Terms of Service files from the tos directory."""
    return send_from_directory('tos', filename)

@asset_bp.route('/api/cover/<order_id>')
def serve_cover(order_id):
    """Serve book cover from Cloud Storage."""
    try:
        cloud_path = f"covers/cover_{order_id}.png"
        
        if not storage_service.file_exists(cloud_path):
            return {'error': 'Cover not found'}, 404
        
        # Download to temporary file and serve it
        temp_file_path = storage_service.download_file_to_temp(cloud_path)
        
        return send_file(
            temp_file_path,
            mimetype='image/png',
            as_attachment=False,
            download_name=f"cover_{order_id}.png"
        )
        
    except Exception as e:
        print(f"Error serving cover {order_id}: {str(e)}")
        return {'error': 'Failed to serve cover'}, 500

@asset_bp.route('/success')
def payment_success():
    """Handle successful payment redirect."""
    from config.stripe_config import stripe_config
    
    session_id = request.args.get('session_id')
    order_id = request.args.get('order_id')
    
    if not session_id or not order_id:
        return redirect('/?error=missing_params')
    
    try:
        # Verify the session
        session_data = stripe_config.retrieve_session(session_id)
        
        if session_data['payment_status'] == 'paid':
            return render_template('success.html', 
                                 order_id=order_id, 
                                 session_id=session_id,
                                 amount=stripe_config.format_amount(session_data['amount_total']))
        else:
            return redirect('/?error=payment_not_completed')
            
    except Exception as e:
        print(f"Error verifying payment: {str(e)}")
        return redirect('/?error=verification_failed') 