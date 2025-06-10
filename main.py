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
BOOK_TITLE = "Spud the Flying Potato and the Friendly Hydra"
STORY_IDEA = """
Spud is a magical potato who gained the power of flight when he was accidentally watered with enchanted rain from 
a fairy garden. He loves soaring through the sky and exploring the world from above. One day, while flying over 
the Whispering Woods, he discovers Hydrina, a gentle three-headed hydra who lives alone in a crystal cave. 
Everyone in the village fears Hydrina because of the scary stories they've heard, but Spud quickly learns 
that she's actually very kind and just wants to make friends. Each of Hydrina's heads has a different personality - 
one loves to sing, one loves to tell jokes, and one loves to paint beautiful pictures. Together, Spud and Hydrina 
must work to show the village that being different doesn't mean being scary, and that friendship can bloom in 
the most unexpected places. They organize a talent show where Hydrina can share her amazing abilities and win 
over the hearts of the villagers.
"""
NUM_PAGES = 10  # Including cover
AGE_GROUP = "4-7"  # Target age group: "3-5", "3-6", "6-8", "6-9", "9-12"
LANGUAGE = "English"
ART_STYLE = "whimsical children's book illustration, magical forest setting, bright cheerful colors, fantasy adventure style with friendly creatures"

# Character Configuration
# Each character can be defined by text description or image files
CHARACTERS = [
    {
        "type": "text",  # "text" or "image"
        "name": "Spud",
        "character_type": "main",  # "main", "secondary", "background"
        "content": """
        Spud is a round, golden-brown potato with a smooth, slightly bumpy skin that gleams in the sunlight. 
        He has large, bright blue eyes with long eyelashes and a wide, cheerful smile. Two small, translucent 
        fairy wings sprout from his back, shimmering with rainbow colors. He wears a tiny red bandana around 
        his middle like a belt and has small freckles scattered across his surface. When he flies, he leaves 
        a trail of golden sparkles behind him. He's about the size of a large apple and has a very expressive, 
        animated face that shows all his emotions clearly.
        """,
        "additional_description": ""  # Optional additional info for image-based characters
    },
    {
        "type": "text",
        "name": "Hydrina",
        "character_type": "main",
        "content": """
        Hydrina is a beautiful, medium-sized hydra with three distinct heads on graceful, serpentine necks. 
        Her body is covered in shimmering scales that shift from emerald green to turquoise blue in the light. 
        The left head (Melody) has violet eyes and wears a small flower crown, always humming or singing. 
        The middle head (Joy) has bright amber eyes and a constant smile, with rosy cheeks that dimple when 
        she laughs. The right head (Arte) has deep purple eyes and wears a tiny painter's beret, often with 
        paint smudges on her snout. All three heads have gentle, kind expressions. Hydrina's body is about 
        the size of a friendly dog, and she has delicate fins along her neck and small wings that help her 
        glide but not fully fly.
        """,
        "additional_description": ""
    },
    {
        "type": "text",
        "name": "Mayor Turnip",
        "character_type": "secondary",
        "content": """
        Mayor Turnip is a distinguished purple and white turnip who leads the village of Vegetable Valley. 
        He's quite round with leafy green hair that he keeps neatly combed and wears a small golden chain 
        of office around his middle. He has kind but worried brown eyes behind tiny spectacles and a well-groomed 
        mustache made of small root hairs. He wears a miniature blue vest with brass buttons and carries 
        a tiny scroll for important village business. Though initially cautious about Hydrina, he has a 
        good heart and wants what's best for his community.
        """,
        "additional_description": ""
    },
    {
        "type": "text",
        "name": "Bella Beetroot",
        "character_type": "secondary",
        "content": """
        Bella is a cheerful young beetroot with deep red and purple coloring and bright green leafy hair 
        tied in pigtails with yellow ribbons. She has sparkling green eyes and freckles across her cheeks. 
        She's adventurous and curious, always eager to make new friends. She wears a simple white dress 
        with red polka dots and tiny boots made from acorn caps. She's one of the first villagers to 
        befriend both Spud and Hydrina, and loves to explore and discover new things.
        """,
        "additional_description": ""
    },
    {
        "type": "text",
        "name": "Grumpy Garlic",
        "character_type": "secondary",
        "content": """
        Grumpy Garlic is an elderly garlic bulb with a papery white exterior and a permanently frowning 
        expression. He has small, sharp eyes and wispy white hair sprouting from his top. He's initially 
        very suspicious of Hydrina and believes all the scary stories about hydras. He wears a patched 
        brown jacket and walks with a tiny walking stick made from a twig. Despite his grumpy exterior, 
        he has a soft heart and eventually comes around when he sees Hydrina's true nature.
        """,
        "additional_description": ""
    }
]

# Advanced Configuration (optional)
THEMES = ["acceptance", "friendship", "overcoming prejudice", "celebrating differences", "showing kindness", "being brave"]
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

