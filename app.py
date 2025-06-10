#!/usr/bin/env python3
"""
Flask Backend API for Children's Book Generator

This provides a web API interface for the book generation system.
"""

import sys
import os
from pathlib import Path
import json
import uuid
import threading
from typing import List, Dict, Any, Optional
from datetime import datetime
import dotenv

from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import base64

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import our modules
from src.character_processing import CharacterProcessor
from src.book_planning import BookPlanner
from src.content_generation import ImageGenerator, TextGenerator
from src.pdf_generation import PDFGenerator
from src.utils.config import load_config

dotenv.load_dotenv("secrets.env")

app = Flask(__name__)
CORS(app)

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Ensure upload folder exists
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

# Store ongoing generations
ongoing_generations = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the main frontend page."""
    return render_template('index.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve static assets from the assets directory."""
    return send_from_directory('assets', filename)

@app.route('/api/generate', methods=['POST'])
def generate_book():
    """Generate a children's book based on provided parameters."""
    try:
        data = request.get_json()
        
        # Generate unique ID for this generation
        generation_id = str(uuid.uuid4())
        
        # Store generation status
        ongoing_generations[generation_id] = {
            'status': 'starting',
            'progress': 0,
            'message': 'Initializing book generation...',
            'start_time': datetime.now().isoformat()
        }
        
        # Start generation in background thread
        generation_thread = threading.Thread(
            target=generate_book_async,
            args=(generation_id, data)
        )
        generation_thread.start()
        
        return jsonify({
            'success': True,
            'generation_id': generation_id,
            'message': 'Book generation started'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/status/<generation_id>')
def get_generation_status(generation_id):
    """Get the status of an ongoing book generation."""
    if generation_id not in ongoing_generations:
        return jsonify({
            'success': False,
            'error': 'Generation ID not found'
        }), 404
    
    return jsonify({
        'success': True,
        'status': ongoing_generations[generation_id]
    })

@app.route('/api/download/<generation_id>')
def download_book(generation_id):
    """Download the generated book PDF."""
    if generation_id not in ongoing_generations:
        return jsonify({
            'success': False,
            'error': 'Generation ID not found'
        }), 404
    
    generation_info = ongoing_generations[generation_id]
    
    if generation_info['status'] != 'completed':
        return jsonify({
            'success': False,
            'error': 'Book generation not completed yet'
        }), 400
    
    pdf_path = generation_info.get('pdf_path')
    if not pdf_path or not Path(pdf_path).exists():
        return jsonify({
            'success': False,
            'error': 'Generated book file not found'
        }), 404
    
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f"book_{generation_id}.pdf"
    )

def generate_book_async(generation_id: str, data: Dict[str, Any]):
    """Generate book asynchronously."""
    try:
        # Update status
        update_status(generation_id, 'processing', 10, 'Loading configuration...')
        
        # Load configuration
        config = load_config()
        
        # Initialize processors
        update_status(generation_id, 'processing', 15, 'Initializing AI clients...')
        character_processor = CharacterProcessor()
        book_planner = BookPlanner()
        image_generator = ImageGenerator()
        text_generator = TextGenerator()
        pdf_generator = PDFGenerator()
        
        # Extract parameters from request
        book_title = data.get('bookTitle', 'Untitled Book')
        story_idea = data.get('storyIdea', '')
        num_pages = int(data.get('numPages', 10))
        age_group = data.get('ageGroup', '4-7')
        language = data.get('language', 'English')
        art_style = data.get('artStyle', 'children\'s book illustration')
        characters_data = data.get('characters', [])
        themes = data.get('themes', [])
        
        # Process characters
        update_status(generation_id, 'processing', 25, f'Processing {len(characters_data)} characters...')
        
        processed_characters = character_processor.process_multiple_characters(characters_data)
        
        if not processed_characters:
            raise Exception("No characters were successfully processed")
        
        # Create book plan
        update_status(generation_id, 'processing', 40, 'Creating book plan and story structure...')
        
        book_plan = book_planner.create_book_plan(
            story_idea=story_idea,
            characters=processed_characters,
            num_pages=num_pages,
            age_group=age_group,
            language=language,
            book_title=book_title,
            themes=themes
        )
        
        # Generate images
        update_status(generation_id, 'processing', 60, 'Generating illustrations...')
        
        page_images = image_generator.generate_all_page_images(
            book_plan=book_plan,
            characters=processed_characters,
            art_style=art_style,
            include_cover=True
        )
        
        # Generate text content
        update_status(generation_id, 'processing', 80, 'Generating text content...')
        
        page_texts = text_generator.generate_all_page_texts(
            book_plan=book_plan,
            language=language
        )
        
        # Generate PDF
        update_status(generation_id, 'processing', 90, 'Assembling final PDF...')
        
        pdf_path = pdf_generator.create_book_pdf(
            book_plan=book_plan,
            page_images=page_images,
            page_texts=page_texts
        )
        
        # Complete
        update_status(generation_id, 'completed', 100, 'Book generation completed!', pdf_path)
        
    except Exception as e:
        update_status(generation_id, 'error', -1, f'Error: {str(e)}')

def update_status(generation_id: str, status: str, progress: int, message: str, pdf_path: Optional[str] = None):
    """Update the status of a generation."""
    if generation_id in ongoing_generations:
        ongoing_generations[generation_id].update({
            'status': status,
            'progress': progress,
            'message': message,
            'updated_time': datetime.now().isoformat()
        })
        
        if pdf_path:
            ongoing_generations[generation_id]['pdf_path'] = pdf_path

@app.route('/api/upload_character_image', methods=['POST'])
def upload_character_image():
    """Upload a character image."""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        file_path = Path(UPLOAD_FOLDER) / unique_filename
        file.save(file_path)
        
        return jsonify({
            'success': True,
            'filename': unique_filename,
            'message': 'Image uploaded successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 