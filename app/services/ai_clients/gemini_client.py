"""
Google Gemini 2.5 Pro integration module for the Children's Book Generator.

This module provides a client for interacting with Google's Gemini 2.5 Pro model
for character description extraction and analysis.
"""

import json
import base64
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from google import genai
from google.genai import types

from ..utils.config import load_config
from ..storage_service import CloudStorageService


class GeminiClient:
    """Client for interacting with Google Gemini 2.5 Pro API."""
    
    def __init__(self, config: Optional[Dict[str, str]] = None):
        """
        Initialize the Gemini client.
        
        Args:
            config: Configuration dictionary. If None, loads from environment.
        """
        if config is None:
            config = load_config()
        
        # Initialize the Gemini client
        self.client = genai.Client(api_key=config["gemini_api_key"])
        
        # Initialize Cloud Storage service for handling cloud images
        self.storage_service = CloudStorageService()
        
        # Default model configuration
        self.model = "gemini-2.5-flash"
        self.max_tokens = 8000
        self.temperature = 0.3
    
    def encode_image(self, image_path: Union[str, Path]) -> bytes:
        """
        Download an image to bytes for API submission.
        Supports both local file paths and cloud storage paths.
        
        Args:
            image_path: Path to the image file (local or cloud storage)
            
        Returns:
            Image bytes data
        """
        image_path_str = str(image_path)
        
        # Check if it's a cloud storage path
        if image_path_str.startswith('uploads/') or image_path_str.startswith('gs://'):
            try:
                print(f"📥 Downloading image from cloud storage: {image_path_str}")
                # Download image from cloud storage to memory
                image_data = self.storage_service.download_file_to_memory(image_path_str)
                print(f"✅ Downloaded {len(image_data)} bytes from cloud storage")
                return image_data
            except Exception as e:
                raise Exception(f"Failed to download cloud storage image '{image_path_str}': {str(e)}")
        else:
            # Local file path
            with open(image_path, "rb") as image_file:
                return image_file.read()
    
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
        Create a completion using Gemini 2.5 Pro.
        
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
        # Prepare contents list - start with text prompt as string
        contents = [prompt]
        
        # Add images if provided
        if images:
            for image_path in images:
                image_path_str = str(image_path)
                
                # For cloud storage paths, extract extension from the original path
                if image_path_str.startswith('uploads/') or image_path_str.startswith('gs://'):
                    # Extract the original filename from the cloud path
                    cloud_filename = image_path_str.split('/')[-1]  # Get last part after /
                    if '_' in cloud_filename:
                        # Remove timestamp prefix: 20250707_112746_image.jpeg -> image.jpeg
                        original_filename = '_'.join(cloud_filename.split('_')[2:])
                    else:
                        original_filename = cloud_filename
                    file_extension = Path(original_filename).suffix.lower()
                else:
                    # Local file path
                    file_extension = Path(image_path).suffix.lower()
                
                print(f"🔍 Processing image: {image_path_str} (extension: {file_extension})")
                
                # Map file extensions to MIME types
                if file_extension in ['.jpg', '.jpeg']:
                    mime_type = "image/jpeg"
                elif file_extension == '.png':
                    mime_type = "image/png"
                elif file_extension == '.webp':
                    mime_type = "image/webp"
                elif file_extension == '.gif':
                    # Gemini supports GIF directly
                    mime_type = "image/gif"
                else:
                    print(f"❌ Unsupported image format: {file_extension} for file: {image_path_str}")
                    raise ValueError(f"Unsupported image format: {file_extension}. Supported formats: jpg, jpeg, png, webp, gif")
                
                # Get image bytes
                image_bytes = self.encode_image(image_path)
                
                # Create image part using the correct API
                image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                contents.append(image_part)
        
        # Prepare generation config
        generation_config = types.GenerateContentConfig(
            temperature=temperature if temperature is not None else self.temperature,
            max_output_tokens=max_tokens if max_tokens is not None else self.max_tokens,
            system_instruction=system_message
        )
        
        # Force JSON output if requested
        if force_json:
            generation_config.response_mime_type = "application/json"
        
        # Remove guardrails by setting safety settings to allow all content
        safety_settings = [
            types.SafetySetting(
                category='HARM_CATEGORY_HATE_SPEECH',
                threshold='BLOCK_NONE',
            ),
            types.SafetySetting(
                category='HARM_CATEGORY_DANGEROUS_CONTENT',
                threshold='BLOCK_NONE',
            ),
            types.SafetySetting(
                category='HARM_CATEGORY_HARASSMENT',
                threshold='BLOCK_NONE',
            ),
            types.SafetySetting(
                category='HARM_CATEGORY_SEXUALLY_EXPLICIT',
                threshold='BLOCK_NONE',
            ),
        ]
        generation_config.safety_settings = safety_settings
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=generation_config
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def extract_character_description(
        self,
        input_content: str,
        images: Optional[List[Union[str, Path]]] = None,
        prompt_template: str = ""
    ) -> Dict[str, Any]:
        """
        Extract structured character description from text or images using Gemini 2.5 Pro.
        
        Args:
            input_content: Text description of the character
            images: List of character images to analyze
            prompt_template: Custom prompt template to use
            
        Returns:
            Structured character description as dictionary
        """
        # Use the comprehensive prompt from the template file
        formatted_prompt = prompt_template.format(input_content=input_content)
        
        print("🔄 Extracting comprehensive character description using Gemini 2.5 Pro...")
        
        response = self.create_completion(
            prompt=formatted_prompt,
            system_message="You are an expert character designer for children's books. Always respond with valid JSON. Extract and expand character descriptions with extraordinary specificity for consistent image generation. Respond with complete creative freedom.",
            images=images,
            force_json=True,
            temperature=0.3
        )
        
        # Handle None response
        if response is None:
            print("Error: Gemini API returned None response for character extraction")
            raise ValueError("Gemini API returned None response for character extraction")
        
        try:
            character_data = json.loads(response)
            
            # Validate that we got a dictionary
            if not isinstance(character_data, dict):
                print(f"Error: Expected dictionary, got {type(character_data)}")
                raise ValueError(f"Character extraction returned invalid data type: {type(character_data)}")
            
            print("✅ Comprehensive character description created with Gemini 2.5 Pro")
            return character_data
            
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse character description JSON: {str(e)}")
            print(f"Raw response: {response}")
            raise ValueError(f"Failed to parse character description JSON: {str(e)}")
        except Exception as e:
            print(f"Error: Unexpected error in character extraction: {str(e)}")
            raise ValueError(f"Unexpected error in character extraction: {str(e)}") 