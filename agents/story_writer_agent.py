# agents/story_writer_agent.py
from .base_agent import BaseBookAgent
from smolagents import InferenceClientModel # Ensure InferenceClientModel is imported for type hinting
from typing import List, Dict, Any, Optional
from data_models.book_plan import BookPlan
from data_models.story_content import StoryContent, ChapterContent, ImagePlaceholder
import re # For parsing image placeholders

class StoryWriterAgent(BaseBookAgent):
    """Agent responsible for writing the complete story content based on the book plan."""

    def __init__(self, model: InferenceClientModel, tools: List[callable] = None, **kwargs):
        """
        Initializes the StoryWriterAgent.

        Args:
            model (InferenceClientModel): An instantiated language model client.
            tools (List[callable], optional): A list of tools available to the agent. Defaults to an empty list.
            **kwargs: Additional arguments for CodeAgent.
        """
        agent_tools = tools if tools is not None else []
        super().__init__(
            model=model, # Pass the model instance directly
            tools=agent_tools,
            system_prompt_path="/home/federico/Desktop/personal/book_publishing_api/prompts/story_writer_prompts.yaml",
            **kwargs
        )

    def write_story(self, book_plan: BookPlan, style_example: Optional[str] = None) -> StoryContent:
        """
        Writes the complete story based on the provided book plan.

        Args:
            book_plan (BookPlan): The detailed plan for the book.
            style_example (Optional[str]): Example text for style imitation.

        Returns:
            StoryContent: The generated story content with image placeholders.
        """
        print(f"StoryWriterAgent: Writing complete book '{book_plan.title}'")
        
        prompt_template = self.load_prompt_template("write_complete_book_prompt")
        
        # Prepare chapter outlines as text
        chapter_outlines_text = ""
        total_images = 0
        for i, chapter in enumerate(book_plan.chapters, 1):
            chapter_outlines_text += f"Chapter {i}: {chapter.title}\n"
            chapter_outlines_text += f"Summary: {chapter.summary}\n"
            chapter_outlines_text += f"Images needed: {chapter.image_placeholders_needed}\n\n"
            total_images += chapter.image_placeholders_needed
        
        formatted_prompt = prompt_template.format(
            book_plan_title=book_plan.title,
            book_plan_genre=book_plan.genre,
            book_plan_target_audience=book_plan.target_audience,
            book_plan_writing_style=book_plan.writing_style_guide,
            book_plan_theme=book_plan.theme or "N/A",
            book_plan_key_elements=", ".join(book_plan.key_elements) if book_plan.key_elements else "N/A",
            chapter_outlines=chapter_outlines_text,
            image_style_guide=book_plan.image_style_guide,
            style_example=style_example if style_example else "N/A",
            total_images=total_images
        )
        
        complete_book_text = ""
        try:
            # Execute the LLM with the formatted prompt to write the entire book
            complete_book_text = self.run(formatted_prompt)
            print(f"StoryWriterAgent: Successfully generated complete book content")
            
        except Exception as e:
            print(f"StoryWriterAgent: Error generating complete book content: {e}")
            print(f"StoryWriterAgent: Using fallback content")
            
            # Create fallback content for the entire book
            complete_book_text = f"# {book_plan.title}\n\n"
            for i, chapter in enumerate(book_plan.chapters, 1):
                complete_book_text += f"## Chapter {i}: {chapter.title}\n\n"
                complete_book_text += f"This is the engaging content for chapter '{chapter.title}'. "
                complete_book_text += f"It tells the story of {chapter.summary}. "
                
                # Add image placeholders
                for img_idx in range(chapter.image_placeholders_needed):
                    if img_idx == 0:
                        complete_book_text += f"[IMAGE: Opening scene for {chapter.title}] "
                    else:
                        complete_book_text += f"[IMAGE: {chapter.title} - scene {img_idx + 1}] "
                
                complete_book_text += "The chapter continues with exciting developments and transitions smoothly to the next part of the story.\n\n"

        # Parse the complete book text into chapters
        chapters_content_list: List[ChapterContent] = []
        all_image_placeholders: List[ImagePlaceholder] = []
        
        # Split the book text into chapters using markdown headers
        chapter_pattern = r'##?\s*Chapter\s*\d+:?\s*([^\n]+)'
        chapter_matches = list(re.finditer(chapter_pattern, complete_book_text, re.IGNORECASE))
        
        for i, match in enumerate(chapter_matches):
            # Extract chapter title from the match
            chapter_title = match.group(1).strip()
            
            # Find the start and end of the chapter content
            chapter_start = match.end()
            if i + 1 < len(chapter_matches):
                chapter_end = chapter_matches[i + 1].start()
            else:
                chapter_end = len(complete_book_text)
            
            chapter_text = complete_book_text[chapter_start:chapter_end].strip()
            
            # Find image placeholders in this chapter
            current_chapter_placeholders = []
            placeholder_matches = re.findall(r"\[IMAGE: (.*?)\]", chapter_text)
            
            temp_chapter_text = chapter_text
            for idx, desc in enumerate(placeholder_matches):
                placeholder_id = f"chapter{i+1}_image{idx+1}"
                current_chapter_placeholders.append(ImagePlaceholder(id=placeholder_id, description=desc))
                # Replace the found placeholder with one that includes the ID
                temp_chapter_text = temp_chapter_text.replace(f"[IMAGE: {desc}]", f"[IMAGE: {placeholder_id}]", 1)
            
            chapters_content_list.append(ChapterContent(
                title=chapter_title,
                text_markdown=temp_chapter_text,
                image_placeholders=current_chapter_placeholders
            ))
            all_image_placeholders.extend(current_chapter_placeholders)

        # If no chapters were found in the text, treat the entire text as one book
        if not chapters_content_list:
            print("StoryWriterAgent: No chapter markers found, treating as single chapter")
            # Find all image placeholders in the complete text
            all_placeholders = []
            placeholder_matches = re.findall(r"\[IMAGE: (.*?)\]", complete_book_text)
            
            temp_text = complete_book_text
            for idx, desc in enumerate(placeholder_matches):
                placeholder_id = f"chapter1_image{idx+1}"
                all_placeholders.append(ImagePlaceholder(id=placeholder_id, description=desc))
                temp_text = temp_text.replace(f"[IMAGE: {desc}]", f"[IMAGE: {placeholder_id}]", 1)
            
            chapters_content_list.append(ChapterContent(
                title=book_plan.title,
                text_markdown=temp_text,
                image_placeholders=all_placeholders
            ))
            all_image_placeholders.extend(all_placeholders)

        story_content = StoryContent(
            book_plan=book_plan,
            chapters_content=chapters_content_list,
            cover_image_prompt=book_plan.cover_concept
        )
        
        print(f"StoryWriterAgent: Generated complete story content - {len(story_content.chapters_content)} chapters, "
              f"{len(all_image_placeholders)} total image placeholders.")
        return story_content