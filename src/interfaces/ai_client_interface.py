"""
Abstract interface for AI client implementations.

This interface defines the contract that all AI clients (Gemini, OpenAI, etc.)
must implement to ensure consistent behavior across different providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from ..domain.models import Character, BookPlan, ImagePromptData, TextData


class AIClientInterface(ABC):
    """Abstract interface for AI client implementations."""
    
    @abstractmethod
    def create_completion(
        self,
        prompt: str,
        system_message: str = "You are a helpful assistant.",
        images: Optional[List[Union[str, Path]]] = None,
        force_json: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Create a completion using the AI model.
        
        Args:
            prompt: The user prompt
            system_message: System message to set context
            images: List of image paths to include in the request
            force_json: Whether to force JSON output format
            temperature: Temperature for generation
            max_tokens: Max tokens for generation
            
        Returns:
            Generated text response
        """
        pass
    
    @abstractmethod
    def extract_character_description(
        self,
        input_content: str,
        images: Optional[List[Union[str, Path]]] = None,
        prompt_template: str = ""
    ) -> Dict[str, Any]:
        """
        Extract structured character description from text or images.
        
        Args:
            input_content: Text description of the character
            images: List of character images to analyze
            prompt_template: Custom prompt template to use
            
        Returns:
            Structured character description as dictionary
        """
        pass
    
    @abstractmethod
    def generate_page_text(
        self,
        page_description: str,
        characters_present: List[str],
        age_group: str,
        language: str,
        book_theme: str,
        previous_context: str = "",
        story_arc: str = "",
        prompt_template: str = ""
    ) -> Dict[str, Any]:
        """
        Generate text content for a book page.
        
        Args:
            page_description: Description of what happens on the page
            characters_present: List of character names present
            age_group: Target age group
            language: Language for the text
            book_theme: Overall theme of the book
            previous_context: Context from previous pages
            story_arc: Overall story arc information
            prompt_template: Custom prompt template to use
            
        Returns:
            Structured page text as dictionary
        """
        pass
    
    @abstractmethod
    def create_book_plan(
        self,
        story_idea: str,
        num_pages: int,
        age_group: str,
        language: str,
        characters: List[Dict[str, Any]],
        prompt_template: str = ""
    ) -> Dict[str, Any]:
        """
        Create a structured book plan.
        
        Args:
            story_idea: The main story concept
            num_pages: Number of pages for the book
            age_group: Target age group
            language: Language for the book
            characters: List of character descriptions
            prompt_template: Custom prompt template to use
            
        Returns:
            Structured book plan as dictionary
        """
        pass
    
    @abstractmethod
    def generate_image_prompt(
        self,
        page_description: str,
        characters_present: List[str],
        character_descriptions: Dict[str, Any],
        mood_tone: str,
        visual_elements: List[str],
        art_style: str,
        prompt_template: str = ""
    ) -> Dict[str, Any]:
        """
        Generate a detailed prompt for image generation.
        
        Args:
            page_description: Description of what happens on the page
            characters_present: List of character names present
            character_descriptions: Full character description data
            mood_tone: Mood and tone for the scene
            visual_elements: List of visual elements to include
            art_style: Desired art style
            prompt_template: Custom prompt template to use
            
        Returns:
            Structured image prompt as dictionary
        """
        pass