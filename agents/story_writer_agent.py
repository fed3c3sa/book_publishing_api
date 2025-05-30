# agents/story_writer_agent.py
from .base_agent import BaseBookAgent
from smolagents import InferenceClientModel # Ensure InferenceClientModel is imported for type hinting
from typing import List, Dict, Any, Optional
from data_models.book_plan import BookPlan
from data_models.story_content import StoryContent, ChapterContent, ImagePlaceholder
import re # For parsing image placeholders

class StoryWriterAgent(BaseBookAgent):
    """Agent responsible for writing the story content based on the book plan."""

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
        Writes the full story based on the provided book plan.

        Args:
            book_plan (BookPlan): The detailed plan for the book.
            style_example (Optional[str]): Example text for style imitation.

        Returns:
            StoryContent: The generated story content with image placeholders.
        """
        chapters_content = []
        all_image_placeholders = []

        for i, chapter_outline in enumerate(book_plan.chapters):
            print(f"StoryWriterAgent: Writing chapter {i+1}: {chapter_outline.title}")
            prompt_template = self.load_prompt_template("write_chapter_prompt")
            
            formatted_prompt = prompt_template.format(
                book_plan_title=book_plan.title,
                book_plan_genre=book_plan.genre,
                book_plan_target_audience=book_plan.target_audience,
                book_plan_writing_style=book_plan.writing_style_guide,
                chapter_title=chapter_outline.title,
                chapter_summary=chapter_outline.summary,
                num_images=chapter_outline.image_placeholders_needed,
                style_example=style_example if style_example else "N/A"
            )
            
            print(f"StoryWriterAgent: (Placeholder) LLM would generate text for 	'{chapter_outline.title}'	. Simulating text generation.")
            # chapter_text_raw = self.execute(formatted_prompt)
            # Placeholder response for now
            chapter_text_raw = f"This is the rich and engaging content for chapter 	'{chapter_outline.title}'	. It elaborates on {chapter_outline.summary}. "
            for img_idx in range(chapter_outline.image_placeholders_needed):
                chapter_text_raw += f" [IMAGE: A descriptive scene for image {img_idx+1} in {chapter_outline.title}]"
            chapter_text_raw += " The chapter concludes with an exciting cliffhanger."

            current_chapter_placeholders = []
            # Use regex to find placeholders like [IMAGE: description]
            placeholder_matches = re.findall(r"\[IMAGE: (.*?)\]", chapter_text_raw)
            
            temp_chapter_text = chapter_text_raw
            for idx, desc in enumerate(placeholder_matches):
                placeholder_id = f"chapter{i+1}_image{idx+1}" # Create a unique ID for the placeholder
                current_chapter_placeholders.append(ImagePlaceholder(id=placeholder_id, description=desc))
                # Replace the found placeholder with one that includes the ID for later mapping
                temp_chapter_text = temp_chapter_text.replace(f"[IMAGE: {desc}]", f"[IMAGE: {placeholder_id}]", 1)
            chapter_text_markdown = temp_chapter_text

            chapters_content.append(ChapterContent(
                title=chapter_outline.title,
                text_markdown=chapter_text_markdown,
                image_placeholders=current_chapter_placeholders
            ))
            all_image_placeholders.extend(current_chapter_placeholders)

        story_content = StoryContent(
            book_plan=book_plan,
            chapters_content=chapters_content,
            cover_image_prompt=book_plan.cover_concept # Get cover prompt from book plan
        )
        print(f"StoryWriterAgent: Generated story content - {len(story_content.chapters_content)} chapters.")
        return story_content

