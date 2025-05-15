# agents/image_creator_agent.py
from .base_agent import BaseBookAgent
from smolagents import InferenceClientModel # Ensure InferenceClientModel is imported for type hinting
from typing import List, Dict, Any, Optional
from data_models.book_plan import BookPlan
from data_models.story_content import StoryContent, ImagePlaceholder
from data_models.generated_image import GeneratedImage
import os
import uuid
import requests
from PIL import Image as PilImage, ImageDraw, ImageFont
from openai import OpenAI
import time

class ImageCreatorAgent(BaseBookAgent):
    """Agent responsible for generating images for the book, including the cover."""

    def __init__(self, model: InferenceClientModel, project_id: str, output_dir: str, tools: List[Any] = None, **kwargs):
        """
        Initializes the ImageCreatorAgent.

        Args:
            model (InferenceClientModel): An instantiated language model client.
            project_id (str): The unique identifier for the current book project.
            output_dir (str): The base directory where images for this project will be saved.
            tools (List[Any], optional): List of tools for the agent. Defaults to an empty list.
            **kwargs: Additional arguments for CodeAgent.
        """
        agent_tools = tools if tools is not None else []
        super().__init__(
            model=model, # Pass the model instance directly
            tools=agent_tools,
            system_prompt_path="/home/federico/Desktop/personal/book_publishing_api/prompts/image_creator_prompts.yaml",
            **kwargs
        )
        self.project_id = project_id
        self.project_output_dir = os.path.join(output_dir, project_id, "images")
        os.makedirs(self.project_output_dir, exist_ok=True)
        
        # Initialize OpenAI client
        # Make sure to set OPENAI_API_KEY environment variable
        self.openai_client = OpenAI(
            api_key="openai-api-key"
        )
        
        # Configuration for DALL-E
        self.dalle_model = "dall-e-3"  # Options: "dall-e-2" or "dall-e-3"
        self.dalle_size = "1024x1024"  # Options: "256x256", "512x512", "1024x1024" for DALL-E 2
                                       # or "1024x1024", "1024x1792", "1792x1024" for DALL-E 3
        self.dalle_quality = "standard"  # Options: "standard" or "hd" (DALL-E 3 only)
        self.dalle_style = "natural"     # Options: "natural" or "vivid" (DALL-E 3 only)

    def _resize_image_for_pdf(self, image_path: str, is_cover: bool = False):
        """
        Resize image to appropriate dimensions for PDF layout.
        
        Args:
            image_path (str): Path to the image file
            is_cover (bool): True if this is a cover image
        """
        try:
            with PilImage.open(image_path) as img:
                # Define maximum dimensions based on PDF layout
                # These values are in pixels and should fit well in typical PDF layouts
                if is_cover:
                    # Cover images can be larger
                    max_width = 800
                    max_height = 1000
                else:
                    # Chapter images should be smaller to fit in the text flow
                    max_width = 600
                    max_height = 400
                
                # Calculate aspect ratio
                aspect_ratio = img.width / img.height
                
                # Determine new dimensions while maintaining aspect ratio
                if aspect_ratio > 1:  # Landscape
                    new_width = min(max_width, img.width)
                    new_height = int(new_width / aspect_ratio)
                    if new_height > max_height:
                        new_height = max_height
                        new_width = int(new_height * aspect_ratio)
                else:  # Portrait or square
                    new_height = min(max_height, img.height)
                    new_width = int(new_height * aspect_ratio)
                    if new_width > max_width:
                        new_width = max_width
                        new_height = int(new_width / aspect_ratio)
                
                # Only resize if the image is larger than the target dimensions
                if img.width > new_width or img.height > new_height:
                    # Use high-quality resampling
                    resized_img = img.resize((new_width, new_height), PilImage.Resampling.LANCZOS)
                    resized_img.save(image_path, "PNG", quality=95, optimize=True)
                    print(f"ImageCreatorAgent: Resized image from {img.width}x{img.height} to {new_width}x{new_height}")
                else:
                    print(f"ImageCreatorAgent: Image size {img.width}x{img.height} is already appropriate, no resizing needed")
                    
        except Exception as e:
            print(f"ImageCreatorAgent: Error resizing image {image_path}: {e}")

    def _generate_single_image(self, placeholder_id: str, prompt: str, style_guide: str, is_cover: bool = False) -> Optional[GeneratedImage]:
        """
        Generates a single image using OpenAI DALL-E.

        Args:
            placeholder_id (str): The ID for this image (e.g., "chapter1_image1", "cover").
            prompt (str): The prompt for image generation.
            style_guide (str): The style guide for the image.
            is_cover (bool): True if this is the cover image.

        Returns:
            Optional[GeneratedImage]: GeneratedImage object or None if failed.
        """
        filename_base = placeholder_id.replace(" ", "_").lower()
        unique_suffix = uuid.uuid4().hex[:6]
        image_filename = f"{filename_base}_{unique_suffix}.png"
        output_path = os.path.join(self.project_output_dir, image_filename)

        # Combine prompt with style guide for better results
        enhanced_prompt = f"{prompt}. Style: {style_guide}"
        
        # Limit prompt length (DALL-E has a 4000 character limit)
        if len(enhanced_prompt) > 4000:
            enhanced_prompt = enhanced_prompt[:3997] + "..."
        
        print(f"ImageCreatorAgent: Generating image for ID '{placeholder_id}' with DALL-E")
        print(f"Enhanced prompt: {enhanced_prompt}")

        try:
            # Generate image with DALL-E
            response = self.openai_client.images.generate(
                model=self.dalle_model,
                prompt=enhanced_prompt,
                size=self.dalle_size,
                quality=self.dalle_quality if self.dalle_model == "dall-e-3" else None,
                style=self.dalle_style if self.dalle_model == "dall-e-3" else None,
                n=1,  # Number of images to generate
            )
            
            # Get the image URL from the response
            image_url = response.data[0].url
            
            # Download the image
            image_response = requests.get(image_url, timeout=30)
            image_response.raise_for_status()
            
            # Save the image
            with open(output_path, 'wb') as f:
                f.write(image_response.content)
            
            # Resize image for PDF compatibility
            self._resize_image_for_pdf(output_path, is_cover)
            
            # Verify the image was saved correctly
            try:
                with PilImage.open(output_path) as img:
                    img.verify()
            except Exception as e:
                print(f"ImageCreatorAgent: Warning - Image verification failed for '{placeholder_id}': {e}")
            
            print(f"ImageCreatorAgent: Successfully generated image for '{placeholder_id}' at {output_path}")
            return GeneratedImage(placeholder_id=placeholder_id, prompt_used=enhanced_prompt, image_path=output_path)
            
        except Exception as e:
            print(f"ImageCreatorAgent: Error generating image for '{placeholder_id}': {e}")
            
            # Create a fallback placeholder image if DALL-E fails
            print(f"ImageCreatorAgent: Creating fallback placeholder image for '{placeholder_id}'")
            return self._create_fallback_image(placeholder_id, prompt, style_guide, output_path, is_cover)

    def _create_fallback_image(self, placeholder_id: str, prompt: str, style_guide: str, output_path: str, is_cover: bool = False) -> Optional[GeneratedImage]:
        """
        Creates a fallback placeholder image when DALL-E generation fails.
        
        Args:
            placeholder_id (str): The ID for this image.
            prompt (str): The original prompt.
            style_guide (str): The style guide.
            output_path (str): Where to save the image.
            is_cover (bool): True if this is a cover image.
            
        Returns:
            Optional[GeneratedImage]: GeneratedImage object or None if failed.
        """
        try:
            # Use appropriate dimensions for PDF
            if is_cover:
                img_width = 800
                img_height = 1000
            else:
                img_width = 600
                img_height = 400
                
            img = PilImage.new("RGB", (img_width, img_height), color="lightgrey")
            draw = ImageDraw.Draw(img)
            
            # Try to load a font, use default if not found
            try:
                font = ImageFont.truetype("arial.ttf", 24)
                small_font = ImageFont.truetype("arial.ttf", 16)
            except IOError:
                font = ImageFont.load_default()
                small_font = font
            
            # Draw text
            title = f"Fallback Image"
            subtitle = f"ID: {placeholder_id}"
            prompt_text = f"Prompt: {prompt[:100]}..."
            style_text = f"Style: {style_guide[:100]}..."
            
            # Calculate positions
            title_bbox = draw.textbbox((0, 0), title, font=font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (img_width - title_width) / 2
            
            draw.text((title_x, 100), title, fill="red", font=font)
            draw.text((50, 200), subtitle, fill="black", font=small_font)
            draw.text((50, 250), prompt_text, fill="black", font=small_font)
            draw.text((50, 300), style_text, fill="black", font=small_font)
            
            img.save(output_path, "PNG")
            print(f"ImageCreatorAgent: Created fallback image for '{placeholder_id}'")
            return GeneratedImage(placeholder_id=placeholder_id, prompt_used=prompt, image_path=output_path)
            
        except Exception as e:
            print(f"ImageCreatorAgent: Error creating fallback image for '{placeholder_id}': {e}")
            return None

    def create_images(self, story_content: StoryContent, book_plan: BookPlan) -> List[GeneratedImage]:
        """
        Generates all images required for the book, including chapter illustrations and the cover.

        Args:
            story_content (StoryContent): The story content with image placeholders and descriptions.
            book_plan (BookPlan): The book plan containing style guides and cover concept.

        Returns:
            List[GeneratedImage]: A list of GeneratedImage objects for all created images.
        """
        generated_images = []
        image_style = book_plan.image_style_guide

        # Generate chapter images
        for i, placeholder in enumerate(story_content.all_image_placeholders):
            print(f"ImageCreatorAgent: Processing placeholder {i+1}/{len(story_content.all_image_placeholders)}: {placeholder.id}")
            
            # Add a small delay between requests to avoid rate limiting
            if i > 0:
                time.sleep(1)
            
            img = self._generate_single_image(placeholder.id, placeholder.description, image_style)
            if img:
                generated_images.append(img)
        
        # Generate cover image
        print(f"ImageCreatorAgent: Processing cover image with concept: '{book_plan.cover_concept}'")
        
        # Add delay before cover generation
        if story_content.all_image_placeholders:
            time.sleep(1)
        
        # Use a larger size for cover if using DALL-E 3
        original_size = self.dalle_size
        is_cover = True  # This is the cover image generation
        if is_cover and self.dalle_model == "dall-e-3":
            self.dalle_size = "1024x1792"  # Portrait orientation for book cover
        
        cover_img = self._generate_single_image("cover", book_plan.cover_concept, image_style, is_cover=True)
        
        # Restore original size setting
        self.dalle_size = original_size
        
        if cover_img:
            generated_images.append(cover_img)
            
        print(f"ImageCreatorAgent: Finished image generation. Total images: {len(generated_images)}")
        return generated_images

    def set_dalle_configuration(self, model: str = None, size: str = None, quality: str = None, style: str = None):
        """
        Update DALL-E configuration settings.
        
        Args:
            model (str): DALL-E model to use ("dall-e-2" or "dall-e-3")
            size (str): Image size
            quality (str): Image quality ("standard" or "hd", DALL-E 3 only)
            style (str): Image style ("natural" or "vivid", DALL-E 3 only)
        """
        if model:
            self.dalle_model = model
        if size:
            self.dalle_size = size
        if quality:
            self.dalle_quality = quality
        if style:
            self.dalle_style = style
        
        print(f"DALL-E configuration updated: model={self.dalle_model}, size={self.dalle_size}, quality={self.dalle_quality}, style={self.dalle_style}")