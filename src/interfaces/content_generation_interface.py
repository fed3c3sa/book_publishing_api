"""
Interface for content generation services.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from ..domain.models import BookPlan, Character, ImagePromptData, TextData


class ContentGenerationInterface(ABC):
    """Abstract interface for content generation services."""
    
    @abstractmethod
    def generate_page_image(
        self,
        page_data: Dict,
        characters: List[Character],
        book_title: str = "",
        art_style: str = "children's book illustration",
        use_reference: bool = True
    ) -> str:
        """
        Generate an image for a specific book page.
        
        Args:
            page_data: Page information from book plan
            characters: List of character models
            book_title: Book title for file organization
            art_style: Desired art style
            use_reference: Whether to use reference image for consistency
            
        Returns:
            Path to generated image file
        """
        pass
    
    @abstractmethod
    def generate_all_page_images(
        self,
        book_plan: BookPlan,
        characters: List[Character],
        art_style: str = "children's book illustration",
        include_cover: bool = True,
        uploaded_cover_path: Optional[str] = None
    ) -> Dict[int, str]:
        """
        Generate images for all pages in the book.
        
        Args:
            book_plan: Complete book plan
            characters: List of character models
            art_style: Desired art style
            include_cover: Whether to generate a cover image
            uploaded_cover_path: Path to uploaded cover image
            
        Returns:
            Dictionary mapping page numbers to image file paths
        """
        pass
    
    @abstractmethod
    def generate_page_text(
        self,
        page_data: Dict,
        book_plan: BookPlan,
        story_context: Optional[Dict] = None,
        previous_page_text: str = "",
        language: str = "English"
    ) -> TextData:
        """
        Generate text content for a specific book page.
        
        Args:
            page_data: Page information from book plan
            book_plan: Complete book plan
            story_context: Current story context for consistency
            previous_page_text: Text from previous page
            language: Language for text content
            
        Returns:
            TextData model with generated content
        """
        pass
    
    @abstractmethod
    def generate_all_page_texts(
        self,
        book_plan: BookPlan,
        language: str = "English"
    ) -> Dict[int, TextData]:
        """
        Generate text for all pages in the book.
        
        Args:
            book_plan: Complete book plan
            language: Language for text content
            
        Returns:
            Dictionary mapping page numbers to TextData models
        """
        pass