"""
Character-specific exception classes.
"""

from typing import Optional, Any, Dict
from .base_exceptions import ProcessingError, ValidationError, ResourceNotFoundError


class CharacterProcessingError(ProcessingError):
    """Raised when character processing fails."""
    
    def __init__(
        self,
        message: str,
        character_name: Optional[str] = None,
        input_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "character_processing", details)
        self.character_name = character_name
        self.input_type = input_type


class CharacterValidationError(ValidationError):
    """Raised when character data validation fails."""
    
    def __init__(
        self,
        message: str,
        character_name: Optional[str] = None,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, field, value, details)
        self.character_name = character_name


class CharacterNotFoundError(ResourceNotFoundError):
    """Raised when a character is not found."""
    
    def __init__(
        self,
        message: str,
        character_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "character", character_name, details)