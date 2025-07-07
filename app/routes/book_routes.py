"""
Book Generation Routes
Handles book cover generation and serving cover images
"""

import uuid
import json
from pathlib import Path
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file, redirect
from werkzeug.utils import secure_filename

# Import services
from app.services.book_generation_service import BookGenerationService
from app.services.storage_service import CloudStorageService

book_bp = Blueprint('book', __name__, url_prefix='/api')

@book_bp.route('/generate', methods=['POST'])
def generate_cover():
    """Generate only the book cover and store order information."""
    try:
        data = request.get_json()
        
        # Generate unique ID for this order
        order_id = str(uuid.uuid4())
        
        # Extract parameters from request
        book_title = data.get('bookTitle', 'Untitled Book')
        story_idea = data.get('storyIdea', '')
        num_pages = int(data.get('numPages', 10))
        age_group = data.get('ageGroup', '4-7')
        language = data.get('language', 'English')
        art_style = data.get('artStyle', 'children\'s book illustration')
        characters_data = data.get('characters', [])
        themes = data.get('themes', [])
        customer_email = data.get('customerEmail', '')
        customer_name = data.get('customerName', '')
        
        # Validate required fields
        if not book_title or not story_idea or not customer_email:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: book title, story idea, and customer email are required'
            }), 400
        
        # Use the book generation service
        book_service = BookGenerationService()
        
        try:
            # Generate cover and save order
            result = book_service.generate_cover_and_save_order(
                order_id=order_id,
                book_title=book_title,
                story_idea=story_idea,
                num_pages=num_pages,
                age_group=age_group,
                language=language,
                art_style=art_style,
                characters_data=characters_data,
                themes=themes,
                customer_email=customer_email,
                customer_name=customer_name
            )
            
            # Note: Email notifications are sent AFTER payment completion, not here
            
            return jsonify({
                'success': True,
                'order_id': order_id,
                'cover_url': f'/api/cover/{order_id}',
                'message': 'Book cover generated successfully! Please proceed to payment to receive your full book.'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to generate cover: {str(e)}'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@book_bp.route('/cover/<order_id>')
def get_cover(order_id):
    """Serve the generated cover image from Cloud Storage."""
    try:
        storage_service = CloudStorageService()
        cloud_file_path = f"covers/cover_{order_id}.png"
        
        print(f"Attempting to serve cover from Cloud Storage: {cloud_file_path}")
        
        # Check if file exists in Cloud Storage
        if not storage_service.file_exists(cloud_file_path):
            print(f"Cover not found in Cloud Storage for order_id: {order_id}")
            return jsonify({
                'success': False,
                'error': f'Cover not found for order {order_id}'
            }), 404
        
        # Get public URL and redirect to it
        public_url = storage_service.get_public_url(cloud_file_path)
        print(f"Redirecting to public URL: {public_url}")
        return redirect(public_url)
        
    except Exception as e:
        print(f"Error serving cover: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error serving cover: {str(e)}'
        }), 500 