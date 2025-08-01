"""
Dependency injection container for the Children's Book Generator.

This module provides a dependency container that manages the creation
and lifecycle of all service dependencies.
"""

from typing import Optional
from functools import lru_cache

from ..interfaces import (
    AIClientInterface,
    CharacterServiceInterface,
    BookPlanningInterface,
    ContentGenerationInterface,
    PDFGenerationInterface,
)
from .ai_gemini_client import GeminiAIClient
from .character_service import CharacterService
from .book_planning_service import BookPlanningService
from .content_generation_service import ContentGenerationService
from .pdf_generation_service import PDFGenerationService
from ..prompts.prompt_manager import PromptManager
from ..workflow.workflow_manager import WorkflowManager
from ..workflow.book_generation_workflow import BookGenerationWorkflow

# Import legacy clients for compatibility
from ..ai_clients.ideogram_client import IdeogramClient


class DependencyContainer:
    """
    Dependency injection container for managing service instances.
    
    This container provides lazy initialization of services with proper
    dependency injection and singleton behavior where appropriate.
    """
    
    def __init__(self):
        """Initialize the dependency container."""
        self._instances = {}
    
    @property
    @lru_cache(maxsize=1)
    def prompt_manager(self) -> PromptManager:
        """Get the prompt manager instance."""
        return PromptManager()
    
    @property
    @lru_cache(maxsize=1)
    def ai_client(self) -> AIClientInterface:
        """Get the AI client instance."""
        return GeminiAIClient()
    
    @property
    @lru_cache(maxsize=1)
    def ideogram_client(self):
        """Get the Ideogram client instance."""
        return IdeogramClient()
    
    @property
    @lru_cache(maxsize=1)
    def character_service(self) -> CharacterServiceInterface:
        """Get the character service instance."""
        return CharacterService()
    
    @property
    @lru_cache(maxsize=1)
    def book_planning_service(self) -> BookPlanningInterface:
        """Get the book planning service instance."""
        return BookPlanningService(
            ai_client=self.ai_client,
            prompt_manager=self.prompt_manager
        )
    
    @property
    @lru_cache(maxsize=1)
    def content_generation_service(self) -> ContentGenerationInterface:
        """Get the content generation service instance."""
        return ContentGenerationService(
            ai_client=self.ai_client,
            image_client=self.ideogram_client,
            prompt_manager=self.prompt_manager
        )
    
    @property
    @lru_cache(maxsize=1)
    def pdf_generation_service(self) -> PDFGenerationInterface:
        """Get the PDF generation service instance."""
        return PDFGenerationService()
    
    @property
    @lru_cache(maxsize=1)
    def workflow_manager(self) -> WorkflowManager:
        """Get the workflow manager instance."""
        return WorkflowManager(workflow_factory=self._create_workflow)
    
    def _create_workflow(self) -> BookGenerationWorkflow:
        """Factory function for creating workflow instances."""
        return BookGenerationWorkflow(
            character_service=self.character_service,
            book_planning_service=self.book_planning_service,
            content_generation_service=self.content_generation_service,
            pdf_generation_service=self.pdf_generation_service
        )
    
    def get_workflow_with_callback(self, progress_callback) -> BookGenerationWorkflow:
        """Create a workflow instance with a specific progress callback."""
        return BookGenerationWorkflow(
            character_service=self.character_service,
            book_planning_service=self.book_planning_service,
            content_generation_service=self.content_generation_service,
            pdf_generation_service=self.pdf_generation_service,
            progress_callback=progress_callback
        )