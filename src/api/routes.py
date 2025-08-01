"""
Flask API routes for the Children's Book Generator.

This module defines all the REST API endpoints using the new modular services
and workflow orchestration system.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename

from ..domain.models import GenerationRequest, CharacterInput, InputType, CharacterType
from ..services.dependency_container import DependencyContainer
from ..exceptions import BookGeneratorError, ValidationError, ResourceNotFoundError
from ..utils.config import PROJECT_ROOT


def create_api_blueprint(container: DependencyContainer) -> Blueprint:
    """
    Create the API blueprint with dependency injection.
    
    Args:
        container: Dependency container with all services
        
    Returns:
        Configured Flask blueprint
    """
    api = Blueprint('api', __name__)
    
    # Upload settings
    UPLOAD_FOLDER = PROJECT_ROOT / 'temp_uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    
    def allowed_file(filename: str) -> bool:
        """Check if file extension is allowed."""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    @api.route('/generate', methods=['POST'])
    def generate_book():
        """Generate a children's book based on provided parameters."""
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data:
                raise ValidationError("Request body is required")
            
            if not data.get('bookTitle'):
                raise ValidationError("Book title is required", field="bookTitle")
            
            if not data.get('storyIdea'):
                raise ValidationError("Story idea is required", field="storyIdea")
            
            if not data.get('characters'):
                raise ValidationError("At least one character is required", field="characters")
            
            # Parse character inputs
            character_inputs = []
            for char_data in data.get('characters', []):
                # Determine input type
                if char_data.get('type') == 'image' or 'image_path' in char_data:
                    input_type = InputType.IMAGE
                    content = char_data.get('content', [])
                    if isinstance(content, str):
                        content = [content]
                else:
                    input_type = InputType.TEXT
                    content = char_data.get('content', char_data.get('description', ''))
                
                # Parse character type
                char_type = CharacterType.MAIN
                if char_data.get('character_type'):
                    char_type_str = char_data['character_type']
                    # Handle both string values and enum values
                    if isinstance(char_type_str, str):
                        try:
                            char_type = CharacterType(char_type_str.lower())
                        except ValueError:
                            char_type = CharacterType.MAIN
                    else:
                        char_type = CharacterType.MAIN
                
                character_input = CharacterInput(
                    type=input_type,
                    content=content,
                    name=char_data.get('name', ''),
                    character_type=char_type,
                    additional_description=char_data.get('additional_description', '')
                )
                character_inputs.append(character_input)
            
            # Create generation request
            generation_request = GenerationRequest(
                book_title=data['bookTitle'],
                story_idea=data['storyIdea'],
                num_pages=int(data.get('numPages', 10)),
                age_group=data.get('ageGroup', '4-7'),
                language=data.get('language', 'English'),
                art_style=data.get('artStyle', "children's book illustration"),
                characters=character_inputs,
                themes=data.get('themes', []),
                cover_image_path=data.get('coverImage')
            )
            
            # Start generation workflow
            workflow_manager = container.workflow_manager
            generation_id = workflow_manager.start_generation(generation_request)
            
            return jsonify({
                'success': True,
                'generation_id': generation_id,
                'message': 'Book generation started'
            })
            
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': e.message,
                'field': e.field
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @api.route('/status/<generation_id>')
    def get_generation_status(generation_id: str):
        """Get the status of an ongoing book generation."""
        try:
            workflow_manager = container.workflow_manager
            context = workflow_manager.get_workflow_status(generation_id)
            
            return jsonify({
                'success': True,
                'status': context.get_summary()
            })
            
        except ResourceNotFoundError as e:
            return jsonify({
                'success': False,
                'error': e.message
            }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @api.route('/download/<generation_id>')
    def download_book(generation_id: str):
        """Download the generated book PDF."""
        try:
            workflow_manager = container.workflow_manager
            context = workflow_manager.get_workflow_status(generation_id)
            
            if not context.is_completed():
                return jsonify({
                    'success': False,
                    'error': 'Book generation not completed yet'
                }), 400
            
            if not context.pdf_path or not Path(context.pdf_path).exists():
                return jsonify({
                    'success': False,
                    'error': 'Generated book file not found'
                }), 404
            
            return send_file(
                context.pdf_path,
                as_attachment=True,
                download_name=f"book_{generation_id}.pdf"
            )
            
        except ResourceNotFoundError as e:
            return jsonify({
                'success': False,
                'error': e.message
            }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @api.route('/upload_character_image', methods=['POST'])
    def upload_character_image():
        """Upload a character image."""
        try:
            if 'image' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'No image file provided'
                }), 400
            
            file = request.files['image']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No file selected'
                }), 400
            
            if not allowed_file(file.filename):
                return jsonify({
                    'success': False,
                    'error': 'Invalid file type'
                }), 400
            
            # Save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{filename}"
            file_path = UPLOAD_FOLDER / unique_filename
            file.save(file_path)
            
            return jsonify({
                'success': True,
                'filename': unique_filename,
                'message': 'Image uploaded successfully'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @api.route('/upload_cover_image', methods=['POST'])
    def upload_cover_image():
        """Upload a book cover image."""
        try:
            if 'image' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'No image file provided'
                }), 400
            
            file = request.files['image']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No file selected'
                }), 400
            
            if not allowed_file(file.filename):
                return jsonify({
                    'success': False,
                    'error': 'Invalid file type'
                }), 400
            
            # Save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"cover_{timestamp}_{filename}"
            file_path = UPLOAD_FOLDER / unique_filename
            file.save(file_path)
            
            return jsonify({
                'success': True,
                'filename': unique_filename,
                'message': 'Cover image uploaded successfully'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @api.route('/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'success': True,
            'message': 'Children\'s Book Generator API is running',
            'timestamp': datetime.now().isoformat()
        })
    
    return api