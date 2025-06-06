"""
Utilities package for the Children's Book Generator.

This package contains utility modules for configuration management,
file handling, and other common functionality.
"""

from .config import (
    load_config,
    load_prompt,
    get_output_path,
    PROJECT_ROOT,
    OUTPUT_DIR,
    CHARACTERS_DIR,
    PLANS_DIR,
    IMAGES_DIR,
    TEXTS_DIR,
    BOOKS_DIR,
    PROMPTS_DIR
)

__all__ = [
    "load_config",
    "load_prompt", 
    "get_output_path",
    "PROJECT_ROOT",
    "OUTPUT_DIR",
    "CHARACTERS_DIR",
    "PLANS_DIR",
    "IMAGES_DIR",
    "TEXTS_DIR",
    "BOOKS_DIR",
    "PROMPTS_DIR"
]

