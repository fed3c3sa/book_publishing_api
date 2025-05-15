# data_models/book_plan.py
from typing import List, Optional
from dataclasses import dataclass, field

@dataclass
class ChapterOutline:
    """Represents the outline for a single chapter."""
    title: str
    summary: str
    image_placeholders_needed: int = 0 # Number of images expected for this chapter

@dataclass
class BookPlan:
    """Represents the overall plan for the book."""
    title: str
    genre: str
    target_audience: str
    writing_style_guide: str # Detailed description of the desired writing style
    image_style_guide: str   # Detailed description of the desired image style
    cover_concept: str       # Description or prompt for the book cover
    chapters: List[ChapterOutline]
    project_id: str # Unique ID for this book project
    # Optional fields for more detailed planning
    theme: Optional[str] = None
    key_elements: Optional[List[str]] = field(default_factory=list)
    estimated_word_count: Optional[int] = None

