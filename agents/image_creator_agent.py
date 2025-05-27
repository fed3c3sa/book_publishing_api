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
        self.style_reference_image_path = None  # Track the first generated image

    def _run_with_retry(self, prompt: str, additional_args: Dict[str, Any], max_retries: int = 3) -> Any:
        """
        Runs self.run() with retry logic.
        
        Args:
            prompt (str): The prompt to send to the agent
            additional_args (Dict[str, Any]): Additional arguments for the run method
            max_retries (int): Maximum number of retry attempts (default: 3)
            
        Returns:
            Any: The result from self.run() if successful, None if all attempts fail
        """
        for attempt in range(max_retries):
            try:
                result = self.run(prompt, additional_args=additional_args)
                
                # Check if the result is valid (image path exists)
                if isinstance(result, str) and os.path.exists(result):
                    return result
                else:
                    print(f"ImageCreatorAgent: Attempt {attempt + 1}/{max_retries} failed - invalid result")
                    
            except Exception as e:
                print(f"ImageCreatorAgent: Attempt {attempt + 1}/{max_retries} failed with error: {str(e)}")
            
            # Add delay between retries (except for the last failed attempt)
            if attempt < max_retries - 1:
                time.sleep(2)
        
        return None

    def create_images(self, story_content: StoryContent, book_plan: BookPlan) -> List[GeneratedImage]:
        """
        Generates all images required for the book, including chapter illustrations and the cover.
        The first generated image is used as a style reference for all subsequent images.

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
            
            # Prepare additional args
            additional_args = {
                'image_id': placeholder.id,
                'is_cover': False
            }
            
            # Add style reference if we have one (after first image)
            if self.style_reference_image_path:
                additional_args['style_reference_image_path'] = self.style_reference_image_path
                print(f"ImageCreatorAgent: Using style reference from first image")
            
            # Use the agent to generate the image with retry logic
            result = self._run_with_retry(
                f"Generate an image for this description: {placeholder.description}. Style: {image_style}",
                additional_args=additional_args
            )
            
            # Check if image generation was successful after all retries
            if result is not None:
                # If this is the first image, save it as style reference
                if i == 0 and not self.style_reference_image_path:
                    self.style_reference_image_path = result
                    print(f"ImageCreatorAgent: First image generated, will use as style reference: {result}")
                
                generated_images.append(GeneratedImage(
                    placeholder_id=placeholder.id, 
                    prompt_used=f"{placeholder.description}. Style: {image_style}", 
                    image_path=result
                ))
            else:
                print(f"ImageCreatorAgent: Skipping failed image generation for placeholder '{placeholder.id}' after 3 attempts")
        
        # Generate cover image
        print(f"ImageCreatorAgent: Processing cover image with concept: '{book_plan.cover_concept}'")
        
        # Add delay before cover generation
        if story_content.all_image_placeholders:
            time.sleep(1)
        
        # Prepare additional args for cover
        cover_additional_args = {
            'image_id': 'cover',
            'is_cover': True
        }
        
        # Add style reference if we have one
        if self.style_reference_image_path:
            cover_additional_args['style_reference_image_path'] = self.style_reference_image_path
            print(f"ImageCreatorAgent: Using style reference for cover image")
        
        # Generate cover image with retry logic
        cover_result = self._run_with_retry(
            f"Generate a book cover image for this concept: {book_plan.cover_concept}. Style: {image_style}",
            additional_args=cover_additional_args
        )
        
        # Check if cover image generation was successful after all retries
        if cover_result is not None:
            generated_images.append(GeneratedImage(
                placeholder_id="cover", 
                prompt_used=f"{book_plan.cover_concept}. Style: {image_style}", 
                image_path=cover_result
            ))
        else:
            print(f"ImageCreatorAgent: Warning: Cover image generation failed after 3 attempts")
            
        print(f"ImageCreatorAgent: Finished image generation. Total images successfully created: {len(generated_images)}")
        return generated_images