# agents/image_description_agent.py
from .base_agent import BaseBookAgent
from smolagents import InferenceClientModel
from typing import List, Dict, Any, Optional
import base64
import io
from PIL import Image
import json

class ImageDescriptionAgent(BaseBookAgent):
    """Agent responsible for analyzing images and generating character descriptions."""

    def __init__(self, model: InferenceClientModel, tools: List[callable] = None, **kwargs):
        """
        Initializes the ImageDescriptionAgent.

        Args:
            model (InferenceClientModel): An instantiated language model client.
            tools (List[callable], optional): A list of tools available to the agent. Defaults to an empty list.
            **kwargs: Additional arguments for BaseBookAgent.
        """
        agent_tools = tools if tools is not None else []
        super().__init__(
            model=model,
            tools=agent_tools,
            system_prompt_path="/home/federico/Desktop/personal/book_publishing_api/prompts/image_description_prompts.yaml",
            **kwargs
        )

    def analyze_character_image(self, image_data: bytes, character_name: str = None) -> str:
        """
        Analyzes an uploaded image and generates a detailed character description.

        Args:
            image_data (bytes): The image data as bytes.
            character_name (str, optional): Optional name for the character.

        Returns:
            str: A detailed character description suitable for use in book creation.
        """
        try:
            # Convert image to base64 for API
            image = Image.open(io.BytesIO(image_data))
            
            # Resize image if too large (to save on API costs)
            max_size = (512, 512)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to base64
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            prompt_template = self.load_prompt_template("analyze_character_image_prompt")
            
            character_name_str = f"Character Name: {character_name}" if character_name else "Character Name: Not specified"
            
            formatted_prompt = prompt_template.format(
                character_name=character_name_str
            )
            
            print(f"ImageDescriptionAgent: Analyzing character image{' for ' + character_name if character_name else ''}...")
            
            # Create message with image
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": formatted_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # Use the model's chat completion directly for vision
            response = self.model.client.chat.completions.create(
                model=self.model.model_id,
                messages=messages,
                max_tokens=500
            )
            
            character_description = response.choices[0].message.content.strip()
            
            print(f"ImageDescriptionAgent: Generated character description successfully")
            return character_description
            
        except Exception as e:
            print(f"ImageDescriptionAgent: Error analyzing image: {e}")
            fallback_description = f"A character{' named ' + character_name if character_name else ''} with distinctive features that make them unique and memorable."
            return fallback_description

    def enhance_character_description(self, basic_description: str, character_name: str = None, story_context: str = None) -> str:
        """
        Enhances a basic character description with more details suitable for book illustration.

        Args:
            basic_description (str): Basic character description.
            character_name (str, optional): Character name.
            story_context (str, optional): Context about the story/book.

        Returns:
            str: Enhanced character description.
        """
        try:
            prompt_template = self.load_prompt_template("enhance_character_description_prompt")
            
            character_name_str = f"Character Name: {character_name}" if character_name else "Character Name: Not specified"
            story_context_str = f"Story Context: {story_context}" if story_context else "Story Context: General children's book"
            
            formatted_prompt = prompt_template.format(
                basic_description=basic_description,
                character_name=character_name_str,
                story_context=story_context_str
            )
            
            print(f"ImageDescriptionAgent: Enhancing character description{' for ' + character_name if character_name else ''}...")
            
            llm_response = self.run(task=formatted_prompt)
            
            print(f"ImageDescriptionAgent: Enhanced character description successfully")
            return llm_response.strip()
            
        except Exception as e:
            print(f"ImageDescriptionAgent: Error enhancing description: {e}")
            return basic_description  # Return original if enhancement fails 