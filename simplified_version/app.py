#!/usr/bin/env python3
"""
Simplified Flask Backend API for Children's Book Generator

This version only generates book covers and handles email workflow.
Users pay to receive the full book via email within 12 hours.
"""

import sys
import os
from pathlib import Path
import json
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, Optional
from datetime import datetime
import dotenv

from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import base64

# Add src directory to Python path
parent_dir = str(Path(__file__).parent.parent)
src_dir = str(Path(__file__).parent.parent / "src")
sys.path.insert(0, parent_dir)
sys.path.insert(0, src_dir)

# Import only what we need for cover generation
try:
    from src.character_processing import CharacterProcessor
    from src.book_planning import BookPlanner
    from src.content_generation import ImageGenerator
    from src.utils.config import load_config
except ImportError as e:
    print(f"Warning: Could not import from src directory: {e}")
    print("Make sure you're running this from the book_publishing_api directory")
    print("Or copy the src directory to the simplified_version folder")
    sys.exit(1)

dotenv.load_dotenv("secrets.env")

app = Flask(__name__)
CORS(app)

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = Path(__file__).parent / 'temp_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Ensure upload folder exists
UPLOAD_FOLDER.mkdir(exist_ok=True)
app_dir = Path(__file__).parent
(app_dir / 'output' / 'covers').mkdir(parents=True, exist_ok=True)
(app_dir / 'output' / 'orders').mkdir(parents=True, exist_ok=True)

# Email configuration
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@yourbookcompany.com')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_USER = os.getenv('EMAIL_USER', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')

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

@app.route('/tos/<path:filename>')
def serve_tos(filename):
    """Serve Terms of Service files from the tos directory."""
    return send_from_directory('tos', filename)

@app.route('/api/generate', methods=['POST'])
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
        
        # Load configuration
        config = load_config()
        
        # Initialize processors (only what we need for cover)
        character_processor = CharacterProcessor()
        book_planner = BookPlanner()
        image_generator = ImageGenerator()
        
        # Process characters
        processed_characters = []
        if characters_data:
            processed_characters = character_processor.process_multiple_characters(characters_data)
        
        # Create a minimal book plan (just for cover generation)
        book_plan = book_planner.create_book_plan(
            story_idea=story_idea,
            characters=processed_characters,
            num_pages=num_pages,
            age_group=age_group,
            language=language,
            book_title=book_title,
            themes=themes
        )
        
        # Generate only the cover image
        try:
            cover_image_path = image_generator.generate_book_cover(
                book_plan=book_plan,
                characters=processed_characters,
                art_style=art_style
            )
            print(f"Cover generated at: {cover_image_path}")
        except Exception as e:
            print(f"Error generating cover: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Failed to generate cover: {str(e)}'
            }), 500
        
        # Save the cover to our output directory
        cover_filename = f"cover_{order_id}.png"
        final_cover_path = Path(__file__).parent / 'output' / 'covers' / cover_filename
        
        # Copy the generated cover to our output directory
        import shutil
        try:
            if not Path(cover_image_path).exists():
                print(f"Source cover file does not exist: {cover_image_path}")
                return jsonify({
                    'success': False,
                    'error': 'Generated cover file not found'
                }), 500
            
            shutil.copy2(cover_image_path, final_cover_path)
            print(f"Cover copied to: {final_cover_path}")
            
            # Verify the copy was successful
            if not final_cover_path.exists():
                return jsonify({
                    'success': False,
                    'error': 'Failed to save cover file'
                }), 500
                
        except Exception as e:
            print(f"Error copying cover: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Failed to save cover: {str(e)}'
            }), 500
        
        # Store order information
        order_data = {
            'order_id': order_id,
            'customer_name': customer_name,
            'customer_email': customer_email,
            'book_title': book_title,
            'story_idea': story_idea,
            'num_pages': num_pages,
            'age_group': age_group,
            'language': language,
            'art_style': art_style,
            'characters': characters_data,
            'themes': themes,
            'cover_path': str(final_cover_path),
            'order_date': datetime.now().isoformat(),
            'status': 'cover_generated',
            'payment_status': 'pending'
        }
        
        # Save order to JSON file
        order_file_path = Path(__file__).parent / 'output' / 'orders' / f"order_{order_id}.json"
        with open(order_file_path, 'w', encoding='utf-8') as f:
            json.dump(order_data, f, indent=2, ensure_ascii=False)
        
        # Send notification email to admin
        send_admin_notification(order_data)
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'cover_url': f'/api/cover/{order_id}',
            'message': 'Book cover generated successfully! Please proceed to payment to receive your full book.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cover/<order_id>')
def get_cover(order_id):
    """Serve the generated cover image."""
    cover_path = Path(__file__).parent / 'output' / 'covers' / f"cover_{order_id}.png"
    
    print(f"Attempting to serve cover: {cover_path}")
    print(f"Cover exists: {cover_path.exists()}")
    
    if not cover_path.exists():
        print(f"Cover not found for order_id: {order_id}")
        return jsonify({
            'success': False,
            'error': f'Cover not found for order {order_id}'
        }), 404
    
    try:
        return send_file(cover_path, mimetype='image/png')
    except Exception as e:
        print(f"Error serving cover: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error serving cover: {str(e)}'
        }), 500

