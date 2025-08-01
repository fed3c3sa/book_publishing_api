"""
Workflow manager for handling multiple concurrent workflows.
"""

from typing import Dict, Optional, Callable
import threading
from datetime import datetime

from ..domain.models import GenerationRequest
from ..exceptions import ResourceNotFoundError
from .workflow_context import WorkflowContext
from .book_generation_workflow import BookGenerationWorkflow


class WorkflowManager:
    """
    Manages multiple concurrent book generation workflows.
    
    This class provides thread-safe management of ongoing book generations,
    allowing multiple books to be generated simultaneously.
    """
    
    def __init__(self, workflow_factory: Callable[[], BookGenerationWorkflow]):
        """
        Initialize the workflow manager.
        
        Args:
            workflow_factory: Factory function that creates BookGenerationWorkflow instances
        """
        self.workflow_factory = workflow_factory
        self.ongoing_workflows: Dict[str, WorkflowContext] = {}
        self._lock = threading.Lock()
    
    def start_generation(
        self,
        request: GenerationRequest,
        progress_callback: Optional[Callable[[WorkflowContext], None]] = None
    ) -> str:
        """
        Start a new book generation workflow.
        
        Args:
            request: Book generation request
            progress_callback: Optional callback for progress updates
            
        Returns:
            Generation ID for tracking the workflow
        """
        # Create workflow with progress callback that updates our storage
        def combined_callback(context: WorkflowContext) -> None:
            with self._lock:
                self.ongoing_workflows[context.generation_id] = context
            
            if progress_callback:
                progress_callback(context)
        
        workflow = self.workflow_factory()
        workflow.progress_callback = combined_callback
        
        # Start workflow in background thread
        def run_workflow():
            context = workflow.execute(request)
            with self._lock:
                self.ongoing_workflows[context.generation_id] = context
        
        thread = threading.Thread(target=run_workflow, daemon=True)
        thread.start()
        
        # Create initial status for temporary context
        from ..domain.models import WorkflowStep, WorkflowStatus
        initial_status = WorkflowStatus(
            current_step=WorkflowStep.INITIALIZE,
            progress=0,
            message="Initializing...",
            start_time=datetime.now(),
            updated_time=datetime.now()
        )
        
        # Return a temporary context with just the generation ID
        # The actual context will be populated when the workflow starts
        temp_context = WorkflowContext(
            generation_id="temp",  # Will be replaced when workflow starts
            request=request,
            status=initial_status
        )
        
        # We need to wait briefly for the workflow to initialize and get the real ID
        # For now, we'll generate an ID here to ensure immediate response
        import uuid
        generation_id = str(uuid.uuid4())
        
        # Store placeholder context
        with self._lock:
            from ..domain.models import WorkflowStep, WorkflowStatus
            placeholder_status = WorkflowStatus(
                current_step=WorkflowStep.INITIALIZE,
                progress=0,
                message="Starting book generation...",
                start_time=datetime.now(),
                updated_time=datetime.now()
            )
            placeholder_context = WorkflowContext(
                generation_id=generation_id,
                request=request,
                status=placeholder_status
            )
            self.ongoing_workflows[generation_id] = placeholder_context
        
        return generation_id
    
    def get_workflow_status(self, generation_id: str) -> WorkflowContext:
        """
        Get the status of a workflow.
        
        Args:
            generation_id: ID of the generation to check
            
        Returns:
            WorkflowContext with current status
            
        Raises:
            ResourceNotFoundError: If generation ID is not found
        """
        with self._lock:
            if generation_id not in self.ongoing_workflows:
                raise ResourceNotFoundError(
                    f"Generation ID not found: {generation_id}",
                    resource_type="workflow",
                    resource_id=generation_id
                )
            
            return self.ongoing_workflows[generation_id]
    
    def get_all_workflows(self) -> Dict[str, WorkflowContext]:
        """Get all current workflows."""
        with self._lock:
            return self.ongoing_workflows.copy()
    
    def cleanup_completed_workflows(self, max_age_hours: int = 24) -> int:
        """
        Clean up completed workflows older than specified age.
        
        Args:
            max_age_hours: Maximum age in hours for completed workflows
            
        Returns:
            Number of workflows cleaned up
        """
        with self._lock:
            current_time = datetime.now()
            to_remove = []
            
            for generation_id, context in self.ongoing_workflows.items():
                if context.is_completed():
                    age_hours = (current_time - context.status.start_time).total_seconds() / 3600
                    if age_hours > max_age_hours:
                        to_remove.append(generation_id)
            
            for generation_id in to_remove:
                del self.ongoing_workflows[generation_id]
            
            return len(to_remove)
    
    def get_workflow_summary(self, generation_id: str) -> Dict:
        """
        Get a summary of workflow status.
        
        Args:
            generation_id: ID of the generation
            
        Returns:
            Dictionary with workflow summary
        """
        context = self.get_workflow_status(generation_id)
        return context.get_summary()