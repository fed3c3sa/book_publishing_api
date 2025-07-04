"""
Text generation module for the Children's Book Generator.

This module handles creating engaging, age-appropriate text content for
each page of the children's book.
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from ..ai_clients.openai_client import OpenAIClient
from ..utils.config import load_prompt, get_output_path, TEXTS_DIR


class StoryContext:
    """
    Tracks story consistency across pages using structured narrative elements.
    
    Based on research into maintaining AI narrative consistency, this class
    implements persistent memory management to prevent story inconsistencies.
    """
    
    def __init__(self):
        """Initialize story context with empty tracking structures."""
        self.story_summary: str = ""
        self.character_states: Dict[str, Dict[str, Any]] = {}
        self.plot_points: List[Dict[str, Any]] = []
        self.themes_developed: List[str] = []
        self.mood_progression: List[str] = []
        self.key_locations: List[str] = []
        self.story_tensions: List[str] = []
        self.page_summaries: List[str] = []
    
    def update_from_page(
        self,
        page_data: Dict[str, Any],
        generated_text: Dict[str, Any],
        book_plan: Dict[str, Any]
    ) -> None:
        """
        Update story context based on a newly generated page.
        
        Args:
            page_data: Page information from book plan
            generated_text: Generated text data for this page
            book_plan: Complete book plan data
        """
        page_number = page_data.get("page_number", 0)
        page_text = generated_text.get("page_text", "")
        
        # Update page summaries
        scene_description = page_data.get("scene_description", "")
        page_summary = f"Page {page_number}: {scene_description}"
        self.page_summaries.append(page_summary)
        
        # Update story summary (keep last 3 page summaries for context)
        recent_summaries = self.page_summaries[-3:]
        self.story_summary = " -> ".join(recent_summaries)
        
        # Track characters present and their states
        characters_present = page_data.get("characters_present", [])
        for character in characters_present:
            if character not in self.character_states:
                self.character_states[character] = {
                    "first_appearance": page_number,
                    "interactions": [],
                    "emotional_state": "neutral",
                    "location": "",
                    "key_attributes": []
                }
            
            # Update character location if specified
            visual_elements = page_data.get("visual_elements", [])
            for element in visual_elements:
                if any(loc_word in element.lower() for loc_word in ["garden", "house", "forest", "park", "school"]):
                    self.character_states[character]["location"] = element
                    if element not in self.key_locations:
                        self.key_locations.append(element)
        
        # Extract and track plot points
        if page_text:
            # Simple heuristic: look for action verbs or emotional content
            action_indicators = ["decided", "found", "discovered", "learned", "helped", "shared", "gave", "asked"]
            for indicator in action_indicators:
                if indicator in page_text.lower():
                    plot_point = {
                        "page": page_number,
                        "action": indicator,
                        "description": scene_description[:100],
                        "characters_involved": characters_present
                    }
                    self.plot_points.append(plot_point)
                    break
        
        # Track themes from book plan
        book_themes = book_plan.get("themes", [])
        for theme in book_themes:
            if theme not in self.themes_developed and any(
                theme_word in page_text.lower() 
                for theme_word in theme.split()
            ):
                self.themes_developed.append(theme)
        
        # Track mood progression based on page content
        mood_indicators = {
            "happy": ["happy", "joy", "smile", "laugh", "excited", "cheerful"],
            "sad": ["sad", "cry", "worried", "upset", "disappointed"],
            "curious": ["wonder", "curious", "explore", "discover", "question"],
            "determined": ["decided", "determined", "tried", "worked", "effort"],
            "peaceful": ["calm", "peaceful", "quiet", "gentle", "serene"]
        }
        
        current_mood = "neutral"
        for mood, indicators in mood_indicators.items():
            if any(indicator in page_text.lower() for indicator in indicators):
                current_mood = mood
                break
        
        if not self.mood_progression or self.mood_progression[-1] != current_mood:
            self.mood_progression.append(current_mood)
        
        # Track story tensions (conflicts or challenges)
        tension_indicators = ["problem", "trouble", "worried", "afraid", "challenge", "difficult", "lost", "broke"]
        for indicator in tension_indicators:
            if indicator in page_text.lower() and indicator not in self.story_tensions:
                self.story_tensions.append(f"Page {page_number}: {indicator}")
    
    def get_context_for_generation(self) -> str:
        """
        Generate a context string for AI text generation.
        
        Returns:
            Formatted context string summarizing story so far
        """
        context_parts = []
        
        if self.story_summary:
            context_parts.append(f"Story so far: {self.story_summary}")
        
        if self.character_states:
            char_info = []
            for char, state in self.character_states.items():
                location = f" (at {state['location']})" if state['location'] else ""
                char_info.append(f"{char}{location}")
            context_parts.append(f"Characters: {', '.join(char_info)}")
        
        if self.themes_developed:
            context_parts.append(f"Themes established: {', '.join(self.themes_developed)}")
        
        if self.mood_progression:
            current_mood = self.mood_progression[-1]
            context_parts.append(f"Current mood: {current_mood}")
        
        if self.story_tensions:
            recent_tensions = self.story_tensions[-2:]  # Last 2 tensions
            context_parts.append(f"Story tensions: {'; '.join(recent_tensions)}")
        
        return " | ".join(context_parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert story context to dictionary for serialization.
        
        Returns:
            Dictionary representation of story context
        """
        return {
            "story_summary": self.story_summary,
            "character_states": self.character_states,
            "plot_points": self.plot_points,
            "themes_developed": self.themes_developed,
            "mood_progression": self.mood_progression,
            "key_locations": self.key_locations,
            "story_tensions": self.story_tensions,
            "page_summaries": self.page_summaries
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoryContext':
        """
        Create StoryContext from dictionary data.
        
        Args:
            data: Dictionary representation of story context
            
        Returns:
            StoryContext instance
        """
        context = cls()
        context.story_summary = data.get("story_summary", "")
        context.character_states = data.get("character_states", {})
        context.plot_points = data.get("plot_points", [])
        context.themes_developed = data.get("themes_developed", [])
        context.mood_progression = data.get("mood_progression", [])
        context.key_locations = data.get("key_locations", [])
        context.story_tensions = data.get("story_tensions", [])
        context.page_summaries = data.get("page_summaries", [])
        return context


class TextGenerator:
    """Handles text generation for book pages."""
    
    def __init__(self, openai_client: Optional[OpenAIClient] = None):
        """
        Initialize the text generator.
        
        Args:
            openai_client: OpenAI client instance. If None, creates a new one.
        """
        self.openai_client = openai_client or OpenAIClient()
        self.text_prompt_template = load_prompt("text_generation")
    
    def generate_page_text(
        self,
        page_data: Dict[str, Any],
        book_plan: Dict[str, Any],
        story_context: Optional[StoryContext] = None,
        previous_page_text: str = "",
        language: str = "English"
    ) -> Tuple[Dict[str, Any], StoryContext]:
        """
        Generate text content for a specific book page with story consistency tracking.
        
        Args:
            page_data: Page information from book plan
            book_plan: Complete book plan data
            story_context: Current story context for consistency tracking
            previous_page_text: Text from the previous page for context (deprecated, use story_context)
            language: Language for the text content
            
        Returns:
            Tuple of (structured page text data, updated story context)
        """
        # Initialize story context if not provided
        if story_context is None:
            story_context = StoryContext()
        
        # Extract page information
        page_description = page_data.get("scene_description", "")
        characters_present = page_data.get("characters_present", [])
        age_group = book_plan.get("target_age", "3-6")
        book_theme = ", ".join(book_plan.get("themes", ["adventure", "friendship"]))
        
        # Get story arc information
        story_arc = json.dumps(book_plan.get("story_arc", {}))
        
        # Use story context for rich previous context instead of just previous page text
        if story_context.story_summary or story_context.character_states:
            context_summary = story_context.get_context_for_generation()
            # Combine story context with previous page text for better transitions
            if previous_page_text:
                previous_context = f"STORY CONTEXT: {context_summary}\n\nPREVIOUS PAGE: {previous_page_text}"
            else:
                previous_context = context_summary
        else:
            previous_context = previous_page_text
        
        # Generate page text using OpenAI
        page_text_data = self.openai_client.generate_page_text(
            page_description=page_description,
            characters_present=characters_present,
            age_group=age_group,
            language=language,
            book_theme=book_theme,
            previous_context=previous_context,
            story_arc=story_arc,
            prompt_template=self.text_prompt_template
        )
        
        # Add page metadata
        page_text_data["page_metadata"] = {
            "page_number": page_data.get("page_number", 0),
            "page_type": page_data.get("page_type", "story"),
            "characters_present": characters_present
        }
        
        # Update story context with the newly generated content
        updated_context = StoryContext.from_dict(story_context.to_dict())  # Deep copy
        updated_context.update_from_page(page_data, page_text_data, book_plan)
        
        return page_text_data, updated_context
    
    def generate_all_page_texts(
        self,
        book_plan: Dict[str, Any],
        language: str = "English"
    ) -> Dict[int, Dict[str, Any]]:
        """
        Generate text for all pages in the book with story consistency tracking.
        
        Args:
            book_plan: Complete book plan data
            language: Language for the text content
            
        Returns:
            Dictionary mapping page numbers to text data
        """
        book_title = book_plan.get("book_title", "Untitled Book")
        pages = book_plan.get("pages", [])
        
        generated_texts = {}
        story_context = StoryContext()  # Initialize story context for consistency
        previous_page_text = ""  # Track previous page text for smooth transitions
        
        # Generate text for each page
        for page_data in pages:
            page_number = page_data.get("page_number", 0)
            page_type = page_data.get("page_type", "story")
            
            # Skip cover page
            if page_type == "cover":
                continue
            
            try:
                text_data, story_context = self.generate_page_text(
                    page_data=page_data,
                    book_plan=book_plan,
                    story_context=story_context,
                    previous_page_text=previous_page_text,
                    language=language
                )
                
                # Save the text data
                self._save_page_text(text_data, book_title, page_number)
                
                # Update previous page text for next iteration
                previous_page_text = text_data.get("page_text", "")
                
                generated_texts[page_number] = text_data
                print(f"Generated text for page {page_number} with story context")
                
            except Exception as e:
                print(f"Error generating text for page {page_number}: {str(e)}")
                continue
        
        # Save final story context for potential future use or debugging
        self._save_story_context(story_context, book_title)
        
        return generated_texts
    
    def _save_page_text(
        self,
        text_data: Dict[str, Any],
        book_title: str,
        page_number: int
    ) -> Path:
        """
        Save page text data to a JSON file.
        
        Args:
            text_data: Page text data dictionary
            book_title: Book title for organization
            page_number: Page number
            
        Returns:
            Path to the saved file
        """
        # Create book-specific directory
        book_texts_dir = self._get_book_texts_dir(book_title)
        
        # Save text data
        filename = f"page_{page_number:02d}_text.json"
        output_path = book_texts_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(text_data, f, indent=2, ensure_ascii=False)
        
        # Also save plain text version for easy access
        plain_text = text_data.get("page_text", "")
        plain_text_path = book_texts_dir / f"page_{page_number:02d}_text.txt"
        
        with open(plain_text_path, 'w', encoding='utf-8') as f:
            f.write(plain_text)
        
        return output_path
    
    def _get_book_texts_dir(self, book_title: str) -> Path:
        """
        Get the texts directory for a specific book.
        
        Args:
            book_title: Book title
            
        Returns:
            Path to the book's texts directory
        """
        # Clean book title for directory name
        clean_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_title = clean_title.replace(' ', '_').lower()
        
        book_texts_dir = TEXTS_DIR / clean_title
        book_texts_dir.mkdir(parents=True, exist_ok=True)
        
        return book_texts_dir
    
    def load_page_text(self, book_title: str, page_number: int) -> Dict[str, Any]:
        """
        Load page text data from a JSON file.
        
        Args:
            book_title: Book title
            page_number: Page number
            
        Returns:
            Page text data dictionary
        """
        book_texts_dir = self._get_book_texts_dir(book_title)
        file_path = book_texts_dir / f"page_{page_number:02d}_text.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Page text file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_all_page_texts(self, book_title: str) -> Dict[int, Dict[str, Any]]:
        """
        Get all page texts for a book.
        
        Args:
            book_title: Book title
            
        Returns:
            Dictionary mapping page numbers to text data
        """
        book_texts_dir = self._get_book_texts_dir(book_title)
        
        if not book_texts_dir.exists():
            raise FileNotFoundError(f"Book texts directory not found: {book_texts_dir}")
        
        page_texts = {}
        
        # Find all JSON text files
        for file_path in book_texts_dir.glob("page_*_text.json"):
            try:
                # Extract page number from filename
                filename = file_path.name
                page_number = int(filename.split("_")[1])
                
                # Load text data
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_data = json.load(f)
                
                page_texts[page_number] = text_data
                
            except (ValueError, IndexError, json.JSONDecodeError) as e:
                print(f"Error loading text file {file_path}: {str(e)}")
                continue
        
        return page_texts
    
    def _save_story_context(
        self,
        story_context: StoryContext,
        book_title: str
    ) -> Path:
        """
        Save story context data to a JSON file.
        
        Args:
            story_context: Story context to save
            book_title: Book title for organization
            
        Returns:
            Path to the saved file
        """
        book_texts_dir = self._get_book_texts_dir(book_title)
        context_path = book_texts_dir / "story_context.json"
        
        with open(context_path, 'w', encoding='utf-8') as f:
            json.dump(story_context.to_dict(), f, indent=2, ensure_ascii=False)
        
        return context_path

