"""
Main book generation workflow implementation.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable

from ..domain.models import (
    GenerationRequest,
    WorkflowStep,
    WorkflowStatus,
    Character,
    BookPlan,
    TextData,
)
from ..interfaces import (
    CharacterServiceInterface,
    BookPlanningInterface,
    ContentGenerationInterface,
    PDFGenerationInterface,
)
from ..exceptions import (
    BookGeneratorError,
    CharacterProcessingError,
    BookPlanningError,
    ContentGenerationError,
    PDFGenerationError,
)
from .workflow_context import WorkflowContext


class BookGenerationWorkflow:
    """
    Main workflow orchestrator for book generation.
    
    This class manages the entire book generation process from character
    processing through PDF creation, with proper error handling and progress tracking.
    """
    
    def __init__(
        self,
        character_service: CharacterServiceInterface,
        book_planning_service: BookPlanningInterface,
        content_generation_service: ContentGenerationInterface,
        pdf_generation_service: PDFGenerationInterface,
        progress_callback: Optional[Callable[[WorkflowContext], None]] = None
    ):
        """
        Initialize the workflow with required services.
        
        Args:
            character_service: Character processing service
            book_planning_service: Book planning service
            content_generation_service: Content generation service
            pdf_generation_service: PDF generation service
            progress_callback: Optional callback for progress updates
        """
        self.character_service = character_service
        self.book_planning_service = book_planning_service
        self.content_generation_service = content_generation_service
        self.pdf_generation_service = pdf_generation_service
        self.progress_callback = progress_callback
    
    def execute(self, request: GenerationRequest) -> WorkflowContext:
        """
        Execute the complete book generation workflow.
        
        Args:
            request: Book generation request
            
        Returns:
            WorkflowContext with results and status
        """
        # Initialize workflow context
        context = self._initialize_context(request)
        
        try:
            # Execute workflow steps
            self._step_process_characters(context)
            self._step_create_book_plan(context)
            self._step_generate_images(context)
            self._step_generate_texts(context)
            self._step_create_pdf(context)
            self._step_complete(context)
            
        except BookGeneratorError as e:
            self._handle_error(context, e)
        except Exception as e:
            self._handle_unexpected_error(context, e)
        
        return context
    
    def _initialize_context(self, request: GenerationRequest) -> WorkflowContext:
        """Initialize workflow context."""
        generation_id = str(uuid.uuid4())
        
        status = WorkflowStatus(
            current_step=WorkflowStep.INITIALIZE,
            progress=0,
            message="Initializing book generation...",
            start_time=datetime.now(),
            updated_time=datetime.now()
        )
        
        context = WorkflowContext(
            generation_id=generation_id,
            request=request,
            status=status
        )
        
        self._update_progress(context)
        return context
    
    def _step_process_characters(self, context: WorkflowContext) -> None:
        """Process character inputs."""
        context.update_status(
            WorkflowStep.PROCESS_CHARACTERS,
            15,
            f"Processing {len(context.request.characters)} characters..."
        )
        self._update_progress(context)
        
        try:
            characters = self.character_service.process_multiple_characters(
                context.request.characters
            )
            
            if not characters:
                raise CharacterProcessingError("No characters were successfully processed")
            
            context.characters = characters
            context.update_status(
                WorkflowStep.PROCESS_CHARACTERS,
                25,
                f"Successfully processed {len(characters)} characters"
            )
            
        except Exception as e:
            raise CharacterProcessingError(
                f"Character processing failed: {str(e)}",
                details={"characters_count": len(context.request.characters)}
            )
        
        self._update_progress(context)
    
    def _step_create_book_plan(self, context: WorkflowContext) -> None:
        """Create book plan."""
        context.update_status(
            WorkflowStep.CREATE_PLAN,
            40,
            "Creating book plan and story structure..."
        )
        self._update_progress(context)
        
        try:
            book_plan = self.book_planning_service.create_book_plan(
                story_idea=context.request.story_idea,
                characters=context.characters,
                num_pages=context.request.num_pages,
                age_group=context.request.age_group,
                language=context.request.language,
                book_title=context.request.book_title,
                themes=context.request.themes
            )
            
            context.book_plan = book_plan
            context.update_status(
                WorkflowStep.CREATE_PLAN,
                50,
                f"Book plan created with {len(book_plan.pages)} pages"
            )
            
        except Exception as e:
            raise BookPlanningError(
                f"Book planning failed: {str(e)}",
                book_title=context.request.book_title
            )
        
        self._update_progress(context)
    
    def _step_generate_images(self, context: WorkflowContext) -> None:
        """Generate page images."""
        if context.request.cover_image_path:
            message = "Generating illustrations (using your uploaded cover)..."
        else:
            message = "Generating illustrations..."
        
        context.update_status(
            WorkflowStep.GENERATE_IMAGES,
            60,
            message
        )
        self._update_progress(context)
        
        try:
            page_images = self.content_generation_service.generate_all_page_images(
                book_plan=context.book_plan,
                characters=context.characters,
                art_style=context.request.art_style,
                include_cover=not bool(context.request.cover_image_path),
                uploaded_cover_path=context.request.cover_image_path
            )
            
            context.page_images = page_images
            context.update_status(
                WorkflowStep.GENERATE_IMAGES,
                75,
                f"Generated {len(page_images)} images"
            )
            
        except Exception as e:
            raise ContentGenerationError(
                f"Image generation failed: {str(e)}",
                content_type="image"
            )
        
        self._update_progress(context)
    
    def _step_generate_texts(self, context: WorkflowContext) -> None:
        """Generate page texts."""
        context.update_status(
            WorkflowStep.GENERATE_TEXT,
            80,
            "Generating text content..."
        )
        self._update_progress(context)
        
        try:
            page_texts = self.content_generation_service.generate_all_page_texts(
                book_plan=context.book_plan,
                language=context.request.language
            )
            
            context.page_texts = page_texts
            context.update_status(
                WorkflowStep.GENERATE_TEXT,
                85,
                f"Generated text for {len(page_texts)} pages"
            )
            
        except Exception as e:
            raise ContentGenerationError(
                f"Text generation failed: {str(e)}",
                content_type="text"
            )
        
        self._update_progress(context)
    
    def _step_create_pdf(self, context: WorkflowContext) -> None:
        """Create final PDF."""
        context.update_status(
            WorkflowStep.CREATE_PDF,
            90,
            "Assembling final PDF..."
        )
        self._update_progress(context)
        
        try:
            # Convert TextData models to dict format for compatibility
            page_texts_dict = {
                page_num: text_data.dict() if hasattr(text_data, 'dict') else text_data
                for page_num, text_data in context.page_texts.items()
            }
            
            pdf_path = self.pdf_generation_service.create_book_pdf(
                book_plan=context.book_plan,
                page_images=context.page_images,
                page_texts=page_texts_dict
            )
            
            context.pdf_path = pdf_path
            context.update_status(
                WorkflowStep.CREATE_PDF,
                95,
                "PDF created successfully"
            )
            
        except Exception as e:
            raise PDFGenerationError(
                f"PDF generation failed: {str(e)}",
                book_title=context.book_plan.book_title if context.book_plan else None
            )
        
        self._update_progress(context)
    
    def _step_complete(self, context: WorkflowContext) -> None:
        """Complete the workflow."""
        context.update_status(
            WorkflowStep.COMPLETE,
            100,
            "Book generation completed successfully!"
        )
        self._update_progress(context)
    
    def _handle_error(self, context: WorkflowContext, error: BookGeneratorError) -> None:
        """Handle known errors."""
        error_message = f"Error in {context.status.current_step.value}: {str(error)}"
        context.update_status(
            context.status.current_step,
            -1,
            "Book generation failed",
            error_message
        )
        self._update_progress(context)
    
    def _handle_unexpected_error(self, context: WorkflowContext, error: Exception) -> None:
        """Handle unexpected errors."""
        error_message = f"Unexpected error in {context.status.current_step.value}: {str(error)}"
        context.update_status(
            context.status.current_step,
            -1,
            "Book generation failed due to unexpected error",
            error_message
        )
        self._update_progress(context)
    
    def _update_progress(self, context: WorkflowContext) -> None:
        """Update progress via callback if provided."""
        if self.progress_callback:
            self.progress_callback(context)