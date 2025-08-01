"""
Content generation exception classes.
"""

from typing import Optional, Any, Dict
from .base_exceptions import ProcessingError


class ContentGenerationError(ProcessingError):
    """Base class for content generation errors."""
    
    def __init__(
        self,
        message: str,
        content_type: Optional[str] = None,
        page_number: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, f"{content_type}_generation", details)
        self.content_type = content_type
        self.page_number = page_number


class ImageGenerationError(ContentGenerationError):
    """Raised when image generation fails."""
    
    def __init__(
        self,
        message: str,
        page_number: Optional[int] = None,
        image_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "image", page_number, details)
        self.image_type = image_type


class TextGenerationError(ContentGenerationError):
    """Raised when text generation fails."""
    
    def __init__(
        self,
        message: str,
        page_number: Optional[int] = None,
        language: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "text", page_number, details)
        self.language = language


class PDFGenerationError(ContentGenerationError):
    """Raised when PDF generation fails."""
    
    def __init__(
        self,
        message: str,
        book_title: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "pdf", None, details)
        self.book_title = book_title