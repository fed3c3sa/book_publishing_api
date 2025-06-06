"""
Book planning module for the Children's Book Generator.

This module handles story ideation, book structure planning, and creates
detailed page-by-page plans for children's books.
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..ai_clients.openai_client import OpenAIClient
from ..utils.config import load_prompt, get_output_path, PLANS_DIR


class BookPlanner:
    """Handles book planning and story structure creation."""
    
    def __init__(self, openai_client: Optional[OpenAIClient] = None):
        """
        Initialize the book planner.
        
        Args:
            openai_client: OpenAI client instance. If None, creates a new one.
        """
        self.openai_client = openai_client or OpenAIClient()
        self.planning_prompt = load_prompt("book_planning")
    
    def create_book_plan(
        self,
        story_idea: str,
        characters: List[Dict[str, Any]],
        num_pages: int = 12,
        age_group: str = "3-6",
        language: str = "English",
        book_title: str = "",
        themes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a comprehensive book plan with page-by-page structure.
        
        Args:
            story_idea: The main story concept or plot
            characters: List of character description dictionaries
            num_pages: Number of pages for the book (including cover)
            age_group: Target age group (e.g., "3-5", "6-8", "9-12")
            language: Language for the book content
            book_title: Optional book title (will be generated if not provided)
            themes: Optional list of themes to include
            
        Returns:
            Comprehensive book plan dictionary
        """
        # Create book plan using OpenAI
        book_plan = self.openai_client.create_book_plan(
            story_idea=story_idea,
            num_pages=num_pages,
            age_group=age_group,
            language=language,
            characters=characters,
            prompt_template=self.planning_prompt
        )
        
        # Add metadata
        book_plan["metadata"] = {
            "original_story_idea": story_idea,
            "num_characters": len(characters),
            "requested_pages": num_pages,
            "target_age_group": age_group,
            "language": language
        }
        
        # Override title if provided
        if book_title:
            book_plan["book_title"] = book_title
        
        # Add or override themes if provided
        if themes:
            book_plan["themes"] = themes
        
        # Validate and enhance the plan
        book_plan = self._enhance_book_plan(book_plan, characters)
        
        return book_plan
    
    def _enhance_book_plan(
        self,
        book_plan: Dict[str, Any],
        characters: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Enhance the book plan with additional metadata and validation.
        
        Args:
            book_plan: Original book plan from AI
            characters: List of character descriptions
            
        Returns:
            Enhanced book plan
        """
        # Create character lookup
        char_lookup = {char["character_name"]: char for char in characters}
        
        # Enhance each page with character details
        enhanced_pages = []
        for page in book_plan.get("pages", []):
            enhanced_page = page.copy()
            
            # Add detailed character information for characters present
            characters_present = page.get("characters_present", [])
            enhanced_page["character_details"] = []
            
            for char_name in characters_present:
                if char_name in char_lookup:
                    enhanced_page["character_details"].append(char_lookup[char_name])
            
            # Add page metadata
            enhanced_page["page_id"] = f"page_{page.get('page_number', 0):02d}"
            enhanced_page["estimated_word_count"] = self._estimate_word_count(
                page.get("text_content_brief", ""),
                book_plan.get("target_age", "3-6")
            )
            
            enhanced_pages.append(enhanced_page)
        
        book_plan["pages"] = enhanced_pages
        
        # Add book-level statistics
        book_plan["statistics"] = {
            "total_pages": len(enhanced_pages),
            "story_pages": len([p for p in enhanced_pages if p.get("page_type") == "story"]),
            "total_characters": len(characters),
            "main_characters": len([c for c in characters if c.get("character_type") == "main"]),
            "estimated_total_words": sum(p.get("estimated_word_count", 0) for p in enhanced_pages)
        }
        
        return book_plan
    
    def _estimate_word_count(self, text_brief: str, age_group: str) -> int:
        """
        Estimate word count for a page based on text brief and age group.
        
        Args:
            text_brief: Brief description of page text
            age_group: Target age group
            
        Returns:
            Estimated word count
        """
        # Base word count by age group
        base_counts = {
            "3-5": 10,
            "3-6": 15,
            "6-8": 25,
            "6-9": 30,
            "9-12": 50
        }
        
        # Get base count for age group
        base_count = base_counts.get(age_group, 20)
        
        # Adjust based on text brief length
        brief_length = len(text_brief.split())
        if brief_length > 20:
            base_count += 10
        elif brief_length > 10:
            base_count += 5
        
        return base_count
    
    def save_book_plan(
        self,
        book_plan: Dict[str, Any],
        filename: Optional[str] = None
    ) -> Path:
        """
        Save book plan to a JSON file.
        
        Args:
            book_plan: Book plan dictionary
            filename: Optional custom filename. If None, uses book title.
            
        Returns:
            Path to the saved file
        """
        if filename is None:
            book_title = book_plan.get("book_title", "untitled_book")
            # Clean filename
            book_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            book_title = book_title.replace(' ', '_').lower()
            filename = f"{book_title}_plan.json"
        
        # Ensure filename has .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Get output path
        output_path = get_output_path(PLANS_DIR, filename)
        
        # Save book plan
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(book_plan, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def load_book_plan(self, filename: str) -> Dict[str, Any]:
        """
        Load book plan from a JSON file.
        
        Args:
            filename: Name of the plan file
            
        Returns:
            Book plan dictionary
        """
        file_path = PLANS_DIR / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Book plan file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_page_by_number(self, book_plan: Dict[str, Any], page_number: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific page from the book plan by page number.
        
        Args:
            book_plan: Book plan dictionary
            page_number: Page number to retrieve
            
        Returns:
            Page dictionary or None if not found
        """
        pages = book_plan.get("pages", [])
        for page in pages:
            if page.get("page_number") == page_number:
                return page
        return None
    
    def get_story_pages(self, book_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get all story pages (excluding cover and back cover).
        
        Args:
            book_plan: Book plan dictionary
            
        Returns:
            List of story page dictionaries
        """
        pages = book_plan.get("pages", [])
        return [page for page in pages if page.get("page_type") == "story"]
    
    def validate_book_plan(self, book_plan: Dict[str, Any]) -> bool:
        """
        Validate that book plan has required fields and structure.
        
        Args:
            book_plan: Book plan dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = [
            "book_title",
            "book_summary",
            "pages"
        ]
        
        for field in required_fields:
            if field not in book_plan:
                return False
        
        # Validate pages structure
        pages = book_plan.get("pages", [])
        if not isinstance(pages, list) or len(pages) == 0:
            return False
        
        # Validate each page has required fields
        for page in pages:
            if not isinstance(page, dict):
                return False
            if "page_number" not in page or "scene_description" not in page:
                return False
        
        return True
    
    def create_page_summary(self, book_plan: Dict[str, Any]) -> str:
        """
        Create a text summary of all pages in the book plan.
        
        Args:
            book_plan: Book plan dictionary
            
        Returns:
            Text summary of the book structure
        """
        summary_lines = [
            f"Book Title: {book_plan.get('book_title', 'Untitled')}",
            f"Summary: {book_plan.get('book_summary', 'No summary available')}",
            f"Target Age: {book_plan.get('target_age', 'Not specified')}",
            f"Total Pages: {len(book_plan.get('pages', []))}",
            "",
            "Page Structure:"
        ]
        
        for page in book_plan.get("pages", []):
            page_num = page.get("page_number", 0)
            page_type = page.get("page_type", "story")
            scene_desc = page.get("scene_description", "No description")
            characters = ", ".join(page.get("characters_present", []))
            
            summary_lines.append(
                f"  Page {page_num} ({page_type}): {scene_desc[:100]}..."
            )
            if characters:
                summary_lines.append(f"    Characters: {characters}")
        
        return "\n".join(summary_lines)