@app.route('/api/payment', methods=['POST'])
def process_payment():
    """Handle payment processing (simplified - just marks as paid)."""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        payment_method = data.get('payment_method', 'credit_card')
        
        if not order_id:
            return jsonify({
                'success': False,
                'error': 'Order ID is required'
            }), 400
        
        # Load order data
        order_file_path = Path(__file__).parent / 'output' / 'orders' / f"order_{order_id}.json"
        if not order_file_path.exists():
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404
        
        with open(order_file_path, 'r', encoding='utf-8') as f:
            order_data = json.load(f)
        
        # Update payment status
        order_data['payment_status'] = 'paid'
        order_data['payment_date'] = datetime.now().isoformat()
        order_data['payment_method'] = payment_method
        order_data['status'] = 'paid_awaiting_production'
        
        # Save updated order
        with open(order_file_path, 'w', encoding='utf-8') as f:
            json.dump(order_data, f, indent=2, ensure_ascii=False)
        
        # Send confirmation email to customer
        send_customer_confirmation(order_data)
        
        # Send production notification to admin
        send_production_notification(order_data)
        
        return jsonify({
            'success': True,
            'message': 'Payment processed successfully! You will receive your complete book via email within 12 hours.',
            'order_id': order_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
        file_path = UPLOAD_FOLDER / unique_filename
        file.save(str(file_path))
        
        return jsonify({
            'success': True,
            'filename': unique_filename,
            'message': 'Image uploaded successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def send_admin_notification(order_data: Dict[str, Any]):
    """Send notification email to admin about new order."""
    try:
        if not EMAIL_USER or not EMAIL_PASSWORD:
            print("Email credentials not configured, skipping admin notification")
            return
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = f"New Book Order - {order_data['book_title']}"
        
        body = f"""
New book order received:

Order ID: {order_data['order_id']}
Customer: {order_data['customer_name']} ({order_data['customer_email']})
Book Title: {order_data['book_title']}
Pages: {order_data['num_pages']}
Age Group: {order_data['age_group']}
Language: {order_data['language']}

Story Idea:
{order_data['story_idea']}

Characters: {len(order_data['characters'])} characters defined

Order Date: {order_data['order_date']}
Status: Cover generated, awaiting payment

Please review the order details in the system.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, ADMIN_EMAIL, text)
        server.quit()
        
        print(f"Admin notification sent for order {order_data['order_id']}")
        
    except Exception as e:
        print(f"Failed to send admin notification: {str(e)}")

def send_customer_confirmation(order_data: Dict[str, Any]):
    """Send payment confirmation email to customer."""
    try:
        if not EMAIL_USER or not EMAIL_PASSWORD:
            print("Email credentials not configured, skipping customer confirmation")
            return
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = order_data['customer_email']
        msg['Subject'] = f"Payment Confirmed - Your Book '{order_data['book_title']}' is in Production!"
        
        body = f"""
Dear {order_data['customer_name']},

Thank you for your payment! We're excited to create your personalized children's book.

Order Details:
- Book Title: {order_data['book_title']}
- Order ID: {order_data['order_id']}
- Pages: {order_data['num_pages']}
- Age Group: {order_data['age_group']}

What happens next:
✅ Payment confirmed
✅ Our expert writers and illustrators are now reviewing your story
📚 Your complete book will be professionally crafted
📧 You'll receive your finished book via email within 12 hours

Our team of children's book experts will carefully review and enhance your story to ensure it's perfectly tailored for your target age group, with engaging illustrations and age-appropriate language.

If you have any questions, please don't hesitate to contact us.

Thank you for choosing our service!

Best regards,
The Children's Book Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, order_data['customer_email'], text)
        server.quit()
        
        print(f"Customer confirmation sent to {order_data['customer_email']}")
        
    except Exception as e:
        print(f"Failed to send customer confirmation: {str(e)}")

def send_production_notification(order_data: Dict[str, Any]):
    """Send production notification to admin."""
    try:
        if not EMAIL_USER or not EMAIL_PASSWORD:
            print("Email credentials not configured, skipping production notification")
            return
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = f"PRODUCTION NEEDED - {order_data['book_title']} (Order: {order_data['order_id']})"
        
        body = f"""
URGENT: Book production needed

Order ID: {order_data['order_id']}
Customer: {order_data['customer_name']} ({order_data['customer_email']})
Book Title: {order_data['book_title']}
Payment Status: PAID
Payment Date: {order_data['payment_date']}

DEADLINE: Book must be delivered within 12 hours of payment

Book Specifications:
- Pages: {order_data['num_pages']}
- Age Group: {order_data['age_group']}
- Language: {order_data['language']}
- Art Style: {order_data['art_style']}

Story Idea:
{order_data['story_idea']}

Characters: {len(order_data['characters'])} characters defined

Please begin production immediately and deliver the completed book to the customer within 12 hours.

Order file location: output/orders/order_{order_data['order_id']}.json
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, ADMIN_EMAIL, text)
        server.quit()
        
        print(f"Production notification sent for order {order_data['order_id']}")
        
    except Exception as e:
        print(f"Failed to send production notification: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Different port to avoid conflicts 