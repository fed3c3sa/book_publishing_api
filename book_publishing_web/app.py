from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import os
import sys
import json
import time
import threading
import uuid
from datetime import datetime

# Add the project root to the Python path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
PARENT_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir))
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

# Import the main workflow function
try:
    sys.path.append(PARENT_DIR)
    from main import main_workflow, load_config
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

app = Flask(__name__, static_folder='static')

# Store book generation jobs
book_jobs = {}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/generate-book', methods=['POST'])
def generate_book():
    try:
        # Get data from request
        data = request.json
        
        # Create a unique project ID
        project_id = f"book_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        # Prepare configuration for the workflow
        try:
            base_config = load_config(os.path.join(PARENT_DIR, "config.yaml"))
        except Exception as e:
            print(f"Error loading config: {e}")
            # Fallback to default config path
            base_config = load_config()
            
        current_run_config = base_config.copy()
        
        # Update config with user inputs - match Streamlit app parameters
        user_idea = data.get("book_idea", "")
        current_run_config["user_book_idea"] = user_idea
        current_run_config["title"] = data.get("title", "")
        current_run_config["main_genre"] = data.get("main_genre", "")
        
        # Map parameter names to match what the backend expects
        current_run_config["writing_style_guide"] = data.get("writing_style", "")
        current_run_config["image_style_guide"] = data.get("image_style", "")
        
        # Copy for backward compatibility
        current_run_config["writing_style"] = data.get("writing_style", "")
        current_run_config["image_style"] = data.get("image_style", "")
        
        # Optional agent flags
        current_run_config["enable_trend_finder"] = data.get("enable_trend_finder", False)
        current_run_config["enable_style_imitator"] = data.get("enable_style_imitator", False)
        current_run_config["style_imitation_example_text"] = data.get("style_imitator_example_text", "")
        current_run_config["enable_translator"] = data.get("enable_translator", False)
        current_run_config["translation_target_language"] = data.get("target_language", "")
        
        # Store job info
        book_jobs[project_id] = {
            "status": "initializing",
            "progress": 0,
            "current_stage": "Starting book generation",
            "config": current_run_config,
            "start_time": time.time(),
            "pdf_path": None,
            "error": None,
            "user_idea": user_idea
        }
        
        # Start book generation in a separate thread
        thread = threading.Thread(
            target=run_book_generation,
            args=(project_id, current_run_config, user_idea)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "project_id": project_id,
            "status": "initializing"
        })
        
    except Exception as e:
        print(f"Error in generate_book: {e}")
        return jsonify({
            "error": str(e)
        }), 500

def run_book_generation(project_id, config, user_idea):
    """Run the book generation workflow in a separate thread"""
    try:
        # Update job status
        book_jobs[project_id]["status"] = "generating"
        book_jobs[project_id]["current_stage"] = "Generating ideas"
        book_jobs[project_id]["progress"] = 10
        
        print(f"Starting book generation with idea: {user_idea}")
        print(f"Config: {config}")
        
        # Call the main workflow function
        project_output_dir, pdf_path = main_workflow(config=config, user_book_idea=user_idea)
        
        # Update job status with results
        if pdf_path and os.path.exists(pdf_path):
            book_jobs[project_id]["status"] = "completed"
            book_jobs[project_id]["progress"] = 100
            book_jobs[project_id]["current_stage"] = "Book generation complete"
            book_jobs[project_id]["pdf_path"] = pdf_path
            book_jobs[project_id]["project_output_dir"] = project_output_dir
            print(f"Book generation completed successfully. PDF: {pdf_path}")
        else:
            book_jobs[project_id]["status"] = "failed"
            book_jobs[project_id]["error"] = f"Failed to generate PDF: {pdf_path}"
            print(f"Book generation failed: {pdf_path}")
    
    except Exception as e:
        # Update job status with error
        book_jobs[project_id]["status"] = "failed"
        book_jobs[project_id]["error"] = str(e)
        print(f"Error in book generation: {e}")
        import traceback
        print(traceback.format_exc())

