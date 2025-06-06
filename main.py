#!/usr/bin/env python3
"""
Children's Book Generator - Main Script

This is the main entry point for generating AI-powered children's books.
Configure the parameters below and run this script to create your book.

Author: AI Children's Book Generator
Version: 1.0.0
"""

import sys
import os
from pathlib import Path
import json
from typing import List, Dict, Any
import dotenv

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import our modules
from src.character_processing import CharacterProcessor
from src.book_planning import BookPlanner
from src.content_generation import ImageGenerator, TextGenerator
from src.pdf_generation import PDFGenerator
from src.utils.config import load_config

dotenv.load_dotenv("secrets.env")
# ============================================================================
# CONFIGURATION SECTION - EDIT THESE PARAMETERS
# ============================================================================

# Book Configuration
BOOK_TITLE = "Milo the Brave Little Mouse"
STORY_IDEA = """
Milo is a tiny mouse who lives in the walls of an old library. He loves reading books but is too scared to 
venture out during the day when humans are around. One night, he discovers that all the books in the library 
are losing their words - they're floating away like leaves in the wind! Milo must overcome his fears and 
go on an adventure through the library to find the mysterious Word Gobbler and save all the stories before 
morning comes. Along the way, he meets helpful friends and learns that being small doesn't mean being powerless.
"""
NUM_PAGES = 8  # Including cover
AGE_GROUP = "4-7"  # Target age group: "3-5", "3-6", "6-8", "6-9", "9-12"
LANGUAGE = "English"
ART_STYLE = "children's book illustration, cozy library setting, warm magical atmosphere, soft watercolor style"

# Character Configuration
# Each character can be defined by text description or image files
CHARACTERS = [
    {
        "type": "text",  # "text" or "image"
        "name": "Milo",
        "character_type": "main",  # "main", "secondary", "background"
        "content": """
        Milo is a tiny brown mouse with soft gray patches on his belly and ears. He has large, 
        curious dark eyes and small round glasses that he found in the library. He wears a tiny 
        blue vest with small buttons and carries a miniature satchel made from a thimble. 
        His whiskers twitch when he's nervous, and he has a kind, determined expression.
        """,
        "additional_description": ""  # Optional additional info for image-based characters
    },
    {
        "type": "text",
        "name": "Luna",
        "character_type": "secondary",
        "content": """
        Luna is a wise old owl who lives in the library's tallest bookshelf. She has beautiful 
        silver and white feathers with bright golden eyes. She wears a small reading monocle 
        and has tiny scrolls tied to her feet. She's the keeper of the library's secrets and 
        speaks in gentle, thoughtful whispers.
        """,
        "additional_description": ""
    },
    {
        "type": "text",
        "name": "Pip",
        "character_type": "secondary",
        "content": """
        Pip is a cheerful cricket who lives in the library's old radiator. He has bright green 
        coloring with darker green stripes and tiny antennae that glow softly in the dark. 
        He can make beautiful music with his wings and has a small harmonica made from a 
        matchstick. He's energetic and loves to help his friends.
        """,
        "additional_description": ""
    },
    {
        "type": "text",
        "name": "Word Gobbler",
        "character_type": "secondary",
        "content": """
        The Word Gobbler is not scary but sad - a creature made of shadows and forgotten 
        letters that swirl around its misty form. It has gentle purple eyes and feeds on 
        words because it's lonely and wants to understand stories. It looks like a cross 
        between a cloud and a friendly ghost, with letters floating around it like fireflies.
        """,
        "additional_description": ""
    }
]

# Advanced Configuration (optional)
THEMES = ["courage", "friendship", "facing fears", "the power of stories", "helping others"]
INCLUDE_COVER = True
GENERATE_HTML = True

# ============================================================================
# WORKFLOW FUNCTIONS
# ============================================================================

def print_step(step_number: int, description: str):
    """Print a formatted step description."""
    print(f"\n{'='*60}")
    print(f"STEP {step_number}: {description}")
    print(f"{'='*60}")

def print_progress(message: str):
    """Print a progress message."""
    print(f"  → {message}")

