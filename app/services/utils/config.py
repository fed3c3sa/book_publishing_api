"""
Configuration management module for the Children's Book Generator.

This module handles loading environment variables, API keys, and other configuration settings.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()

# Output directories
OUTPUT_DIR = PROJECT_ROOT / "output"
CHARACTERS_DIR = OUTPUT_DIR / "characters"
PLANS_DIR = OUTPUT_DIR / "plans"
IMAGES_DIR = OUTPUT_DIR / "images"
TEXTS_DIR = OUTPUT_DIR / "texts"
BOOKS_DIR = OUTPUT_DIR / "books"

# Prompts directory
PROMPTS_DIR = PROJECT_ROOT / "prompts"

# Ensure all directories exist
for directory in [CHARACTERS_DIR, PLANS_DIR, IMAGES_DIR, TEXTS_DIR, BOOKS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def load_config(env_file: str = "secrets.env") -> Dict[str, str]:
    """
    Load configuration from environment variables and .env file.
    
    Args:
        env_file: Path to the environment file, relative to project root
        
    Returns:
        Dictionary containing configuration values
    """
    # Load environment variables from file
    env_path = PROJECT_ROOT / env_file
    if env_path.exists():
        load_dotenv(env_path)
    
    # Required API keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    ideogram_api_key = os.getenv("IDEOGRAM_API_KEY")
    
    # Optional configuration
    openai_org_id = os.getenv("OPENAI_ORG_ID", "")
    
    # Validate required keys
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables or .env file")
    if not ideogram_api_key:
        raise ValueError("IDEOGRAM_API_KEY not found in environment variables or .env file")
    
    return {
        "openai_api_key": openai_api_key,
        "ideogram_api_key": ideogram_api_key,
        "openai_org_id": openai_org_id,
    }


def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt template from the prompts directory.
    
    Args:
        prompt_name: Name of the prompt file (without extension)
        
    Returns:
        String containing the prompt template
    """
    prompt_path = PROMPTS_DIR / f"{prompt_name}.txt"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def get_output_path(directory: Path, filename: str) -> Path:
    """
    Get a path for an output file in the specified directory.
    
    Args:
        directory: Directory to save the file in
        filename: Name of the file
        
    Returns:
        Path object for the output file
    """
    # Ensure directory exists
    directory.mkdir(parents=True, exist_ok=True)
    
    # Return full path
    return directory / filename

