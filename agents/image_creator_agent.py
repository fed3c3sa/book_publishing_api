# agents/image_creator_agent.py
from .base_agent import BaseBookAgent
from smolagents import InferenceClientModel # Ensure InferenceClientModel is imported for type hinting
from typing import List, Dict, Any, Optional
from data_models.book_plan import BookPlan
from data_models.story_content import StoryContent, ImagePlaceholder
from data_models.generated_image import GeneratedImage
import os
import uuid
from PIL import Image as PilImage, ImageDraw, ImageFont

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
            system_prompt_path="/home/ubuntu/book_writing_agent/prompts/image_creator_prompts.yaml",
            **kwargs
        )
        self.project_id = project_id
        self.project_output_dir = os.path.join(output_dir, project_id, "images")
        os.makedirs(self.project_output_dir, exist_ok=True)

    def _generate_single_image(self, placeholder_id: str, prompt: str, style_guide: str, is_cover: bool = False) -> Optional[GeneratedImage]:
        """
        Generates a single image (or simulates generation).

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

        print(f"ImageCreatorAgent: Preparing to generate image for ID \t'{placeholder_id}'\t with prompt: \t'{prompt}'\t and style: \t'{style_guide}'\t")

        # In a real scenario, the agent would use self.execute() to call an image generation tool.
        # The tool would be responsible for interacting with an image generation API/model.
        # For this placeholder, we simulate the tool call and file creation.
        # Example of how it might be structured if using self.execute() and a tool:
        # tool_call_prompt = f"Use the image_generation_tool to create an image with prompt 	'{prompt}	', style 	'{style_guide}	', and save it as 	'{image_filename}	' in directory 	'{self.project_output_dir}	'."
        # tool_response = self.execute(tool_call_prompt) # This would trigger the tool if correctly set up.
        # output_path = tool_response # Assuming the tool returns the path.

        # Direct simulation of the tool's effect for now:
        output_path = os.path.join(self.project_output_dir, image_filename)
        try:
            # Create a simple placeholder image using Pillow (PIL)
            img_width = 600
            img_height = 400
            img = PilImage.new("RGB", (img_width, img_height), color = "lightgrey")
            draw = ImageDraw.Draw(img)
            
            # Try to load a font, use default if not found
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                font = ImageFont.load_default()
            
            text = f"Placeholder for: {placeholder_id}\nPrompt: {prompt[:50]}...\nStyle: {style_guide[:50]}..."
            
            # Calculate text position (simple centering)
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = (img_width - text_width) / 2
            text_y = (img_height - text_height) / 2
            
            draw.text((text_x, text_y), text, fill="black", font=font)
            img.save(output_path, "PNG")
            print(f"ImageCreatorAgent: Successfully simulated image generation for \t'{placeholder_id}'\t at {output_path}")
            return GeneratedImage(placeholder_id=placeholder_id, prompt_used=prompt, image_path=output_path)
        except Exception as e:
            print(f"ImageCreatorAgent: Error simulating image generation for \t'{placeholder_id}'\t : {e}")
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
        for placeholder in story_content.all_image_placeholders:
            print(f"ImageCreatorAgent: Processing placeholder: {placeholder.id} - \t'{placeholder.description}'\t")
            img = self._generate_single_image(placeholder.id, placeholder.description, image_style)
            if img:
                generated_images.append(img)
        
        # Generate cover image
        print(f"ImageCreatorAgent: Processing cover image with concept: \t'{book_plan.cover_concept}'\t")
        cover_img = self._generate_single_image("cover", book_plan.cover_concept, image_style, is_cover=True)
        if cover_img:
            generated_images.append(cover_img)
            
        print(f"ImageCreatorAgent: Finished image generation. Total images: {len(generated_images)}")
        return generated_images

