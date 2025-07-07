"""
Upload Routes
Handles file uploads for character images
"""

import tempfile
from pathlib import Path
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from app.services.storage_service import CloudStorageService

upload_bp = Blueprint('upload', __name__, url_prefix='/api')

# Upload configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Initialize Cloud Storage service
storage_service = CloudStorageService()

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload_character_image', methods=['POST'])
def upload_character_image():
    """Upload a character image to Cloud Storage."""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        
        # Upload to Cloud Storage
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        cloud_path = f"uploads/{unique_filename}"
        
        # Upload file data to Cloud Storage
        file.seek(0)  # Reset file pointer
        cloud_url = storage_service.upload_file_from_memory(
            file_data=file,
            cloud_file_path=cloud_path,
            content_type=file.content_type
        )
        
        return jsonify({
            'success': True,
            'filename': unique_filename,
            'cloud_path': cloud_path,
            'cloud_url': cloud_url,
            'message': 'Image uploaded successfully to Cloud Storage'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500 