"""
Interface for character processing services.
"""

from abc import ABC, abstractmethod
from typing import List
from pathlib import Path

from ..domain.models import Character, CharacterInput


class CharacterServiceInterface(ABC):
    """Abstract interface for character processing services."""
    
    @abstractmethod
    def process_character_input(self, character_input: CharacterInput) -> Character:
        """
        Process a single character input and return a complete Character model.
        
        Args:
            character_input: Input data for character processing
            
        Returns:
            Complete Character model
        """
        pass
    
    @abstractmethod
    def process_multiple_characters(self, character_inputs: List[CharacterInput]) -> List[Character]:
        """
        Process multiple character inputs.
        
        Args:
            character_inputs: List of character input data
            
        Returns:
            List of processed Character models
        """
        pass
    
    @abstractmethod
    def save_character(self, character: Character, filename: str = None) -> Path:
        """
        Save character to file.
        
        Args:
            character: Character model to save
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        pass
    
    @abstractmethod
    def load_character(self, filename: str) -> Character:
        """
        Load character from file.
        
        Args:
            filename: Name of character file
            
        Returns:
            Character model
        """
        pass
    
    @abstractmethod
    def validate_character(self, character: Character) -> bool:
        """
        Validate character data completeness.
        
        Args:
            character: Character to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass