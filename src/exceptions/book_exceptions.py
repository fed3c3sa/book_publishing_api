"""
Book planning and structure exception classes.
"""

from typing import Optional, Any, Dict
from .base_exceptions import ProcessingError, ValidationError, ResourceNotFoundError


class BookPlanningError(ProcessingError):
    """Raised when book planning fails."""
    
    def __init__(
        self,
        message: str,
        book_title: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "book_planning", details)
        self.book_title = book_title


class BookValidationError(ValidationError):
    """Raised when book plan validation fails."""
    
    def __init__(
        self,
        message: str,
        book_title: Optional[str] = None,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, field, value, details)
        self.book_title = book_title


class BookNotFoundError(ResourceNotFoundError):
    """Raised when a book plan is not found."""
    
    def __init__(
        self,
        message: str,
        book_title: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "book_plan", book_title, details)