"""
Children's Book Generator - Source Package

This package contains all the core modules for generating AI-powered children's books.
"""

# Make imports available at package level
from .ai_clients import OpenAIClient, IdeogramClient
from .character_processing import CharacterProcessor
from .book_planning import BookPlanner
from .content_generation import ImageGenerator, TextGenerator
from .pdf_generation import PDFGenerator

__all__ = [
    "OpenAIClient",
    "IdeogramClient", 
    "CharacterProcessor",
    "BookPlanner",
    "ImageGenerator",
    "TextGenerator",
    "PDFGenerator"
]

__version__ = "1.0.0"

