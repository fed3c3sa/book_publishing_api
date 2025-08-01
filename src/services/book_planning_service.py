"""
Book planning service implementation.

This service handles story planning, book structure creation,
and page organization using the new domain models.
"""

import json
from typing import List, Optional
from pathlib import Path

from ..interfaces.book_planning_interface import BookPlanningInterface
from ..interfaces.ai_client_interface import AIClientInterface
from ..domain.models import BookPlan, Character, PageData, BookMetadata, BookStatistics
from ..exceptions import BookPlanningError, BookValidationError, BookNotFoundError
from ..utils.config import PLANS_DIR, get_output_path
from ..prompts.prompt_manager import PromptManager


class BookPlanningService(BookPlanningInterface):
    """
    Book planning service implementation.
    
    This service handles creating structured book plans with page-by-page
    breakdown, character integration, and metadata management.
    """
    
    def __init__(
        self,
        ai_client: AIClientInterface,
        prompt_manager: Optional[PromptManager] = None
    ):
        """
        Initialize the book planning service.
        
        Args:
            ai_client: AI client for book plan generation
            prompt_manager: Prompt manager for loading templates
        """
        self.ai_client = ai_client
        self.prompt_manager = prompt_manager or PromptManager()
        self._planning_prompt = None
    
    @property
    def planning_prompt(self) -> str:
        """Get the book planning prompt template."""
        if self._planning_prompt is None:
            self._planning_prompt = self.prompt_manager.get_book_planning_prompt()
        return self._planning_prompt
    
    def create_book_plan(
        self,
        story_idea: str,
        characters: List[Character],
        num_pages: int = 12,
        age_group: str = "3-6",
        language: str = "English",
        book_title: str = "",
        themes: List[str] = None
    ) -> BookPlan:
        """
        Create a comprehensive book plan.
        
        Args:
            story_idea: The main story concept or plot
            characters: List of character models
            num_pages: Number of pages for the book
            age_group: Target age group
            language: Language for the book content
            book_title: Optional book title
            themes: Optional list of themes to include
            
        Returns:
            Complete BookPlan model
            
        Raises:
            BookPlanningError: If planning fails
        """
        try:
            # Convert characters to dict format for AI client
            characters_data = [char.dict() for char in characters]
            
            # Create book plan using AI
            book_plan_data = self.ai_client.create_book_plan(
                story_idea=story_idea,
                num_pages=num_pages,
                age_group=age_group,
                language=language,
                characters=characters_data,
                prompt_template=self.planning_prompt
            )
            
            # Enhance book plan with metadata
            enhanced_plan_data = self._enhance_book_plan(
                book_plan_data, characters, story_idea, num_pages, age_group, language
            )
            
            # Override title if provided
            if book_title:
                enhanced_plan_data["book_title"] = book_title
            
            # Add or override themes if provided
            if themes:
                enhanced_plan_data["themes"] = themes
            
            return BookPlan(**enhanced_plan_data)
            
        except Exception as e:
            raise BookPlanningError(
                f"Book planning failed: {str(e)}",
                book_title=book_title
            )
    
    def _enhance_book_plan(
        self,
        book_plan_data: dict,
        characters: List[Character],
        story_idea: str,
        num_pages: int,
        age_group: str,
        language: str
    ) -> dict:
        """Enhance book plan with additional metadata and validation."""
        # Create character lookup
        char_lookup = {char.character_name: char for char in characters}
        
        # Enhance each page with character details
        enhanced_pages = []
        if "pages" in book_plan_data:
            for page_data in book_plan_data["pages"]:
                enhanced_page = page_data.copy()
                
                # Add detailed character information for characters present
                characters_present = page_data.get("characters_present", [])
                enhanced_page["character_details"] = [
                    char_lookup[char_name].dict() 
                    for char_name in characters_present 
                    if char_name in char_lookup
                ]
                
                # Add page metadata
                enhanced_page["page_id"] = f"page_{page_data.get('page_number', 0):02d}"
                enhanced_page["estimated_word_count"] = self._estimate_word_count(
                    page_data.get("text_content_brief", ""),
                    age_group
                )
                
                enhanced_pages.append(enhanced_page)
        
        book_plan_data["pages"] = enhanced_pages
        
        # Add metadata
        book_plan_data["metadata"] = BookMetadata(
            original_story_idea=story_idea,
            num_characters=len(characters),
            requested_pages=num_pages,
            target_age_group=age_group,
            language=language
        ).dict()
        
        # Add statistics
        book_plan_data["statistics"] = BookStatistics(
            total_pages=len(enhanced_pages),
            story_pages=len([p for p in enhanced_pages if p.get("page_type") == "story"]),
            total_characters=len(characters),
            main_characters=len([c for c in characters if c.character_type.value == "main"]),
            estimated_total_words=sum(p.get("estimated_word_count", 0) for p in enhanced_pages)
        ).dict()
        
        return book_plan_data
    
    def _estimate_word_count(self, text_brief: str, age_group: str) -> int:
        """Estimate word count for a page based on text brief and age group."""
        base_counts = {
            "3-5": 10,
            "3-6": 15,
            "6-8": 25,
            "6-9": 30,
            "9-12": 115
        }
        
        base_count = base_counts.get(age_group, 20)
        
        # Adjust based on text brief length
        brief_length = len(text_brief.split())
        if brief_length > 20:
            base_count += 10
        elif brief_length > 10:
            base_count += 5
        
        return base_count
    
    def save_book_plan(self, book_plan: BookPlan, filename: str = None) -> Path:
        """
        Save book plan to file.
        
        Args:
            book_plan: BookPlan model to save
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        if filename is None:
            book_title = book_plan.book_title
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
            json.dump(book_plan.dict(), f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def load_book_plan(self, filename: str) -> BookPlan:
        """
        Load book plan from file.
        
        Args:
            filename: Name of plan file
            
        Returns:
            BookPlan model
            
        Raises:
            BookNotFoundError: If file is not found
        """
        file_path = PLANS_DIR / filename
        if not file_path.exists():
            raise BookNotFoundError(
                f"Book plan file not found: {file_path}",
                book_title=filename
            )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                plan_data = json.load(f)
            
            return BookPlan(**plan_data)
            
        except Exception as e:
            raise BookPlanningError(
                f"Failed to load book plan from {file_path}: {str(e)}",
                book_title=filename
            )
    
    def validate_book_plan(self, book_plan: BookPlan) -> bool:
        """
        Validate book plan structure and completeness.
        
        Args:
            book_plan: BookPlan to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Pydantic validation happens automatically
            # Additional business logic validation
            
            if not book_plan.book_title.strip():
                return False
            
            if not book_plan.book_summary.strip():
                return False
            
            if not book_plan.pages:
                return False
            
            # Validate each page has required fields
            for page in book_plan.pages:
                if not hasattr(page, 'page_number') or not hasattr(page, 'scene_description'):
                    return False
            
            return True
            
        except Exception:
            return False