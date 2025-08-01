"""
Workflow context for maintaining state during book generation.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel

from ..domain.models import (
    GenerationRequest,
    WorkflowStep,
    WorkflowStatus,
    Character,
    BookPlan,
    TextData,
)


class WorkflowContext(BaseModel):
    """Context object that maintains state throughout the workflow."""
    
    # Request data
    generation_id: str
    request: GenerationRequest
    
    # Workflow status
    status: WorkflowStatus
    
    # Generated data
    characters: List[Character] = []
    book_plan: Optional[BookPlan] = None
    page_images: Dict[int, str] = {}
    page_texts: Dict[int, TextData] = {}
    pdf_path: Optional[str] = None
    
    # Intermediate data
    processed_character_inputs: List[Dict[str, Any]] = []
    story_context: Optional[Dict[str, Any]] = None
    generation_metadata: Dict[str, Any] = {}
    
    # Error handling
    errors: List[str] = []
    warnings: List[str] = []
    
    class Config:
        arbitrary_types_allowed = True
    
    def update_status(
        self,
        step: WorkflowStep,
        progress: int,
        message: str,
        error_message: Optional[str] = None
    ) -> None:
        """Update workflow status."""
        self.status.current_step = step
        self.status.progress = progress
        self.status.message = message
        self.status.updated_time = datetime.now()
        
        if error_message:
            self.status.error_message = error_message
            self.errors.append(error_message)
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
    
    def get_progress_percentage(self) -> int:
        """Get current progress percentage."""
        return self.status.progress
    
    def is_completed(self) -> bool:
        """Check if workflow is completed."""
        return self.status.current_step == WorkflowStep.COMPLETE
    
    def has_errors(self) -> bool:
        """Check if workflow has errors."""
        return len(self.errors) > 0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get workflow summary."""
        return {
            "generation_id": self.generation_id,
            "status": self.status.current_step.value,
            "progress": self.status.progress,
            "message": self.status.message,
            "characters_count": len(self.characters),
            "pages_count": len(self.book_plan.pages) if self.book_plan else 0,
            "images_generated": len(self.page_images),
            "texts_generated": len(self.page_texts),
            "errors_count": len(self.errors),
            "warnings_count": len(self.warnings),
            "start_time": self.status.start_time.isoformat(),
            "updated_time": self.status.updated_time.isoformat(),
        }