def main():
    """Main workflow for generating a children's book."""
    print("🎨 Children's Book Generator Starting...")
    print(f"📖 Creating: {BOOK_TITLE}")
    print(f"🎯 Target Age: {AGE_GROUP}")
    print(f"📄 Pages: {NUM_PAGES}")
    
    try:
        # Load configuration and check API keys
        print_step(1, "Loading Configuration and API Keys")
        config = load_config()
        print_progress("✅ Configuration loaded successfully")
        print_progress("✅ API keys validated")
        
        # Initialize processors
        print_step(2, "Initializing AI Clients")
        character_processor = CharacterProcessor()
        book_planner = BookPlanner()
        image_generator = ImageGenerator()
        text_generator = TextGenerator()
        pdf_generator = PDFGenerator()
        print_progress("✅ All AI clients initialized")
        
        # Process characters
        print_step(3, "Processing Character Descriptions")
        print_progress(f"Processing {len(CHARACTERS)} characters...")
        
        processed_characters = character_processor.process_multiple_characters(CHARACTERS)
        
        if not processed_characters:
            raise Exception("No characters were successfully processed")
        
        print_progress(f"✅ Successfully processed {len(processed_characters)} characters")
        for char in processed_characters:
            char_name = char.get("character_name", "Unknown")
            char_type = char.get("character_type", "unknown")
            print_progress(f"   - {char_name} ({char_type})")
        
        # Upgrade existing character files to new format if needed
        print_progress("🔄 Checking and upgrading character formats...")
        characters_dir = Path("output/characters")
        if characters_dir.exists():
            for char_file in characters_dir.glob("*.json"):
                try:
                    upgraded_char = character_processor.upgrade_character_file(char_file.name)
                    # Update processed_characters with upgraded data
                    for i, char in enumerate(processed_characters):
                        if char.get("character_name", "").lower() == upgraded_char.get("character_name", "").lower():
                            processed_characters[i] = upgraded_char
                            break
                except Exception as e:
                    print_progress(f"   ⚠️  Warning: Could not upgrade {char_file.name}: {str(e)}")
        
        print_progress("✅ Character format upgrade completed")
        
        # Create book plan
        print_step(4, "Creating Book Plan and Story Structure")
        print_progress("Generating story structure with AI...")
        
        book_plan = book_planner.create_book_plan(
            story_idea=STORY_IDEA,
            characters=processed_characters,
            num_pages=NUM_PAGES,
            age_group=AGE_GROUP,
            language=LANGUAGE,
            book_title=BOOK_TITLE,
            themes=THEMES
        )
        
        # Save book plan
        plan_path = book_planner.save_book_plan(book_plan)
        print_progress(f"✅ Book plan created and saved to: {plan_path}")
        print_progress(f"   Title: {book_plan.get('book_title', 'Unknown')}")
        print_progress(f"   Pages: {len(book_plan.get('pages', []))}")
        print_progress(f"   Summary: {book_plan.get('book_summary', 'No summary')[:100]}...")
        
        # Generate images
        print_step(5, "Generating Images for All Pages")
        print_progress("Creating illustrations with AI...")
        
        page_images = image_generator.generate_all_page_images(
            book_plan=book_plan,
            characters=processed_characters,
            art_style=ART_STYLE,
            include_cover=INCLUDE_COVER
        )
        
        print_progress(f"✅ Generated {len(page_images)} images")
        for page_num, image_path in page_images.items():
            page_type = "Cover" if page_num == 0 else f"Page {page_num}"
            print_progress(f"   - {page_type}: {Path(image_path).name}")
        
        # Generate text content
        print_step(6, "Generating Text Content for All Pages")
        print_progress("Creating page text with AI...")
        
        page_texts = text_generator.generate_all_page_texts(
            book_plan=book_plan,
            language=LANGUAGE
        )
        
        print_progress(f"✅ Generated text for {len(page_texts)} pages")
        for page_num, text_data in page_texts.items():
            word_count = text_data.get("word_count", 0)
            print_progress(f"   - Page {page_num}: {word_count} words")
        
        # Generate PDF
        print_step(7, "Assembling Final PDF Book")
        print_progress("Combining images and text into PDF...")
        
        pdf_path = pdf_generator.create_book_pdf(
            book_plan=book_plan,
            page_images=page_images,
            page_texts=page_texts
        )
        
        print_progress(f"✅ PDF book created: {pdf_path}")
        
        # Generate HTML version if requested
        if GENERATE_HTML:
            print_step(8, "Creating HTML Version")
            print_progress("Generating interactive HTML book...")
            
            html_path = pdf_generator.create_html_version(
                book_plan=book_plan,
                page_images=page_images,
                page_texts=page_texts
            )
            
            print_progress(f"✅ HTML book created: {html_path}")
        
        # Final summary
        print("\n" + "="*60)
        print("🎉 BOOK GENERATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"📖 Book Title: {book_plan.get('book_title', 'Unknown')}")
        print(f"📄 Total Pages: {len(book_plan.get('pages', []))}")
        print(f"🎨 Images Generated: {len(page_images)}")
        print(f"📝 Text Pages: {len(page_texts)}")
        print(f"📁 PDF Output: {pdf_path}")
        if GENERATE_HTML:
            print(f"🌐 HTML Output: {html_path}")
        
        print("\n📂 All files saved in the 'output' directory:")
        print(f"   - Characters: output/characters/")
        print(f"   - Book Plan: output/plans/")
        print(f"   - Images: output/images/")
        print(f"   - Text: output/texts/")
        print(f"   - Final Books: output/books/")
        
        print("\n✨ Your children's book is ready!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nPlease check:")
        print("1. Your API keys are correctly set in secrets.env")
        print("2. All required dependencies are installed (pip install -r requirements.txt)")
        print("3. Your internet connection is working")
        print("4. The character descriptions and story idea are appropriate")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

