"""
Prompt management and loading system.
"""

from typing import Dict, Optional
from pathlib import Path
from enum import Enum

from ..utils.config import PROMPTS_DIR
from ..exceptions import ResourceNotFoundError, ConfigurationError


class PromptCategory(str, Enum):
    """Categories of prompts used in the system."""
    CHARACTER = "character"
    BOOK_PLANNING = "book_planning"
    TEXT_GENERATION = "text_generation"
    IMAGE_GENERATION = "image_generation"


class PromptManager:
    """
    Manages loading and caching of prompt templates.
    
    This class provides centralized access to all prompts with caching
    and validation capabilities.
    """
    
    def __init__(self, prompts_directory: Path = PROMPTS_DIR):
        """
        Initialize the prompt manager.
        
        Args:
            prompts_directory: Directory containing prompt files
        """
        self.prompts_directory = prompts_directory
        self._prompt_cache: Dict[str, str] = {}
        self._validate_prompts_directory()
    
    def _validate_prompts_directory(self) -> None:
        """Validate that the prompts directory exists and is accessible."""
        if not self.prompts_directory.exists():
            raise ConfigurationError(
                f"Prompts directory not found: {self.prompts_directory}",
                config_key="prompts_directory"
            )
        
        if not self.prompts_directory.is_dir():
            raise ConfigurationError(
                f"Prompts path is not a directory: {self.prompts_directory}",
                config_key="prompts_directory"
            )
    
    def load_prompt(self, prompt_name: str, category: Optional[PromptCategory] = None) -> str:
        """
        Load a prompt template by name.
        
        Args:
            prompt_name: Name of the prompt (without .txt extension)
            category: Optional category for organized prompts
            
        Returns:
            Prompt template as string
            
        Raises:
            ResourceNotFoundError: If prompt file is not found
        """
        # Check cache first
        cache_key = f"{category.value if category else ''}/{prompt_name}"
        if cache_key in self._prompt_cache:
            return self._prompt_cache[cache_key]
        
        # Determine file path
        if category:
            prompt_path = self.prompts_directory / category.value / f"{prompt_name}.txt"
        else:
            prompt_path = self.prompts_directory / f"{prompt_name}.txt"
        
        # Load prompt file
        if not prompt_path.exists():
            raise ResourceNotFoundError(
                f"Prompt file not found: {prompt_path}",
                resource_type="prompt",
                resource_id=prompt_name
            )
        
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_content = f.read()
            
            # Cache the prompt
            self._prompt_cache[cache_key] = prompt_content
            
            return prompt_content
            
        except Exception as e:
            raise ResourceNotFoundError(
                f"Failed to load prompt file {prompt_path}: {str(e)}",
                resource_type="prompt",
                resource_id=prompt_name
            )
    

    
    def get_book_planning_prompt(self) -> str:
        """Get the book planning prompt."""
        return self.load_prompt("book_planning", PromptCategory.BOOK_PLANNING)
    
    def get_text_generation_prompt(self) -> str:
        """Get the text generation prompt."""
        return self.load_prompt("text_generation", PromptCategory.TEXT_GENERATION)
    
    def get_image_generation_prompt(self) -> str:
        """Get the image generation prompt."""
        return self.load_prompt("image_generation", PromptCategory.IMAGE_GENERATION)
    
    def clear_cache(self) -> None:
        """Clear the prompt cache."""
        self._prompt_cache.clear()
    
    def get_available_prompts(self, category: Optional[PromptCategory] = None) -> list[str]:
        """
        Get list of available prompt names.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of available prompt names
        """
        if category:
            search_dir = self.prompts_directory / category.value
        else:
            search_dir = self.prompts_directory
        
        if not search_dir.exists():
            return []
        
        prompt_files = search_dir.glob("*.txt")
        return [f.stem for f in prompt_files]
    
    def validate_prompt_template(self, prompt_content: str, required_placeholders: list[str]) -> bool:
        """
        Validate that a prompt template contains required placeholders.
        
        Args:
            prompt_content: Prompt template content
            required_placeholders: List of required placeholder names
            
        Returns:
            True if all required placeholders are present
        """
        for placeholder in required_placeholders:
            if f"{{{placeholder}}}" not in prompt_content:
                return False
        return True