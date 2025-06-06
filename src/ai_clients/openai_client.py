"""
OpenAI GPT-4o integration module for the Children's Book Generator.

This module provides a client for interacting with OpenAI's GPT-4o model
for text generation, character description, and book planning.
"""

import json
import base64
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import openai
from openai import OpenAI

from ..utils.config import load_config


class OpenAIClient:
    """Client for interacting with OpenAI GPT-4o API."""
    
    def __init__(self, config: Optional[Dict[str, str]] = None):
        """
        Initialize the OpenAI client.
        
        Args:
            config: Configuration dictionary. If None, loads from environment.
        """
        if config is None:
            config = load_config()
        
        # Get organization ID, but skip if it's empty or placeholder
        org_id = config.get("openai_org_id")
        if org_id and org_id.strip() and org_id.strip() != "your_openai_org_id_here":
            org_id = org_id.strip()
        else:
            org_id = None
        
        self.client = OpenAI(
            api_key=config["openai_api_key"],
            organization=org_id
        )
        
        # Default model configuration
        self.model = "gpt-4o"
        self.max_tokens = 4000
        self.temperature = 0.7
    
    def encode_image(self, image_path: Union[str, Path]) -> str:
        """
        Encode an image to base64 for API submission.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image string
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
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
        Create a completion using GPT-4o.
        
        Args:
            prompt: The user prompt
            system_message: System message to set context
            images: List of image paths to include in the request
            force_json: Whether to force JSON output format
            temperature: Temperature for generation (overrides default)
            max_tokens: Max tokens for generation (overrides default)
            
        Returns:
            Generated text response
        """
        # Prepare messages
        messages = [
            {"role": "system", "content": system_message}
        ]
        
        # Prepare user message content
        user_content = [{"type": "text", "text": prompt}]
        
        # Add images if provided
        if images:
            for image_path in images:
                # Determine image format
                image_path = Path(image_path)
                if image_path.suffix.lower() in ['.jpg', '.jpeg']:
                    media_type = "image/jpeg"
                elif image_path.suffix.lower() == '.png':
                    media_type = "image/png"
                elif image_path.suffix.lower() == '.webp':
                    media_type = "image/webp"
                else:
                    raise ValueError(f"Unsupported image format: {image_path.suffix}")
                
                # Encode image
                base64_image = self.encode_image(image_path)
                
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{media_type};base64,{base64_image}"
                    }
                })
        
        messages.append({"role": "user", "content": user_content})
        
        # Prepare request parameters
        request_params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.max_tokens
        }
        
        # Force JSON output if requested
        if force_json:
            request_params["response_format"] = {"type": "json_object"}
        
        try:
            response = self.client.chat.completions.create(**request_params)
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
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
        # Format the prompt
        formatted_prompt = prompt_template.format(input_content=input_content)
        
        # Create completion
        response = self.create_completion(
            prompt=formatted_prompt,
            system_message="You are an expert character designer for children's books. Always respond with valid JSON.",
            images=images,
            force_json=True,
            temperature=0.3  # Lower temperature for more consistent structure
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse character description JSON: {str(e)}")
    
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
            age_group: Target age group (e.g., "3-5", "6-8")
            language: Language for the book
            characters: List of character descriptions
            prompt_template: Custom prompt template to use
            
        Returns:
            Structured book plan as dictionary
        """
        # Format the prompt
        formatted_prompt = prompt_template.format(
            story_idea=story_idea,
            num_pages=num_pages,
            age_group=age_group,
            language=language,
            characters=json.dumps(characters, indent=2)
        )
        
        # Create completion
        response = self.create_completion(
            prompt=formatted_prompt,
            system_message="You are an expert children's book author and story planner. Always respond with valid JSON.",
            force_json=True,
            temperature=0.5
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse book plan JSON: {str(e)}")
    
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
        # Format the prompt
        formatted_prompt = prompt_template.format(
            page_description=page_description,
            characters_present=", ".join(characters_present),
            character_descriptions=json.dumps(character_descriptions, indent=2),
            mood_tone=mood_tone,
            visual_elements=", ".join(visual_elements),
            art_style=art_style
        )
        
        # Create completion
        response = self.create_completion(
            prompt=formatted_prompt,
            system_message="You are an expert at creating detailed prompts for AI image generation. Always respond with valid JSON.",
            force_json=True,
            temperature=0.4
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse image prompt JSON: {str(e)}")
    
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
        # Format the prompt
        formatted_prompt = prompt_template.format(
            page_description=page_description,
            characters_present=", ".join(characters_present),
            age_group=age_group,
            language=language,
            book_theme=book_theme,
            previous_context=previous_context,
            story_arc=story_arc
        )
        
        # Create completion
        response = self.create_completion(
            prompt=formatted_prompt,
            system_message="You are an expert children's book author. Always respond with valid JSON.",
            force_json=True,
            temperature=0.6
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse page text JSON: {str(e)}")

