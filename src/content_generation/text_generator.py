"""
Text generation module for the Children's Book Generator.

This module handles creating engaging, age-appropriate text content for
each page of the children's book.
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..ai_clients.openai_client import OpenAIClient
from ..utils.config import load_prompt, get_output_path, TEXTS_DIR


class TextGenerator:
    """Handles text generation for book pages."""
    
    def __init__(self, openai_client: Optional[OpenAIClient] = None):
        """
        Initialize the text generator.
        
        Args:
            openai_client: OpenAI client instance. If None, creates a new one.
        """
        self.openai_client = openai_client or OpenAIClient()
        self.text_prompt_template = load_prompt("text_generation")
    
    def generate_page_text(
        self,
        page_data: Dict[str, Any],
        book_plan: Dict[str, Any],
        previous_page_text: str = "",
        language: str = "English"
    ) -> Dict[str, Any]:
        """
        Generate text content for a specific book page.
        
        Args:
            page_data: Page information from book plan
            book_plan: Complete book plan data
            previous_page_text: Text from the previous page for context
            language: Language for the text content
            
        Returns:
            Structured page text data
        """
        # Extract page information
        page_description = page_data.get("scene_description", "")
        characters_present = page_data.get("characters_present", [])
        age_group = book_plan.get("target_age", "3-6")
        book_theme = ", ".join(book_plan.get("themes", ["adventure", "friendship"]))
        
        # Get story arc information
        story_arc = json.dumps(book_plan.get("story_arc", {}))
        
        # Generate page text using OpenAI
        page_text_data = self.openai_client.generate_page_text(
            page_description=page_description,
            characters_present=characters_present,
            age_group=age_group,
            language=language,
            book_theme=book_theme,
            previous_context=previous_page_text,
            story_arc=story_arc,
            prompt_template=self.text_prompt_template
        )
        
        # Add page metadata
        page_text_data["page_metadata"] = {
            "page_number": page_data.get("page_number", 0),
            "page_type": page_data.get("page_type", "story"),
            "characters_present": characters_present
        }
        
        return page_text_data
    
    def generate_all_page_texts(
        self,
        book_plan: Dict[str, Any],
        language: str = "English"
    ) -> Dict[int, Dict[str, Any]]:
        """
        Generate text for all pages in the book.
        
        Args:
            book_plan: Complete book plan data
            language: Language for the text content
            
        Returns:
            Dictionary mapping page numbers to text data
        """
        book_title = book_plan.get("book_title", "Untitled Book")
        pages = book_plan.get("pages", [])
        
        generated_texts = {}
        previous_text = ""
        
        # Generate text for each page
        for page_data in pages:
            page_number = page_data.get("page_number", 0)
            page_type = page_data.get("page_type", "story")
            
            # Skip cover page
            if page_type == "cover":
                continue
            
            try:
                text_data = self.generate_page_text(
                    page_data=page_data,
                    book_plan=book_plan,
                    previous_page_text=previous_text,
                    language=language
                )
                
                # Save the text data
                self._save_page_text(text_data, book_title, page_number)
                
                # Update previous text for context
                previous_text = text_data.get("page_text", "")
                
                generated_texts[page_number] = text_data
                print(f"Generated text for page {page_number}")
                
            except Exception as e:
                print(f"Error generating text for page {page_number}: {str(e)}")
                continue
        
        return generated_texts
    
    def _save_page_text(
        self,
        text_data: Dict[str, Any],
        book_title: str,
        page_number: int
    ) -> Path:
        """
        Save page text data to a JSON file.
        
        Args:
            text_data: Page text data dictionary
            book_title: Book title for organization
            page_number: Page number
            
        Returns:
            Path to the saved file
        """
        # Create book-specific directory
        book_texts_dir = self._get_book_texts_dir(book_title)
        
        # Save text data
        filename = f"page_{page_number:02d}_text.json"
        output_path = book_texts_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(text_data, f, indent=2, ensure_ascii=False)
        
        # Also save plain text version for easy access
        plain_text = text_data.get("page_text", "")
        plain_text_path = book_texts_dir / f"page_{page_number:02d}_text.txt"
        
        with open(plain_text_path, 'w', encoding='utf-8') as f:
            f.write(plain_text)
        
        return output_path
    
    def _get_book_texts_dir(self, book_title: str) -> Path:
        """
        Get the texts directory for a specific book.
        
        Args:
            book_title: Book title
            
        Returns:
            Path to the book's texts directory
        """
        # Clean book title for directory name
        clean_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_title = clean_title.replace(' ', '_').lower()
        
        book_texts_dir = TEXTS_DIR / clean_title
        book_texts_dir.mkdir(parents=True, exist_ok=True)
        
        return book_texts_dir
    
    def load_page_text(self, book_title: str, page_number: int) -> Dict[str, Any]:
        """
        Load page text data from a JSON file.
        
        Args:
            book_title: Book title
            page_number: Page number
            
        Returns:
            Page text data dictionary
        """
        book_texts_dir = self._get_book_texts_dir(book_title)
        file_path = book_texts_dir / f"page_{page_number:02d}_text.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Page text file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_all_page_texts(self, book_title: str) -> Dict[int, Dict[str, Any]]:
        """
        Get all page texts for a book.
        
        Args:
            book_title: Book title
            
        Returns:
            Dictionary mapping page numbers to text data
        """
        book_texts_dir = self._get_book_texts_dir(book_title)
        
        if not book_texts_dir.exists():
            raise FileNotFoundError(f"Book texts directory not found: {book_texts_dir}")
        
        page_texts = {}
        
        # Find all JSON text files
        for file_path in book_texts_dir.glob("page_*_text.json"):
            try:
                # Extract page number from filename
                filename = file_path.name
                page_number = int(filename.split("_")[1])
                
                # Load text data
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_data = json.load(f)
                
                page_texts[page_number] = text_data
                
            except (ValueError, IndexError, json.JSONDecodeError) as e:
                print(f"Error loading text file {file_path}: {str(e)}")
                continue
        
        return page_texts

