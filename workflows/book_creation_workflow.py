"""Book creation workflow implementation."""

import logging
import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

from smolagents import OpenAIServerModel

from agents import (
    IdeatorAgent,
    StoryWriterAgent,
    ImageCreatorAgent,
    ImpaginatorAgent,
    TrendFinderAgent,
    StyleImitatorAgent,
    TranslatorAgent,
    ImageDescriptionAgent
)
from data_models.book_plan import BookPlan
from data_models.story_content import StoryContent
from data_models.generated_image import GeneratedImage
from data_models.character import Character
from tools.ideogram_image_generation_tool import ideogram_image_generation_tool
from workflows.character_processor import CharacterProcessor

logger = logging.getLogger(__name__)


class BookCreationWorkflow:
    """Manages the complete book creation workflow."""
    
    def __init__(self, config: Dict[str, Any], project_output_dir: str):
        """Initialize the workflow with configuration and output directory."""
        self.config = config
        self.project_output_dir = Path(project_output_dir)
        self.llm_model = None
        self.agents = {}
        
        # Initialize LLM model
        self._initialize_llm_model()
        
        # Initialize core agents
        self._initialize_core_agents()
        
        # Initialize optional agents based on config
        self._initialize_optional_agents()
        
    def _initialize_llm_model(self) -> None:
        """Initialize the LLM model."""
        try:
            # Get API key from environment or config
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
                
            model_id = self.config.get("openai_llm_model", "gpt-4o")
            
            self.llm_model = OpenAIServerModel(
                api_key=api_key,
                model_id=model_id
            )
            logger.info(f"LLM model initialized: {model_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM model: {e}")
            raise
            
    def _initialize_core_agents(self) -> None:
        """Initialize the core agents required for book creation."""
        try:
            # Core agents needed for basic book creation
            self.agents['ideator'] = IdeatorAgent(model=self.llm_model)
            self.agents['story_writer'] = StoryWriterAgent(model=self.llm_model)
            
            # Extract project ID from output directory name
            project_id = self.project_output_dir.name
            output_base_dir = str(self.project_output_dir.parent)
            
            self.agents['image_creator'] = ImageCreatorAgent(
                model=self.llm_model,
                project_id=project_id,
                output_dir=output_base_dir,
                tools=[ideogram_image_generation_tool]
            )
            
            self.agents['impaginator'] = ImpaginatorAgent(
                model=self.llm_model,
                project_id=project_id,
                output_dir=output_base_dir,
                pdf_config=self.config.get("pdf_layout", {})
            )
            
            logger.info("Core agents initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize core agents: {e}")
            raise
            
    def _initialize_optional_agents(self) -> None:
        """Initialize optional agents based on configuration."""
        try:
            # Initialize optional agents only if enabled
            if self.config.get("enable_trend_finder", False):
                self.agents['trend_finder'] = TrendFinderAgent(
                    model=self.llm_model,
                    tools=[]  # Add web search tools when available
                )
                logger.info("TrendFinderAgent enabled")
                
            if self.config.get("enable_style_imitator", False):
                self.agents['style_imitator'] = StyleImitatorAgent(
                    model=self.llm_model,
                    tools=[]  # Add text analysis tools when available
                )
                logger.info("StyleImitatorAgent enabled")
                
            if self.config.get("enable_translator", False):
                self.agents['translator'] = TranslatorAgent(
                    model=self.llm_model,
                    tools=[]  # Add translation tools when available
                )
                logger.info("TranslatorAgent enabled")
                
            # Always initialize image description agent for character processing
            self.agents['image_description'] = ImageDescriptionAgent(model=self.llm_model)
            
        except Exception as e:
            logger.warning(f"Some optional agents failed to initialize: {e}")
            
    def execute(self, user_book_idea: str, characters: Optional[List[Character]] = None) -> Optional[str]:
        """
        Execute the complete book creation workflow.
        
        Args:
            user_book_idea: The user's book concept
            characters: Optional list of pre-defined characters
            
        Returns:
            Path to the generated PDF file, or None if failed
        """
        try:
            logger.info("Starting book creation workflow execution")
            
            # Step 1: Process characters
            processed_characters = self._process_characters(characters)
            
            # Step 2: Find trends (optional)
            trend_analysis = self._find_trends()
            
            # Step 3: Generate book plan
            book_plan = self._generate_book_plan(user_book_idea, trend_analysis, processed_characters)
            if not book_plan:
                logger.error("Failed to generate book plan")
                return None
                
            # Step 4: Write story content
            story_content = self._write_story_content(book_plan)
            if not story_content:
                logger.error("Failed to generate story content")
                return None
                
            # Step 5: Generate images
            generated_images = self._generate_images(story_content, book_plan)
            
            # Step 6: Create PDF
            pdf_path = self._create_pdf(story_content, generated_images)
            
            # Step 7: Optional translation
            self._handle_translation(book_plan)
            
            logger.info(f"Book creation workflow completed successfully: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return None
            
    def _process_characters(self, characters: Optional[List[Character]]) -> List[Character]:
        """Process and analyze character descriptions."""
        if not characters and not self.config.get("characters"):
            logger.info("No characters provided, skipping character processing")
            return []
            
        processor = CharacterProcessor(
            config=self.config,
            llm_model=self.llm_model,
            image_description_agent=self.agents.get('image_description')
        )
        
        # Use provided characters or process from config
        if characters:
            return processor.process_existing_characters(characters)
        else:
            return processor.process_characters_from_config()
            
    def _find_trends(self) -> Optional[str]:
        """Find trends using TrendFinderAgent if enabled."""
        trend_finder = self.agents.get('trend_finder')
        if not trend_finder:
            return None
            
        try:
            logger.info("Finding trends...")
            topic = self.config.get("trend_finder_topic", "children's books about dragons")
            genre = self.config.get("trend_finder_genre", "fantasy")
            
            trends = trend_finder.find_trends(topic=topic, genre=genre)
            logger.info("Trend analysis completed")
            return trends
            
        except Exception as e:
            logger.warning(f"Trend finding failed: {e}")
            return None
            
    def _generate_book_plan(self, user_book_idea: str, trend_analysis: Optional[str], 
                           characters: List[Character]) -> Optional[BookPlan]:
        """Generate the book plan using IdeatorAgent."""
        try:
            logger.info("Generating book plan...")
            ideator = self.agents['ideator']
            
            # Extract parameters from config
            book_plan = ideator.generate_initial_idea(
                user_prompt=user_book_idea,
                trend_analysis=trend_analysis,
                title=self.config.get("title"),
                genre=self.config.get("main_genre"),
                target_audience=self.config.get("target_audience"),
                writing_style_guide=self.config.get("writing_style_guide"),
                image_style_guide=self.config.get("image_style_guide"),
                cover_concept=self.config.get("cover_concept"),
                theme=self.config.get("theme"),
                key_elements=self.config.get("key_elements"),
                characters=characters
            )
            
            if book_plan and book_plan.chapters:
                book_plan.characters = characters
                self._save_book_plan(book_plan)
                logger.info(f"Book plan generated: {book_plan.title} with {len(book_plan.chapters)} chapters")
                return book_plan
            else:
                logger.error("Generated book plan is invalid or empty")
                return None
                
        except Exception as e:
            logger.error(f"Book plan generation failed: {e}")
            return None
            
    def _write_story_content(self, book_plan: BookPlan) -> Optional[StoryContent]:
        """Write the story content using StoryWriterAgent."""
        try:
            logger.info("Writing story content...")
            story_writer = self.agents['story_writer']
            
            # Check for style imitation
            example_style_text = None
            style_imitator = self.agents.get('style_imitator')
            if style_imitator and self.config.get("style_imitation_example_text"):
                logger.info("Analyzing writing style...")
                example_style_text = self.config["style_imitation_example_text"]
                
            story_content = story_writer.write_story(book_plan, style_example=example_style_text)
            
            if story_content and story_content.chapters_content:
                self._save_story_summary(story_content)
                logger.info(f"Story content generated for {story_content.book_plan.title}")
                return story_content
            else:
                logger.error("Generated story content is invalid or empty")
                return None
                
        except Exception as e:
            logger.error(f"Story content generation failed: {e}")
            return None
            
    def _generate_images(self, story_content: StoryContent, book_plan: BookPlan) -> List[GeneratedImage]:
        """Generate images using ImageCreatorAgent."""
        try:
            logger.info("Generating images...")
            image_creator = self.agents['image_creator']
            
            generated_images = image_creator.create_images(story_content, book_plan)
            
            self._save_image_log(generated_images)
            logger.info(f"Image generation completed: {len(generated_images)} images processed")
            return generated_images
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return []
            
    def _create_pdf(self, story_content: StoryContent, generated_images: List[GeneratedImage]) -> Optional[str]:
        """Create the final PDF using ImpaginatorAgent."""
        try:
            logger.info("Creating PDF...")
            impaginator = self.agents['impaginator']
            
            # Find cover image
            cover_image = next(
                (img for img in generated_images 
                 if img.placeholder_id == "cover" and img.image_path and not img.error_message),
                None
            )
            cover_path = cover_image.image_path if cover_image else None
            
            pdf_path = impaginator.create_book_pdf(
                story_content,
                generated_images,
                cover_image_path=cover_path
            )
            
            logger.info(f"PDF created successfully: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"PDF creation failed: {e}")
            return None
            
    def _handle_translation(self, book_plan: BookPlan) -> None:
        """Handle optional translation if enabled."""
        translator = self.agents.get('translator')
        target_language = self.config.get("translation_target_language")
        
        if not translator or not target_language:
            return
            
        try:
            logger.info(f"Translating book to {target_language}...")
            
            translated_title = translator.translate_text(book_plan.title, target_language)
            
            # Save translation summary
            translation_file = self.project_output_dir / f"translation_summary_{target_language}.txt"
            with open(translation_file, "w", encoding="utf-8") as f:
                f.write(f"Original Title: {book_plan.title}\n")
                f.write(f"Translated Title ({target_language}): {translated_title}\n\n")
                
                for i, chapter in enumerate(book_plan.chapters):
                    translated_chapter = translator.translate_text(chapter.title, target_language)
                    f.write(f"Ch {i+1} Original: {chapter.title} -> Translated: {translated_chapter}\n")
                    
            logger.info("Translation completed")
            
        except Exception as e:
            logger.warning(f"Translation failed: {e}")
            
    def _save_book_plan(self, book_plan: BookPlan) -> None:
        """Save the book plan to a YAML file."""
        try:
            plan_file = self.project_output_dir / "book_plan.yaml"
            with open(plan_file, "w", encoding="utf-8") as f:
                yaml.dump(book_plan.__dict__, f, indent=2, default_flow_style=False, allow_unicode=True)
            logger.debug("Book plan saved")
        except Exception as e:
            logger.warning(f"Failed to save book plan: {e}")
            
    def _save_story_summary(self, story_content: StoryContent) -> None:
        """Save a summary of the story content."""
        try:
            summary_file = self.project_output_dir / "story_summary.txt"
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(f"Title: {story_content.book_plan.title}\n")
                f.write(f"Characters: {len(story_content.book_plan.characters)} defined\n")
                
                for char in story_content.book_plan.characters:
                    f.write(f"  - {char.name} ({char.role}): {char.description[:100]}...\n")
                    
                f.write("\n")
                for i, chapter in enumerate(story_content.chapters_content):
                    f.write(f"\nChapter {i+1}: {chapter.title}\n")
                    f.write(f"{chapter.text_markdown[:200]}...\n")
                    f.write(f"Image Placeholders: {len(chapter.image_placeholders)}\n")
                    
            logger.debug("Story summary saved")
        except Exception as e:
            logger.warning(f"Failed to save story summary: {e}")
            
    def _save_image_log(self, generated_images: List[GeneratedImage]) -> None:
        """Save a log of generated images."""
        try:
            log_file = self.project_output_dir / "image_log.txt"
            with open(log_file, "w", encoding="utf-8") as f:
                for img in generated_images:
                    f.write(f"Placeholder ID: {img.placeholder_id}, "
                           f"Path: {img.image_path}, "
                           f"Error: {img.error_message}\n")
            logger.debug("Image log saved")
        except Exception as e:
            logger.warning(f"Failed to save image log: {e}") 