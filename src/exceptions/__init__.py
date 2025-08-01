"""
Custom exception classes for the Children's Book Generator.

This module provides structured error handling with specific exception
types for different failure scenarios in the book generation process.
"""

from .base_exceptions import (
    BookGeneratorError,
    ValidationError,
    ProcessingError,
    ResourceNotFoundError,
    ConfigurationError,
)

from .character_exceptions import (
    CharacterProcessingError,
    CharacterValidationError,
    CharacterNotFoundError,
)

from .book_exceptions import (
    BookPlanningError,
    BookValidationError,
    BookNotFoundError,
)

from .content_exceptions import (
    ContentGenerationError,
    ImageGenerationError,
    TextGenerationError,
    PDFGenerationError,
)

from .ai_exceptions import (
    AIClientError,
    AIResponseError,
    AIAuthenticationError,
    AIRateLimitError,
)

__all__ = [
    # Base exceptions
    "BookGeneratorError",
    "ValidationError", 
    "ProcessingError",
    "ResourceNotFoundError",
    "ConfigurationError",
    
    # Character exceptions
    "CharacterProcessingError",
    "CharacterValidationError",
    "CharacterNotFoundError",
    
    # Book exceptions
    "BookPlanningError",
    "BookValidationError",
    "BookNotFoundError",
    
    # Content exceptions
    "ContentGenerationError",
    "ImageGenerationError",
    "TextGenerationError", 
    "PDFGenerationError",
    
    # AI exceptions
    "AIClientError",
    "AIResponseError",
    "AIAuthenticationError",
    "AIRateLimitError",
]