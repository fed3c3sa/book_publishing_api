"""
Ideogram API integration module for the Children's Book Generator.

This module provides a client for generating images using the Ideogram API
for children's book illustrations.
"""

import os
import time
import requests
from typing import Dict, Any, Optional, Union
from pathlib import Path
from typing import List

from ..utils.config import load_config


class IdeogramClient:
    """Client for interacting with Ideogram API."""
    
    def __init__(self, config: Optional[Dict[str, str]] = None):
        """
        Initialize the Ideogram client.
        
        Args:
            config: Configuration dictionary. If None, loads from environment.
        """
        if config is None:
            config = load_config()
        
        self.api_key = config["ideogram_api_key"]
        self.base_url = "https://api.ideogram.ai/v1/ideogram-v3/generate"
    
    def generate_image(
        self,
        prompt: str,
        output_path: Union[str, Path],
        style_reference_image_path: Optional[Union[str, Path]] = None,
        aspect_ratio: str = "1x1",
        style_type: str = "GENERAL",
        magic_prompt: str = "AUTO",
        num_images: int = 1,
        resolution: Optional[str] = None,
        rendering_speed: str = "DEFAULT",
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None
    ) -> str:
        """
        Generate an image using Ideogram API.
        
        Args:
            prompt: Text prompt for image generation
            output_path: Path where the generated image will be saved
            style_reference_image_path: Optional reference image for style consistency
            aspect_ratio: Aspect ratio for the image (1x1, 16x9, etc.)
            style_type: Style type (AUTO, GENERAL, REALISTIC, DESIGN)
            magic_prompt: Magic prompt option (AUTO, ON, OFF)
            num_images: Number of images to generate (1-8)
            resolution: Resolution if not using aspect_ratio
            rendering_speed: Rendering speed (TURBO, DEFAULT, QUALITY)
            negative_prompt: Description of what to exclude from image
            seed: Random seed for reproducible generation
            
        Returns:
            Path to the generated image file
        """
        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare form data - all parameters go in data, not JSON
        data = {
            "prompt": prompt,
            "magic_prompt": magic_prompt,
            "num_images": num_images,  # Send as integer, not string
            "rendering_speed": rendering_speed
        }
        
        # Add aspect ratio or resolution
        if resolution:
            data["resolution"] = resolution
        else:
            data["aspect_ratio"] = aspect_ratio
            
        # Add optional parameters if provided
        if negative_prompt:
            data["negative_prompt"] = negative_prompt
        if seed is not None:
            data["seed"] = seed  # Send as integer, not string
        
        # Prepare files for multipart upload
        files = {}
        
        # Add style reference image if provided
        if style_reference_image_path and os.path.exists(style_reference_image_path):
            try:
                with open(style_reference_image_path, 'rb') as img_file:
                    # Read the image content
                    image_content = img_file.read()
                    
                    # Check file size (max 10MB)
                    if len(image_content) > 10 * 1024 * 1024:
                        print(f"Warning: Style reference image exceeds 10MB limit, skipping")
                    else:
                        # Get the file extension to determine MIME type
                        ext = os.path.splitext(style_reference_image_path)[1].lower()
                        mime_types = {
                            '.jpg': 'image/jpeg',
                            '.jpeg': 'image/jpeg',
                            '.png': 'image/png',
                            '.webp': 'image/webp'
                        }
                        mime_type = mime_types.get(ext, 'image/jpeg')
                        
                        # Add to files with proper filename and MIME type
                        files['style_reference_images'] = (
                            os.path.basename(style_reference_image_path),
                            image_content,
                            mime_type
                        )
                        print(f"Using style reference image: {style_reference_image_path}")
            except Exception as e:
                print(f"Warning: Could not read style reference image: {e}")
        
        # Only add style_type if no style reference images are used
        # API allows only one of: style_type, style_codes, OR style_reference_images
        if not files:
            data["style_type"] = style_type
        
        # Make the API request - use JSON format when no files, multipart when files present
        try:
            if files:
                # Use multipart/form-data when style reference images are provided
                response = requests.post(
                    self.base_url,
                    headers={"Api-Key": self.api_key},
                    data=data,
                    files=files,
                    timeout=120,  # Increased timeout for image generation
                )
            else:
                # Use JSON format when no files to upload
                response = requests.post(
                    self.base_url,
                    headers={
                        "Api-Key": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json=data,
                    timeout=120,  # Increased timeout for image generation
                )
            response.raise_for_status()
            response_data = response.json()
            
            # Parse and download the first image
            first_image = (
                response_data.get("data", [{}])[0] if isinstance(response_data.get("data"), list) else {}
            )
            image_url = first_image.get("url")
            if not image_url:
                raise Exception(f"No image URL returned. Response: {response_data}")
            
            # Download the image with retry logic
            for attempt in range(3):
                try:
                    img_resp = requests.get(image_url, timeout=60)
                    img_resp.raise_for_status()
                    break
                except requests.exceptions.RequestException:
                    if attempt < 2:  # Don't sleep on the last attempt
                        time.sleep(2)
                    else:
                        raise Exception("Failed to download image after retries.")
            
            # Save the image
            with open(output_path, "wb") as f:
                f.write(img_resp.content)
            
            return str(output_path)
            
        except requests.exceptions.HTTPError as e:
            # Include response content for better debugging
            error_msg = f"HTTP Error: {e}"
            try:
                if hasattr(e.response, 'text'):
                    error_msg += f"\nResponse: {e.response.text}"
            except:
                pass
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request Error: {e}")
        except Exception as e:
            raise Exception(f"Unexpected Error: {str(e)}")
    
    def generate_book_page_image(
        self,
        image_prompt_data: Dict[str, Any],
        page_number: int,
        output_dir: Path,
        reference_image_path: Optional[Path] = None,
        characters_data: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Generate an image for a specific book page.
        
        Args:
            image_prompt_data: Structured image prompt data from OpenAI
            page_number: Page number for file naming
            output_dir: Directory to save the image
            reference_image_path: Optional reference image for style consistency
            characters_data: Optional list of character data for consistency
            
        Returns:
            Path to the generated image file
        """
        # Extract the main prompt
        main_prompt = image_prompt_data.get("image_prompt", "")
        
        # Add character consistency formulas if available
        if characters_data:
            character_consistency = []
            for char_data in characters_data:
                consistency_formula = char_data.get("consistency_formula", "")
                if consistency_formula:
                    character_consistency.append(consistency_formula)
                
                # Also add ideogram_character_seed for extra consistency
                seed_description = char_data.get("ideogram_character_seed", "")
                if seed_description:
                    character_consistency.append(seed_description)
            
            if character_consistency:
                main_prompt += f" Character consistency: {', '.join(character_consistency)}."
        
        # Add style specifications if available
        style_specs = image_prompt_data.get("style_specifications", "")
        if style_specs:
            main_prompt += f" {style_specs}"
        
        # Add composition notes if available
        composition = image_prompt_data.get("composition_notes", "")
        if composition:
            main_prompt += f" {composition}"
        
        # Enhance prompt for children's book style
        main_prompt += " Children's book illustration, bright colors, friendly and engaging, high quality digital art"
        
        # Add style anchors from characters if available
        if characters_data:
            style_anchors = []
            for char_data in characters_data:
                char_anchors = char_data.get("style_anchors", [])
                style_anchors.extend(char_anchors)
            
            if style_anchors:
                unique_anchors = list(set(style_anchors))  # Remove duplicates
                main_prompt += f", {', '.join(unique_anchors)}"
        
        # Determine output filename
        output_filename = f"page_{page_number:02d}.png"
        output_path = output_dir / output_filename
        
        # Generate the image
        return self.generate_image(
            prompt=main_prompt,
            output_path=output_path,
            style_reference_image_path=reference_image_path,
            aspect_ratio="1x1",  # Square format for book pages
            style_type="DESIGN"  # Good for children's book illustrations
        )
    
    def generate_book_cover(
        self,
        title: str,
        characters: List[Dict[str, Any]],
        theme: str,
        output_dir: Path,
        reference_image_path: Optional[Path] = None
    ) -> str:
        """
        Generate a cover image for the book.
        
        Args:
            title: Book title
            characters: List of main characters
            theme: Book theme/genre
            output_dir: Directory to save the cover
            reference_image_path: Optional reference image for style consistency
            
        Returns:
            Path to the generated cover image file
        """
        # Create cover prompt
        main_characters = [char for char in characters if char.get("character_type") == "main"]
        
        cover_prompt = f"Children's book cover illustration for '{title}', "
        
        # Add character descriptions using new structure
        if main_characters:
            char_descriptions = []
            character_consistency = []
            style_anchors = []
            
            for char in main_characters:
                # Use consistency formula for main description
                consistency_formula = char.get("consistency_formula", "")
                if consistency_formula:
                    character_consistency.append(consistency_formula)
                
                # Get ideogram seed for additional details
                seed_description = char.get("ideogram_character_seed", "")
                if seed_description:
                    char_descriptions.append(seed_description)
                
                # Collect style anchors
                char_anchors = char.get("style_anchors", [])
                style_anchors.extend(char_anchors)
                
                # Fallback to physical description if new fields not available
                if not consistency_formula and not seed_description:
                    phys_desc = char.get("physical_description", {})
                    exact_colors = phys_desc.get("exact_colors", {})
                    char_name = char.get("character_name", "character")
                    species = char.get("species", "character")
                    
                    # Build description from exact colors
                    color_desc = ""
                    if exact_colors:
                        primary = exact_colors.get("primary", "")
                        secondary = exact_colors.get("secondary", "")
                        details = exact_colors.get("details", "")
                        color_desc = f"{primary} {secondary} {details}".strip()
                    
                    size = phys_desc.get("size", "")
                    distinctive = phys_desc.get("distinctive_features", [])
                    
                    desc_parts = [char_name, species, size, color_desc]
                    if distinctive:
                        desc_parts.extend(distinctive[:2])  # Limit to 2 features
                    
                    char_descriptions.append(", ".join(filter(None, desc_parts)))
            
            # Add character consistency to prompt
            if character_consistency:
                cover_prompt += f"Characters: {', '.join(character_consistency)}, "
            elif char_descriptions:
                cover_prompt += f"featuring {', '.join(char_descriptions)}, "
            
            # Add style anchors
            if style_anchors:
                unique_anchors = list(set(style_anchors))  # Remove duplicates
                cover_prompt += f"art style: {', '.join(unique_anchors)}, "
        
        cover_prompt += (
            f"theme: {theme}, bright and colorful children's book illustration style, "
            f"engaging and friendly, high quality, professional book cover design, "
            f"title space at top, appealing to children"
        )
        
        # Determine output filename
        output_filename = "cover.png"
        output_path = output_dir / output_filename
        
        # Generate the cover
        return self.generate_image(
            prompt=cover_prompt,
            output_path=output_path,
            style_reference_image_path=reference_image_path,
            aspect_ratio="3x4",  # Portrait format for book cover
            style_type="DESIGN"
        )

