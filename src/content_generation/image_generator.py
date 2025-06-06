"""
Image generation module for the Children's Book Generator.

This module handles creating detailed prompts for image generation and
coordinating with the Ideogram API to generate consistent book illustrations.
"""

import json
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from ..ai_clients.openai_client import OpenAIClient
from ..ai_clients.ideogram_client import IdeogramClient
from ..utils.config import load_prompt, get_output_path, IMAGES_DIR


class ImageGenerator:
    """Handles image prompt generation and image creation for book pages."""
    
    def __init__(
        self,
        openai_client: Optional[OpenAIClient] = None,
        ideogram_client: Optional[IdeogramClient] = None
    ):
        """
        Initialize the image generator.
        
        Args:
            openai_client: OpenAI client instance. If None, creates a new one.
            ideogram_client: Ideogram client instance. If None, creates a new one.
        """
        self.openai_client = openai_client or OpenAIClient()
        self.ideogram_client = ideogram_client or IdeogramClient()
        self.image_prompt_template = load_prompt("image_generation")
        
        # Track reference image for consistency
        self.reference_image_path = None
    
    def generate_image_prompt(
        self,
        page_data: Dict[str, Any],
        characters: List[Dict[str, Any]],
        art_style: str = "children's book illustration, colorful, friendly"
    ) -> Dict[str, Any]:
        """
        Generate a detailed prompt for image generation based on page data.
        
        Args:
            page_data: Page information from book plan
            characters: List of all character descriptions
            art_style: Desired art style for the illustration
            
        Returns:
            Structured image prompt data
        """
        # Extract page information
        page_description = page_data.get("scene_description", "")
        characters_present = page_data.get("characters_present", [])
        mood_tone = page_data.get("mood_tone", "happy and engaging")
        visual_elements = page_data.get("visual_elements", [])
        
        # Get character descriptions for characters present on this page
        relevant_characters = {}
        for char in characters:
            char_name = char.get("character_name", "")
            if char_name in characters_present:
                relevant_characters[char_name] = char
        
        # Generate image prompt using OpenAI
        image_prompt_data = self.openai_client.generate_image_prompt(
            page_description=page_description,
            characters_present=characters_present,
            character_descriptions=relevant_characters,
            mood_tone=mood_tone,
            visual_elements=visual_elements,
            art_style=art_style,
            prompt_template=self.image_prompt_template
        )
        
        # Add page metadata
        image_prompt_data["page_metadata"] = {
            "page_number": page_data.get("page_number", 0),
            "page_type": page_data.get("page_type", "story"),
            "characters_present": characters_present
        }
        
        return image_prompt_data
    
    def generate_page_image(
        self,
        page_data: Dict[str, Any],
        characters: List[Dict[str, Any]],
        book_title: str = "",
        art_style: str = "children's book illustration, colorful, friendly",
        use_reference: bool = True
    ) -> str:
        """
        Generate an image for a specific book page.
        
        Args:
            page_data: Page information from book plan
            characters: List of all character descriptions
            book_title: Book title for file organization
            art_style: Desired art style for the illustration
            use_reference: Whether to use reference image for consistency
            
        Returns:
            Path to the generated image file
        """
        # Generate image prompt
        image_prompt_data = self.generate_image_prompt(
            page_data=page_data,
            characters=characters,
            art_style=art_style
        )
        
        # Save image prompt data
        page_number = page_data.get("page_number", 0)
        prompt_filename = f"page_{page_number:02d}_prompt.json"
        prompt_path = self._save_image_prompt(image_prompt_data, book_title, prompt_filename)
        
        # Create output directory for this book
        book_images_dir = self._get_book_images_dir(book_title)
        
        # Generate the image using Ideogram
        reference_image = self.reference_image_path if use_reference else None
        
        image_path = self.ideogram_client.generate_book_page_image(
            image_prompt_data=image_prompt_data,
            page_number=page_number,
            output_dir=book_images_dir,
            reference_image_path=reference_image,
            characters_data=characters
        )
        
        # Set reference image for future pages if this is the first generated image
        if self.reference_image_path is None and Path(image_path).exists():
            self.reference_image_path = Path(image_path)
        
        return image_path
    
    def generate_book_cover(
        self,
        book_plan: Dict[str, Any],
        characters: List[Dict[str, Any]],
        art_style: str = "children's book cover, professional, engaging"
    ) -> str:
        """
        Generate a cover image for the book.
        
        Args:
            book_plan: Complete book plan data
            characters: List of all character descriptions
            art_style: Desired art style for the cover
            
        Returns:
            Path to the generated cover image file
        """
        book_title = book_plan.get("book_title", "Untitled Book")
        themes = book_plan.get("themes", [])
        theme_str = ", ".join(themes) if themes else "adventure and friendship"
        
        # Create output directory for this book
        book_images_dir = self._get_book_images_dir(book_title)
        
        # Generate cover using Ideogram
        cover_path = self.ideogram_client.generate_book_cover(
            title=book_title,
            characters=characters,
            theme=theme_str,
            output_dir=book_images_dir,
            reference_image_path=self.reference_image_path
        )
        
        return cover_path
    
    def generate_all_page_images(
        self,
        book_plan: Dict[str, Any],
        characters: List[Dict[str, Any]],
        art_style: str = "children's book illustration, colorful, friendly",
        include_cover: bool = True
    ) -> Dict[int, str]:
        """
        Generate images for all pages in the book.
        
        Args:
            book_plan: Complete book plan data
            characters: List of all character descriptions
            art_style: Desired art style for illustrations
            include_cover: Whether to generate a cover image
            
        Returns:
            Dictionary mapping page numbers to image file paths
        """
        book_title = book_plan.get("book_title", "Untitled Book")
        pages = book_plan.get("pages", [])
        
        generated_images = {}
        
        # Generate cover if requested
        if include_cover:
            try:
                cover_path = self.generate_book_cover(book_plan, characters, art_style)
                generated_images[0] = cover_path  # Cover is page 0
                print(f"Generated cover: {cover_path}")
            except Exception as e:
                print(f"Error generating cover: {str(e)}")
        
        # Generate images for each page
        for page_data in pages:
            page_number = page_data.get("page_number", 0)
            page_type = page_data.get("page_type", "story")
            
            # Skip cover page if we already generated it separately
            if page_type == "cover" and include_cover:
                continue
            
            try:
                image_path = self.generate_page_image(
                    page_data=page_data,
                    characters=characters,
                    book_title=book_title,
                    art_style=art_style
                )
                generated_images[page_number] = image_path
                print(f"Generated image for page {page_number}: {image_path}")
                
            except Exception as e:
                print(f"Error generating image for page {page_number}: {str(e)}")
                continue
        
        return generated_images
    
    def _save_image_prompt(
        self,
        image_prompt_data: Dict[str, Any],
        book_title: str,
        filename: str
    ) -> Path:
        """
        Save image prompt data to a JSON file.
        
        Args:
            image_prompt_data: Image prompt data dictionary
            book_title: Book title for organization
            filename: Name of the file to save
            
        Returns:
            Path to the saved file
        """
        # Create book-specific directory
        book_prompts_dir = self._get_book_images_dir(book_title) / "prompts"
        book_prompts_dir.mkdir(parents=True, exist_ok=True)
        
        # Save prompt data
        output_path = book_prompts_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(image_prompt_data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def _get_book_images_dir(self, book_title: str) -> Path:
        """
        Get the images directory for a specific book.
        
        Args:
            book_title: Book title
            
        Returns:
            Path to the book's images directory
        """
        # Clean book title for directory name
        clean_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_title = clean_title.replace(' ', '_').lower()
        
        book_images_dir = IMAGES_DIR / clean_title
        book_images_dir.mkdir(parents=True, exist_ok=True)
        
        return book_images_dir
    
    def set_reference_image(self, image_path: Union[str, Path]) -> None:
        """
        Set a reference image for style consistency.
        
        Args:
            image_path: Path to the reference image
        """
        self.reference_image_path = Path(image_path)
    
    def clear_reference_image(self) -> None:
        """Clear the current reference image."""
        self.reference_image_path = None

