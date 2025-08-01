"""
Prompt management system for the Children's Book Generator.

This module provides organized access to all prompts used throughout
the book generation process, with easy maintenance and versioning.
"""

from .prompt_manager import PromptManager
from .prompt_registry import PromptRegistry

__all__ = [
    "PromptManager",
    "PromptRegistry",
]