from typing import Optional
from dataclasses import dataclass

@dataclass
class Character:
    """Represents a character in the book with detailed description."""
    name: str
    description: str
    role: str = "main"  # main, secondary, background
    image_source: Optional[str] = None  # "text" or "image" - how the description was created
    
    def __post_init__(self):
        """Validate character data after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Character name cannot be empty")
        if not self.description or not self.description.strip():
            raise ValueError("Character description cannot be empty")
        if self.role not in ["main", "secondary", "background"]:
            self.role = "main"  # Default to main if invalid role provided 