@app.route('/api/book-status', methods=['GET'])
def get_book_status():
    project_id = request.args.get('project_id')
    
    if not project_id or project_id not in book_jobs:
        return jsonify({"error": "Invalid project ID"}), 404
    
    job = book_jobs[project_id]
    
    # If job is still running, update progress based on elapsed time
    if job["status"] == "generating":
        elapsed_time = time.time() - job["start_time"]
        
        # Simulate progress stages based on time
        if elapsed_time < 10:  # First 10 seconds
            job["progress"] = min(25, int(elapsed_time * 2.5))
            job["current_stage"] = "Generating ideas"
        elif elapsed_time < 20:  # Next 10 seconds
            job["progress"] = min(50, 25 + int((elapsed_time - 10) * 2.5))
            job["current_stage"] = "Writing story"
        elif elapsed_time < 30:  # Next 10 seconds
            job["progress"] = min(75, 50 + int((elapsed_time - 20) * 2.5))
            job["current_stage"] = "Creating images"
        else:  # Remaining time
            job["progress"] = min(95, 75 + int((elapsed_time - 30) * 0.5))
            job["current_stage"] = "Compiling book"
    
    return jsonify({
        "status": job["status"],
        "progress": job["progress"],
        "current_stage": job["current_stage"],
        "pdf_path": job["pdf_path"],
        "error": job["error"]
    })

@app.route('/api/book-preview', methods=['GET'])
def get_book_preview():
    project_id = request.args.get('project_id')
    
    if not project_id or project_id not in book_jobs:
        return jsonify({"error": "Invalid project ID"}), 404
    
    job = book_jobs[project_id]
    
    if job["status"] != "completed":
        return jsonify({"error": "Book generation not completed"}), 400
    
    # Get book information from the output directory
    project_output_dir = job.get("project_output_dir")
    pdf_path = job.get("pdf_path")
    
    if not project_output_dir or not pdf_path or not os.path.exists(pdf_path):
        return jsonify({"error": "Book files not found"}), 404
    
    # Get book title from config
    title = job["config"].get("title", "Your Generated Book")
    
    # Find cover image if available
    cover_image = None
    image_log_path = os.path.join(project_output_dir, "image_log.txt")
    if os.path.exists(image_log_path):
        with open(image_log_path, "r") as f:
            for line in f:
                if "cover" in line.lower() and "Path:" in line:
                    cover_path = line.split("Path:")[1].split(",")[0].strip()
                    if os.path.exists(cover_path):
                        cover_image = cover_path
                    break
    
    # Return book preview data
    return jsonify({
        "title": title,
        "cover_image": cover_image,
        "pdf_path": pdf_path,
        "project_output_dir": project_output_dir
    })

@app.route('/download-pdf/<path:project_id>')
def download_pdf(project_id):
    if project_id not in book_jobs:
        return "Book not found", 404
    
    job = book_jobs[project_id]
    pdf_path = job.get("pdf_path")
    
    if not pdf_path or not os.path.exists(pdf_path):
        return "PDF file not found", 404
    
    # Get the directory and filename
    directory = os.path.dirname(pdf_path)
    filename = os.path.basename(pdf_path)
    
    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/view-book-plan/<path:project_id>')
def view_book_plan(project_id):
    if project_id not in book_jobs:
        return "Book not found", 404
    
    job = book_jobs[project_id]
    project_output_dir = job.get("project_output_dir")
    
    if not project_output_dir:
        return "Book plan not found", 404
    
    book_plan_path = os.path.join(project_output_dir, "book_plan.yaml")
    if not os.path.exists(book_plan_path):
        return "Book plan file not found", 404
    
    with open(book_plan_path, "r") as f:
        content = f.read()
    
    return content, 200, {'Content-Type': 'text/plain'}

@app.route('/view-story-summary/<path:project_id>')
def view_story_summary(project_id):
    if project_id not in book_jobs:
        return "Book not found", 404
    
    job = book_jobs[project_id]
    project_output_dir = job.get("project_output_dir")
    
    if not project_output_dir:
        return "Story summary not found", 404
    
    summary_path = os.path.join(project_output_dir, "story_summary.txt")
    if not os.path.exists(summary_path):
        return "Story summary file not found", 404
    
    with open(summary_path, "r") as f:
        content = f.read()
    
    return content, 200, {'Content-Type': 'text/plain'}

@app.route('/view-image-log/<path:project_id>')
def view_image_log(project_id):
    if project_id not in book_jobs:
        return "Book not found", 404
    
    job = book_jobs[project_id]
    project_output_dir = job.get("project_output_dir")
    
    if not project_output_dir:
        return "Image log not found", 404
    
    log_path = os.path.join(project_output_dir, "image_log.txt")
    if not os.path.exists(log_path):
        return "Image log file not found", 404
    
    with open(log_path, "r") as f:
        content = f.read()
    
    return content, 200, {'Content-Type': 'text/plain'}

@app.route('/generated_images/<path:filename>')
def serve_generated_image(filename):
    return send_from_directory(os.path.join(PARENT_DIR, 'book_publishing', 'generated_images'), filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
