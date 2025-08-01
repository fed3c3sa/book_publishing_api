"""
Children's Book Generator - Source Package

This package contains all the core modules for generating AI-powered children's books.
"""

# Make imports available at package level
from .services import (
    CharacterService,
    BookPlanningService,
    ContentGenerationService,
    PDFGenerationService
)

__all__ = [
    "CharacterService",
    "BookPlanningService",
    "ContentGenerationService", 
    "PDFGenerationService"
]

__version__ = "2.0.0"

