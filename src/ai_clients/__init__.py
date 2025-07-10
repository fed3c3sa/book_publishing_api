"""
AI Clients package for the Children's Book Generator.

This package contains clients for interacting with various AI services
including Google Gemini 2.5 Flash and Ideogram for text and image generation.
"""

from .gemini_client import GeminiClient
from .ideogram_client import IdeogramClient

__all__ = ["GeminiClient", "IdeogramClient"]

