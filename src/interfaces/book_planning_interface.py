"""
Interface for book planning services.
"""

from abc import ABC, abstractmethod
from typing import List
from pathlib import Path

from ..domain.models import BookPlan, Character


class BookPlanningInterface(ABC):
    """Abstract interface for book planning services."""
    
    @abstractmethod
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
        """
        pass
    
    @abstractmethod
    def save_book_plan(self, book_plan: BookPlan, filename: str = None) -> Path:
        """
        Save book plan to file.
        
        Args:
            book_plan: BookPlan model to save
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        pass
    
    @abstractmethod
    def load_book_plan(self, filename: str) -> BookPlan:
        """
        Load book plan from file.
        
        Args:
            filename: Name of plan file
            
        Returns:
            BookPlan model
        """
        pass
    
    @abstractmethod
    def validate_book_plan(self, book_plan: BookPlan) -> bool:
        """
        Validate book plan structure and completeness.
        
        Args:
            book_plan: BookPlan to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass