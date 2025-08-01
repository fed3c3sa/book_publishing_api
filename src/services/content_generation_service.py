"""
Content generation service implementation.

This service handles image and text generation for book pages,
coordinating between AI clients and managing the generation workflow.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path

from ..interfaces.content_generation_interface import ContentGenerationInterface
from ..interfaces.ai_client_interface import AIClientInterface
from ..domain.models import BookPlan, Character, TextData, ImagePromptData
from ..exceptions import ContentGenerationError, ImageGenerationError, TextGenerationError
from ..utils.config import IMAGES_DIR, TEXTS_DIR, get_output_path
from ..prompts.prompt_manager import PromptManager


class StoryContext:
    """Simple story context tracking for text generation consistency."""
    
    def __init__(self):
        self.story_summary = ""
        self.character_states = {}
        self.page_summaries = []
        self.mood_progression = []
    
    def update_from_page(self, page_data: dict, generated_text: dict, book_plan: BookPlan):
        """Update context from a newly generated page."""
        page_number = page_data.get("page_number", 0)
        page_text = generated_text.get("page_text", "")
        
        # Update page summaries
        scene_description = page_data.get("scene_description", "")
        page_summary = f"Page {page_number}: {scene_description}"
        self.page_summaries.append(page_summary)
        
        # Keep last 3 summaries for context
        recent_summaries = self.page_summaries[-3:]
        self.story_summary = " -> ".join(recent_summaries)
    
    def get_context_for_generation(self) -> str:
        """Generate context string for AI generation."""
        context_parts = []
        
        if self.story_summary:
            context_parts.append(f"Story so far: {self.story_summary}")
        
        return " | ".join(context_parts)


class ContentGenerationService(ContentGenerationInterface):
    """
    Content generation service implementation.
    
    This service coordinates image and text generation for book pages,
    ensuring consistency and quality across all content.
    """
    
    def __init__(
        self,
        ai_client: AIClientInterface,
        image_client: Optional[Any] = None,  # Ideogram client
        prompt_manager: Optional[PromptManager] = None
    ):
        """
        Initialize the content generation service.
        
        Args:
            ai_client: AI client for text and prompt generation
            image_client: Image generation client (Ideogram)
            prompt_manager: Prompt manager for loading templates
        """
        self.ai_client = ai_client
        self.image_client = image_client
        self.prompt_manager = prompt_manager or PromptManager()
        self._text_prompt = None
        self._image_prompt = None
        self.reference_image_path = None
    
    @property
    def text_generation_prompt(self) -> str:
        """Get the text generation prompt template."""
        if self._text_prompt is None:
            self._text_prompt = self.prompt_manager.get_text_generation_prompt()
        return self._text_prompt
    
    @property
    def image_generation_prompt(self) -> str:
        """Get the image generation prompt template."""
        if self._image_prompt is None:
            self._image_prompt = self.prompt_manager.get_image_generation_prompt()
        return self._image_prompt
    
    def generate_page_image(
        self,
        page_data: dict,
        characters: List[Character],
        book_title: str = "",
        art_style: str = "children's book illustration",
        use_reference: bool = True
    ) -> str:
        """
        Generate an image for a specific book page.
        
        Args:
            page_data: Page information from book plan
            characters: List of character models
            book_title: Book title for file organization
            art_style: Desired art style
            use_reference: Whether to use reference image for consistency
            
        Returns:
            Path to generated image file
            
        Raises:
            ImageGenerationError: If image generation fails
        """
        try:
            # Generate image prompt
            image_prompt_data = self._generate_image_prompt(
                page_data, characters, art_style
            )
            
            # Save image prompt data
            page_number = page_data.get("page_number", 0)
            prompt_filename = f"page_{page_number:02d}_prompt.json"
            self._save_image_prompt(image_prompt_data, book_title, prompt_filename)
            
            if not self.image_client:
                raise ImageGenerationError(
                    "Image client not configured",
                    page_number=page_number
                )
            
            # Create output directory
            book_images_dir = self._get_book_images_dir(book_title)
            
            # Generate image using image client
            reference_image = self.reference_image_path if use_reference else None
            
            image_path = self.image_client.generate_book_page_image(
                image_prompt_data=image_prompt_data,
                page_number=page_number,
                output_dir=book_images_dir,
                reference_image_path=reference_image,
                characters_data=[char.dict() for char in characters]
            )
            
            # Set reference image for future pages
            if self.reference_image_path is None and Path(image_path).exists():
                self.reference_image_path = Path(image_path)
            
            return image_path
            
        except Exception as e:
            raise ImageGenerationError(
                f"Image generation failed: {str(e)}",
                page_number=page_data.get("page_number")
            )
    
    def _generate_image_prompt(
        self,
        page_data: dict,
        characters: List[Character],
        art_style: str
    ) -> dict:
        """Generate detailed image prompt for a page."""
        page_description = page_data.get("scene_description", "")
        characters_present = page_data.get("characters_present", [])
        mood_tone = page_data.get("mood_tone", "happy and engaging")
        visual_elements = page_data.get("visual_elements", [])
        
        # Get character descriptions for characters present
        relevant_characters = {}
        for char in characters:
            if char.character_name in characters_present:
                relevant_characters[char.character_name] = char.dict()
        
        # Generate image prompt using AI
        image_prompt_data = self.ai_client.generate_image_prompt(
            page_description=page_description,
            characters_present=characters_present,
            character_descriptions=relevant_characters,
            mood_tone=mood_tone,
            visual_elements=visual_elements,
            art_style=art_style,
            prompt_template=self.image_generation_prompt
        )
        
        # Add page metadata
        image_prompt_data["page_metadata"] = {
            "page_number": page_data.get("page_number", 0),
            "page_type": page_data.get("page_type", "story"),
            "characters_present": characters_present
        }
        
        return image_prompt_data
    
    def generate_all_page_images(
        self,
        book_plan: BookPlan,
        characters: List[Character],
        art_style: str = "children's book illustration",
        include_cover: bool = True,
        uploaded_cover_path: Optional[str] = None
    ) -> Dict[int, str]:
        """
        Generate images for all pages in the book.
        
        Args:
            book_plan: Complete book plan
            characters: List of character models
            art_style: Desired art style
            include_cover: Whether to generate a cover image
            uploaded_cover_path: Path to uploaded cover image
            
        Returns:
            Dictionary mapping page numbers to image file paths
        """
        generated_images = {}
        
        # Handle cover
        if uploaded_cover_path:
            generated_images[0] = uploaded_cover_path
        elif include_cover and self.image_client:
            try:
                cover_path = self._generate_book_cover(book_plan, characters, art_style)
                generated_images[0] = cover_path
            except Exception as e:
                print(f"Error generating cover: {str(e)}")
        
        # Generate images for each page
        for page in book_plan.pages:
            page_number = page.page_number
            page_type = page.page_type
            
            # Skip cover page if already handled
            if page_type.value == "cover" and (include_cover or uploaded_cover_path):
                continue
            
            try:
                use_reference = page_number > 1
                
                image_path = self.generate_page_image(
                    page_data=page.dict(),
                    characters=characters,
                    book_title=book_plan.book_title,
                    art_style=art_style,
                    use_reference=use_reference
                )
                
                generated_images[page_number] = image_path
                
            except Exception as e:
                print(f"Error generating image for page {page_number}: {str(e)}")
                continue
        
        return generated_images
    
    def _generate_book_cover(
        self,
        book_plan: BookPlan,
        characters: List[Character],
        art_style: str
    ) -> str:
        """Generate a cover image for the book."""
        if not self.image_client:
            raise ImageGenerationError("Image client not configured for cover generation")
        
        book_title = book_plan.book_title
        themes = book_plan.themes or []
        theme_str = ", ".join(themes) if themes else "adventure and friendship"
        
        book_images_dir = self._get_book_images_dir(book_title)
        
        cover_path = self.image_client.generate_book_cover(
            title=book_title,
            characters=[char.dict() for char in characters],
            theme=theme_str,
            output_dir=book_images_dir,
            reference_image_path=self.reference_image_path
        )
        
        return cover_path
    
    def generate_page_text(
        self,
        page_data: dict,
        book_plan: BookPlan,
        story_context: Optional[dict] = None,
        previous_page_text: str = "",
        language: str = "English"
    ) -> TextData:
        """
        Generate text content for a specific book page.
        
        Args:
            page_data: Page information from book plan
            book_plan: Complete book plan
            story_context: Current story context for consistency
            previous_page_text: Text from previous page
            language: Language for text content
            
        Returns:
            TextData model with generated content
            
        Raises:
            TextGenerationError: If text generation fails
        """
        try:
            page_description = page_data.get("scene_description", "")
            characters_present = page_data.get("characters_present", [])
            age_group = book_plan.target_age
            book_theme = ", ".join(book_plan.themes) if book_plan.themes else "adventure, friendship"
            
            # Get story arc information
            story_arc = ""
            if book_plan.story_arc:
                story_arc = str(book_plan.story_arc.dict())
            
            # Generate page text using AI
            text_data = self.ai_client.generate_page_text(
                page_description=page_description,
                characters_present=characters_present,
                age_group=age_group,
                language=language,
                book_theme=book_theme,
                previous_context=previous_page_text,
                story_arc=story_arc,
                prompt_template=self.text_generation_prompt
            )
            
            # Add page metadata
            text_data["page_metadata"] = {
                "page_number": page_data.get("page_number", 0),
                "page_type": page_data.get("page_type", "story"),
                "characters_present": characters_present
            }
            
            return TextData(**text_data)
            
        except Exception as e:
            raise TextGenerationError(
                f"Text generation failed: {str(e)}",
                page_number=page_data.get("page_number"),
                language=language
            )
    
    def generate_all_page_texts(
        self,
        book_plan: BookPlan,
        language: str = "English"
    ) -> Dict[int, TextData]:
        """
        Generate text for all pages in the book.
        
        Args:
            book_plan: Complete book plan
            language: Language for text content
            
        Returns:
            Dictionary mapping page numbers to TextData models
        """
        generated_texts = {}
        story_context = StoryContext()
        previous_pages_text = []
        
        for page in book_plan.pages:
            page_number = page.page_number
            page_type = page.page_type
            
            # Skip cover page
            if page_type.value == "cover":
                continue
            
            try:
                # Create context from previous pages
                if len(previous_pages_text) >= 2:
                    previous_context = f"Previous page: {previous_pages_text[-1]}\n\nTwo pages ago: {previous_pages_text[-2]}"
                elif len(previous_pages_text) == 1:
                    previous_context = f"Previous page: {previous_pages_text[-1]}"
                else:
                    story_summary = book_plan.book_summary
                    previous_context = f"FIRST PAGE OF STORY: This is the opening page. Introduce the main characters and setting. Story summary: {story_summary}"
                
                text_data = self.generate_page_text(
                    page_data=page.dict(),
                    book_plan=book_plan,
                    story_context=story_context.__dict__,
                    previous_page_text=previous_context,
                    language=language
                )
                
                # Save text data
                self._save_page_text(text_data, book_plan.book_title, page_number)
                
                # Update context
                current_page_text = text_data.page_text
                previous_pages_text.append(current_page_text)
                if len(previous_pages_text) > 2:
                    previous_pages_text.pop(0)
                
                story_context.update_from_page(page.dict(), text_data.dict(), book_plan)
                
                generated_texts[page_number] = text_data
                
            except Exception as e:
                print(f"Error generating text for page {page_number}: {str(e)}")
                continue
        
        return generated_texts
    
    def _save_image_prompt(self, image_prompt_data: dict, book_title: str, filename: str) -> Path:
        """Save image prompt data to file."""
        book_prompts_dir = self._get_book_images_dir(book_title) / "prompts"
        book_prompts_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = book_prompts_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            import json
            json.dump(image_prompt_data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def _save_page_text(self, text_data: TextData, book_title: str, page_number: int) -> Path:
        """Save page text data to file."""
        book_texts_dir = self._get_book_texts_dir(book_title)
        
        filename = f"page_{page_number:02d}_text.json"
        output_path = book_texts_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            import json
            json.dump(text_data.dict(), f, indent=2, ensure_ascii=False)
        
        # Also save plain text version
        plain_text_path = book_texts_dir / f"page_{page_number:02d}_text.txt"
        with open(plain_text_path, 'w', encoding='utf-8') as f:
            f.write(text_data.page_text)
        
        return output_path
    
    def _get_book_images_dir(self, book_title: str) -> Path:
        """Get images directory for a specific book."""
        clean_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_title = clean_title.replace(' ', '_').lower()
        
        book_images_dir = IMAGES_DIR / clean_title
        book_images_dir.mkdir(parents=True, exist_ok=True)
        
        return book_images_dir
    
    def _get_book_texts_dir(self, book_title: str) -> Path:
        """Get texts directory for a specific book."""
        clean_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_title = clean_title.replace(' ', '_').lower()
        
        book_texts_dir = TEXTS_DIR / clean_title
        book_texts_dir.mkdir(parents=True, exist_ok=True)
        
        return book_texts_dir