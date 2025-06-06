"""
AI Clients package for the Children's Book Generator.

This package contains clients for interacting with various AI services
including OpenAI GPT-4o and Ideogram for text and image generation.
"""

from .openai_client import OpenAIClient
from .ideogram_client import IdeogramClient

__all__ = ["OpenAIClient", "IdeogramClient"]

