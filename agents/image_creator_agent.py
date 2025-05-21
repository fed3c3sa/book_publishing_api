# agents/image_creator_agent.py
from .base_agent import BaseBookAgent
from smolagents import InferenceClientModel
from typing import List, Dict, Any, Optional
from data_models.book_plan import BookPlan
from data_models.story_content import StoryContent
from data_models.generated_image import GeneratedImage
import os
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
            **kwargs: Additional arguments for BaseBookAgent.
        """
        # Ensure tools is a list, even if None is passed
        agent_tools = tools if tools is not None else []
        
        super().__init__(
            model=model,
            tools=agent_tools,
            system_prompt_path="/home/federico/Desktop/personal/book_publishing_api/prompts/image_creator_prompts.yaml",
            **kwargs
        )
        self.project_id = project_id
        self.project_output_dir = os.path.join(output_dir, project_id, "images")
        os.makedirs(self.project_output_dir, exist_ok=True)

    def create_images(self, story_content: StoryContent, book_plan: BookPlan) -> List[GeneratedImage]:
        """
        Generates all images required for the book, including chapter illustrations and the cover.

        Args:
            story_content (StoryContent): The story content with image placeholders and descriptions.
            book_plan (BookPlan): The book plan containing style guides and cover concept.

        Returns:
            List[GeneratedImage]: A list of GeneratedImage objects for all successfully created images.
        """
        generated_images = []
        image_style = book_plan.image_style_guide
        
        # Find the image generation tool from the tools list
        image_generator = None
        for tool in self.tools:
            if "image_generator" in tool:
                image_generator = tool
                break
        
        if not image_generator:
            print("ImageCreatorAgent: Error - Image generation tool not found in tools list")
            return []

        # Generate chapter images
        for i, placeholder in enumerate(story_content.all_image_placeholders):
            print(f"ImageCreatorAgent: Processing placeholder {i+1}/{len(story_content.all_image_placeholders)}: {placeholder.id}")
            
            # Add a small delay between requests to avoid rate limiting
            if i > 0:
                time.sleep(1)
            
            # Use the agent to generate the image
            result = self.run(
                f"Generate an image for this description: {placeholder.description}. Style: {image_style}",
                additional_args={
                    'image_id': placeholder.id,
                    'is_cover': False
                }
            )
            
            # Check if image generation was successful
            if isinstance(result, str) and os.path.exists(result):
                generated_images.append(GeneratedImage(
                    placeholder_id=placeholder.id, 
                    prompt_used=f"{placeholder.description}. Style: {image_style}", 
                    image_path=result
                ))
            else:
                print(f"ImageCreatorAgent: Skipping failed image generation for placeholder '{placeholder.id}'")
        
        # Generate cover image
        print(f"ImageCreatorAgent: Processing cover image with concept: '{book_plan.cover_concept}'")
        
        # Add delay before cover generation
        if story_content.all_image_placeholders:
            time.sleep(1)
        
        # Generate cover image
        cover_result = self.run(
            f"Generate a book cover image for this concept: {book_plan.cover_concept}. Style: {image_style}",
            additional_args={
                'image_id': 'cover',
                'is_cover': True
            }
        )
        
        # Check if cover image generation was successful
        if isinstance(cover_result, str) and os.path.exists(cover_result):
            generated_images.append(GeneratedImage(
                placeholder_id="cover", 
                prompt_used=f"{book_plan.cover_concept}. Style: {image_style}", 
                image_path=cover_result
            ))
        else:
            print(f"ImageCreatorAgent: Warning: Cover image generation failed")
            
        print(f"ImageCreatorAgent: Finished image generation. Total images successfully created: {len(generated_images)}")
        return generated_images
