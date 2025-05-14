# data_models/story_content.py
from typing import List, Optional
from dataclasses import dataclass, field
from .book_plan import BookPlan # Assuming BookPlan is in the same directory or accessible

@dataclass
class ImagePlaceholder:
    """Represents a placeholder for an image within the story text."""
    id: str  # Unique identifier for the image, e.g., "chapter1_image1"
    description: str # Textual description of the image to be generated

@dataclass
class ChapterContent:
    """Represents the content of a single chapter."""
    title: str
    text_markdown: str # The full text of the chapter in Markdown format
    image_placeholders: List[ImagePlaceholder] = field(default_factory=list)

@dataclass
class StoryContent:
    """Represents the complete story content, including all chapters and image details."""
    book_plan: BookPlan # The plan this story is based on
    chapters_content: List[ChapterContent]
    cover_image_prompt: str # Specific prompt for the cover image

    @property
    def all_image_placeholders(self) -> List[ImagePlaceholder]:
        """Returns a flat list of all image placeholders from all chapters."""
        placeholders = []
        for chapter in self.chapters_content:
            placeholders.extend(chapter.image_placeholders)
        return placeholders

