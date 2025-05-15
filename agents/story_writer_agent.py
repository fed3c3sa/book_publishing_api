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
        chapters_content_list: List[ChapterContent] = []
        all_image_placeholders: List[ImagePlaceholder] = []
        
        # Store previously written chapter texts (markdown) for context
        written_chapter_texts_markdown: List[str] = [] 

        for i, chapter_outline in enumerate(book_plan.chapters):
            current_chapter_number = i + 1
            print(f"StoryWriterAgent: Writing chapter {current_chapter_number}: {chapter_outline.title}")
            
            prompt_template = self.load_prompt_template("write_chapter_prompt")
            
            # --- Prepare context from previous chapters ---
            previous_chapter_summaries_str = "N/A"
            if i > 0:
                summaries = []
                # Iterate through the outlines of previously planned chapters
                for j in range(i): 
                    prev_chap_outline = book_plan.chapters[j]
                    summaries.append(f"Chapter {j+1} - {prev_chap_outline.title}: {prev_chap_outline.summary}")
                previous_chapter_summaries_str = "\n".join(summaries)

            previous_chapter_full_text = "N/A"
            if i > 0 and written_chapter_texts_markdown:
                # Get the text of the immediately preceding chapter
                previous_chapter_full_text = written_chapter_texts_markdown[i-1]
            # --- End of context preparation ---

            formatted_prompt = prompt_template.format(
                book_plan_title=book_plan.title,
                book_plan_genre=book_plan.genre,
                book_plan_target_audience=book_plan.target_audience,
                book_plan_writing_style=book_plan.writing_style_guide,
                
                # New context variables
                previous_chapter_summaries=previous_chapter_summaries_str,
                previous_chapter_text=previous_chapter_full_text,
                chapter_number=current_chapter_number,
                
                chapter_title=chapter_outline.title,
                chapter_summary=chapter_outline.summary,
                num_images=chapter_outline.image_placeholders_needed,
                style_example=style_example if style_example else "N/A"
            )
            
            chapter_text_raw = "" # Initialize to ensure it's defined
            try:
                # Execute the LLM with the formatted prompt
                chapter_text_raw = self.run(formatted_prompt)
                print(f"StoryWriterAgent: Successfully generated content for '{chapter_outline.title}'")
                
            except Exception as e:
                print(f"StoryWriterAgent: Error generating content for '{chapter_outline.title}': {e}")
                print(f"StoryWriterAgent: Using fallback content for chapter '{chapter_outline.title}'")
                
                # Fallback content generation if LLM fails
                chapter_text_raw = f"This is the rich and engaging content for chapter '{chapter_outline.title}'. It elaborates on {chapter_outline.summary}. "
                
                # Add image placeholders to the fallback content
                for img_idx in range(chapter_outline.image_placeholders_needed):
                    if img_idx == 0:
                        chapter_text_raw += f" [IMAGE: {chapter_outline.title} - opening scene illustration for Chapter {current_chapter_number}]"
                    elif img_idx == chapter_outline.image_placeholders_needed - 1:
                        chapter_text_raw += f" [IMAGE: {chapter_outline.title} - concluding scene illustration for Chapter {current_chapter_number}]"
                    else:
                        chapter_text_raw += f" [IMAGE: {chapter_outline.title} - mid-chapter action scene {img_idx} for Chapter {current_chapter_number}]"
                
                chapter_text_raw += " The chapter concludes with an exciting transition to the next part of the story."

            current_chapter_placeholders = []
            # Use regex to find placeholders like [IMAGE: description]
            placeholder_matches = re.findall(r"\[IMAGE: (.*?)\]", chapter_text_raw)
            
            temp_chapter_text = chapter_text_raw
            for idx, desc in enumerate(placeholder_matches):
                placeholder_id = f"chapter{current_chapter_number}_image{idx+1}" # Create a unique ID for the placeholder
                current_chapter_placeholders.append(ImagePlaceholder(id=placeholder_id, description=desc))
                # Replace the found placeholder with one that includes the ID for later mapping
                temp_chapter_text = temp_chapter_text.replace(f"[IMAGE: {desc}]", f"[IMAGE: {placeholder_id}]", 1)
            chapter_text_markdown = temp_chapter_text

            # Store the generated markdown text for the next iteration's context
            written_chapter_texts_markdown.append(chapter_text_markdown)

            # Validate that we have the expected number of image placeholders
            if len(current_chapter_placeholders) != chapter_outline.image_placeholders_needed:
                print(f"StoryWriterAgent: Warning - Expected {chapter_outline.image_placeholders_needed} image placeholders "
                      f"but found {len(current_chapter_placeholders)} in chapter '{chapter_outline.title}'")

            chapters_content_list.append(ChapterContent(
                title=chapter_outline.title,
                text_markdown=chapter_text_markdown,
                image_placeholders=current_chapter_placeholders
            ))
            all_image_placeholders.extend(current_chapter_placeholders)

        story_content = StoryContent(
            book_plan=book_plan,
            chapters_content=chapters_content_list, # Use the correctly typed list
            cover_image_prompt=book_plan.cover_concept # Get cover prompt from book plan
        )
        print(f"StoryWriterAgent: Generated story content - {len(story_content.chapters_content)} chapters, "
              f"{len(all_image_placeholders)} total image placeholders.")
        return story_content