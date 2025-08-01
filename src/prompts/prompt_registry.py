"""
Registry of all prompts with their metadata and validation rules.
"""

from typing import Dict, List, NamedTuple
from .prompt_manager import PromptCategory


class PromptInfo(NamedTuple):
    """Information about a prompt template."""
    name: str
    category: PromptCategory
    description: str
    required_placeholders: List[str]
    optional_placeholders: List[str] = []


class PromptRegistry:
    """Registry of all prompt templates with metadata."""
    
    # Define all prompts with their requirements
    PROMPTS: Dict[str, PromptInfo] = {

        
        "book_planning": PromptInfo(
            name="book_planning", 
            category=PromptCategory.BOOK_PLANNING,
            description="Create structured book plans with page-by-page breakdown",
            required_placeholders=[
                "story_idea", "num_pages", "age_group", "language", "characters"
            ],
            optional_placeholders=[]
        ),
        
        "text_generation": PromptInfo(
            name="text_generation",
            category=PromptCategory.TEXT_GENERATION,
            description="Generate age-appropriate text content for book pages",
            required_placeholders=[
                "page_description", "characters_present", "age_group", 
                "language", "book_theme", "previous_context", "story_arc"
            ],
            optional_placeholders=[]
        ),
        
        "image_generation": PromptInfo(
            name="image_generation",
            category=PromptCategory.IMAGE_GENERATION,
            description="Create detailed prompts for AI image generation",
            required_placeholders=[
                "page_description", "characters_present", "character_descriptions",
                "mood_tone", "visual_elements", "art_style"
            ],
            optional_placeholders=[]
        ),
    }
    
    @classmethod
    def get_prompt_info(cls, prompt_name: str) -> PromptInfo:
        """
        Get information about a prompt.
        
        Args:
            prompt_name: Name of the prompt
            
        Returns:
            PromptInfo object
            
        Raises:
            KeyError: If prompt is not registered
        """
        if prompt_name not in cls.PROMPTS:
            raise KeyError(f"Prompt '{prompt_name}' is not registered")
        
        return cls.PROMPTS[prompt_name]
    
    @classmethod
    def get_prompts_by_category(cls, category: PromptCategory) -> List[PromptInfo]:
        """
        Get all prompts in a category.
        
        Args:
            category: Prompt category
            
        Returns:
            List of PromptInfo objects
        """
        return [info for info in cls.PROMPTS.values() if info.category == category]
    
    @classmethod
    def validate_prompt_placeholders(cls, prompt_name: str, prompt_content: str) -> bool:
        """
        Validate that a prompt contains all required placeholders.
        
        Args:
            prompt_name: Name of the prompt
            prompt_content: Prompt template content
            
        Returns:
            True if valid
        """
        info = cls.get_prompt_info(prompt_name)
        
        for placeholder in info.required_placeholders:
            if f"{{{placeholder}}}" not in prompt_content:
                return False
        
        return True
    
    @classmethod
    def get_all_prompt_names(cls) -> List[str]:
        """Get all registered prompt names."""
        return list(cls.PROMPTS.keys())