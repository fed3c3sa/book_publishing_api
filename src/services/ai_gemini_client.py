"""
Gemini AI client implementation with interface compliance.

This service adapts the existing Gemini client to use the new interface
and provides improved error handling and type safety.
"""

import json
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from ..interfaces.ai_client_interface import AIClientInterface
from ..exceptions import AIClientError, AIResponseError, AIAuthenticationError
from ..utils.config import load_config

# Import the existing Gemini client
from ..ai_clients.gemini_client import GeminiClient as LegacyGeminiClient


class GeminiAIClient(AIClientInterface):
    """
    Gemini AI client implementation that complies with the AIClientInterface.
    
    This class wraps the existing Gemini client with the new interface
    and provides improved error handling and type safety.
    """
    
    def __init__(self, config: Optional[Dict[str, str]] = None):
        """
        Initialize the Gemini AI client.
        
        Args:
            config: Configuration dictionary. If None, loads from environment.
        """
        try:
            if config is None:
                config = load_config()
            
            self.client = LegacyGeminiClient(config)
            
        except Exception as e:
            raise AIAuthenticationError(
                f"Failed to initialize Gemini client: {str(e)}",
                client_name="gemini"
            )
    
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
        Create a completion using Gemini 2.5.
        
        Args:
            prompt: The user prompt
            system_message: System message to set context
            images: List of image paths to include in the request
            force_json: Whether to force JSON output format
            temperature: Temperature for generation
            max_tokens: Max tokens for generation
            
        Returns:
            Generated text response
            
        Raises:
            AIClientError: If API call fails
            AIResponseError: If response is invalid
        """
        try:
            response = self.client.create_completion(
                prompt=prompt,
                system_message=system_message,
                images=images,
                force_json=force_json,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            if response is None:
                raise AIResponseError(
                    "Gemini API returned None response",
                    client_name="gemini"
                )
            
            return response
            
        except Exception as e:
            if isinstance(e, (AIClientError, AIResponseError)):
                raise
            
            raise AIClientError(
                f"Gemini API error: {str(e)}",
                client_name="gemini"
            )
    
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
            
        Raises:
            AIResponseError: If character extraction fails
        """
        try:
            character_data = self.client.extract_character_description(
                input_content=input_content,
                images=images,
                prompt_template=prompt_template
            )
            
            if not isinstance(character_data, dict):
                raise AIResponseError(
                    f"Expected dictionary, got {type(character_data)}",
                    client_name="gemini"
                )
            
            return character_data
            
        except Exception as e:
            if isinstance(e, AIResponseError):
                raise
            
            raise AIResponseError(
                f"Character description extraction failed: {str(e)}",
                client_name="gemini"
            )
    
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
            
        Raises:
            AIResponseError: If text generation fails
        """
        try:
            text_data = self.client.generate_page_text(
                page_description=page_description,
                characters_present=characters_present,
                age_group=age_group,
                language=language,
                book_theme=book_theme,
                previous_context=previous_context,
                story_arc=story_arc,
                prompt_template=prompt_template
            )
            
            if not isinstance(text_data, dict):
                raise AIResponseError(
                    f"Expected dictionary, got {type(text_data)}",
                    client_name="gemini"
                )
            
            return text_data
            
        except Exception as e:
            if isinstance(e, AIResponseError):
                raise
            
            raise AIResponseError(
                f"Page text generation failed: {str(e)}",
                client_name="gemini"
            )
    
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
            
        Raises:
            AIResponseError: If book planning fails
        """
        try:
            book_plan = self.client.create_book_plan(
                story_idea=story_idea,
                num_pages=num_pages,
                age_group=age_group,
                language=language,
                characters=characters,
                prompt_template=prompt_template
            )
            
            if not isinstance(book_plan, dict):
                raise AIResponseError(
                    f"Expected dictionary, got {type(book_plan)}",
                    client_name="gemini"
                )
            
            return book_plan
            
        except Exception as e:
            if isinstance(e, AIResponseError):
                raise
            
            raise AIResponseError(
                f"Book plan creation failed: {str(e)}",
                client_name="gemini"
            )
    
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
            
        Raises:
            AIResponseError: If image prompt generation fails
        """
        try:
            image_prompt = self.client.generate_image_prompt(
                page_description=page_description,
                characters_present=characters_present,
                character_descriptions=character_descriptions,
                mood_tone=mood_tone,
                visual_elements=visual_elements,
                art_style=art_style,
                prompt_template=prompt_template
            )
            
            if not isinstance(image_prompt, dict):
                raise AIResponseError(
                    f"Expected dictionary, got {type(image_prompt)}",
                    client_name="gemini"
                )
            
            return image_prompt
            
        except Exception as e:
            if isinstance(e, AIResponseError):
                raise
            
            raise AIResponseError(
                f"Image prompt generation failed: {str(e)}",
                client_name="gemini"
            )