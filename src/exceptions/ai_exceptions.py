"""
AI client exception classes.
"""

from typing import Optional, Any, Dict
from .base_exceptions import ProcessingError


class AIClientError(ProcessingError):
    """Base class for AI client errors."""
    
    def __init__(
        self,
        message: str,
        client_name: Optional[str] = None,
        model_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "ai_client", details)
        self.client_name = client_name
        self.model_name = model_name


class AIResponseError(AIClientError):
    """Raised when AI response is invalid or unexpected."""
    
    def __init__(
        self,
        message: str,
        client_name: Optional[str] = None,
        response_text: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, client_name, None, details)
        self.response_text = response_text


class AIAuthenticationError(AIClientError):
    """Raised when AI client authentication fails."""
    
    def __init__(
        self,
        message: str,
        client_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, client_name, None, details)
        self.error_code = "AI_AUTHENTICATION_ERROR"


class AIRateLimitError(AIClientError):
    """Raised when AI client rate limit is exceeded."""
    
    def __init__(
        self,
        message: str,
        client_name: Optional[str] = None,
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, client_name, None, details)
        self.retry_after = retry_after
        self.error_code = "AI_RATE_LIMIT_ERROR"