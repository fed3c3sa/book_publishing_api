"""
Interfaces and protocols for the Children's Book Generator.

This module defines abstract interfaces that provide contracts for
service implementations, enabling better testability and modularity.
"""

from .ai_client_interface import AIClientInterface
from .character_service_interface import CharacterServiceInterface
from .book_planning_interface import BookPlanningInterface
from .content_generation_interface import ContentGenerationInterface
from .pdf_generation_interface import PDFGenerationInterface

__all__ = [
    "AIClientInterface",
    "CharacterServiceInterface", 
    "BookPlanningInterface",
    "ContentGenerationInterface",
    "PDFGenerationInterface",
]