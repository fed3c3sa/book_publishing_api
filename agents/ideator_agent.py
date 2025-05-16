# agents/ideator_agent.py
from .base_agent import BaseBookAgent
from smolagents import InferenceClientModel # Ensure InferenceClientModel is imported for type hinting
from typing import List, Dict, Any, Optional
from data_models.book_plan import BookPlan, ChapterOutline
import json # For parsing LLM output if it's JSON
import uuid
from datetime import datetime

class IdeatorAgent(BaseBookAgent):
    """Agent responsible for generating the initial book idea and plan."""

    def __init__(self, model: InferenceClientModel, tools: List[callable] = None, **kwargs):
        """
        Initializes the IdeatorAgent.

        Args:
            model (InferenceClientModel): An instantiated language model client.
            tools (List[callable], optional): A list of tools available to the agent. Defaults to an empty list.
            **kwargs: Additional arguments for CodeAgent.
        """
        agent_tools = tools if tools is not None else []
        super().__init__(
            model=model, # Pass the model instance directly
            tools=agent_tools,
            system_prompt_path="/home/federico/Desktop/personal/book_publishing_api/prompts/ideator_prompts.yaml",
            **kwargs
        )

    def generate_initial_idea(self, 
                            user_prompt: str, 
                            trend_analysis: Optional[Dict[str, Any]] = None, 
                            title: Optional[str] = None,
                            genre: Optional[str] = None,
                            target_audience: Optional[str] = None,
                            writing_style_guide: Optional[str] = None,
                            image_style_guide: Optional[str] = None,
                            cover_concept: Optional[str] = None,
                            theme: Optional[str] = None,
                            key_elements: Optional[List[str]] = None) -> BookPlan:
        """
        Generates a detailed book plan based on a user prompt and optional parameters.

        Args:
            user_prompt (str): The user's initial idea or requirements for the book.
            trend_analysis (Optional[Dict[str, Any]]): Optional trend data to inform the idea.
            title (Optional[str]): Optional provisional title for the book.
            genre (Optional[str]): Optional genre specification.
            target_audience (Optional[str]): Optional target audience specification.
            writing_style_guide (Optional[str]): Optional writing style guidelines.
            image_style_guide (Optional[str]): Optional image style guidelines.
            cover_concept (Optional[str]): Optional cover concept description.
            theme (Optional[str]): Optional theme specification.
            key_elements (Optional[List[str]]): Optional list of key elements to include.

        Returns:
            BookPlan: A detailed plan for the book.
        """
        prompt_template = self.load_prompt_template("generate_book_plan_prompt")
        
        trend_info_str = "No trend analysis provided." 
        if trend_analysis:
            trend_info_str = json.dumps(trend_analysis, indent=2)

        # Handle provisional title
        title_str = "No provisional title provided."
        if title:
            title_str = f"Use this provisional title: '{title}'"
            print(f"IdeatorAgent: Using provisional title: {title}")

        # Handle optional parameters
        optional_constraints = []
        
        if genre:
            optional_constraints.append(f"Genre: {genre}")
            print(f"IdeatorAgent: Using specified genre: {genre}")
            
        if target_audience:
            optional_constraints.append(f"Target Audience: {target_audience}")
            print(f"IdeatorAgent: Using specified target audience: {target_audience}")
            
        if writing_style_guide:
            optional_constraints.append(f"Writing Style Guide: {writing_style_guide}")
            print(f"IdeatorAgent: Using specified writing style guide")
            
        if image_style_guide:
            optional_constraints.append(f"Image Style Guide: {image_style_guide}")
            print(f"IdeatorAgent: Using specified image style guide")
            
        if cover_concept:
            optional_constraints.append(f"Cover Concept: {cover_concept}")
            print(f"IdeatorAgent: Using specified cover concept")
            
        if theme:
            optional_constraints.append(f"Theme: {theme}")
            print(f"IdeatorAgent: Using specified theme: {theme}")
            
        if key_elements:
            optional_constraints.append(f"Key Elements: {', '.join(key_elements)}")
            print(f"IdeatorAgent: Using specified key elements: {key_elements}")

        # Combine optional constraints
        constraints_str = "No additional constraints provided."
        if optional_constraints:
            constraints_str = "\n".join(optional_constraints)

        formatted_prompt = prompt_template.format(
            user_prompt=user_prompt,
            trend_analysis=trend_info_str,
            title=title_str,
            additional_constraints=constraints_str
        )
        
        print(f"IdeatorAgent: Generating book plan based on prompt: '{user_prompt[:100]}...'")
        
        try:
            # Execute the LLM with the formatted prompt
            llm_response_dict = self.run(task=formatted_prompt)
            print(f"IdeatorAgent: Received LLM response, attempting to parse as JSON...")
            
            # Try to parse the LLM response as JSON
            plan_dict = json.loads(llm_response_dict)
            print(f"IdeatorAgent: Successfully parsed LLM response as JSON")
            
        except json.JSONDecodeError as e:
            print(f"IdeatorAgent: Error parsing LLM response as JSON: {e}. Using fallback plan.")
            # Fallback plan in case of JSON parsing error
            # Use provided parameters if available, otherwise use fallback values
            fallback_title = title if title else "The Magical Forest Adventure"
            fallback_genre = genre if genre else "Children's Fantasy"
            fallback_target_audience = target_audience if target_audience else "Ages 6-10"
            fallback_writing_style = writing_style_guide if writing_style_guide else "Simple, engaging language with vivid descriptions. Positive and encouraging tone."
            fallback_image_style = image_style_guide if image_style_guide else "Colorful, whimsical illustrations. Friendly characters. Bright and inviting scenes."
            fallback_cover_concept = cover_concept if cover_concept else "A group of diverse children and friendly animals at the entrance of a vibrant, sunlit magical forest."
            fallback_theme = theme if theme else "Friendship and adventure"
            fallback_key_elements = key_elements if key_elements else ["Magical transformation", "Animal friends", "Discovery and wonder"]
            
            plan_dict = {
                "title": fallback_title,
                "genre": fallback_genre,
                "target_audience": fallback_target_audience,
                "writing_style_guide": fallback_writing_style,
                "image_style_guide": fallback_image_style,
                "cover_concept": fallback_cover_concept,
                "chapters": [
                    {"title": "The Mysterious Map", "summary": "Children find a mysterious map in their grandmother's attic.", "image_placeholders_needed": 2},
                    {"title": "Journey into the Whispering Woods", "summary": "They follow the map into a local woods that transforms into a magical forest.", "image_placeholders_needed": 3},
                    {"title": "Meeting the Forest Guardians", "summary": "The children meet talking animals who are guardians of the forest.", "image_placeholders_needed": 2}
                ],
                "theme": fallback_theme,
                "key_elements": fallback_key_elements
            }
        except Exception as e:
            print(f"IdeatorAgent: Unexpected error during LLM execution: {e}. Using fallback plan.")
            # More comprehensive fallback for any other execution errors
            # Use provided parameters if available, otherwise use fallback values
            fallback_title = title if title else "The Little Dragon Who Couldn't Breathe Fire"
            fallback_genre = genre if genre else "Children's Picture Book"
            fallback_target_audience = target_audience if target_audience else "Ages 3-6"
            fallback_writing_style = writing_style_guide if writing_style_guide else "Simple, repetitive, and rhythmic language. Focus on themes of friendship, perseverance, and self-acceptance. Short sentences, easy vocabulary. Encouraging and warm tone."
            fallback_image_style = image_style_guide if image_style_guide else "Soft, watercolor-style illustrations. Cute and expressive characters. Pastel color palette. Full-page spreads with minimal text overlay where appropriate."
            fallback_cover_concept = cover_concept if cover_concept else "A small, sad-looking green dragon trying to puff out a tiny wisp of smoke, with friendly animal friends looking on encouragingly. Sunny meadow background."
            fallback_theme = theme if theme else "Self-acceptance and celebrating differences"
            fallback_key_elements = key_elements if key_elements else ["Cute dragon character", "Supportive friends", "Problem-solving", "Happy resolution"]
            
            plan_dict = {
                "title": fallback_title,
                "genre": fallback_genre,
                "target_audience": fallback_target_audience,
                "writing_style_guide": fallback_writing_style,
                "image_style_guide": fallback_image_style,
                "cover_concept": fallback_cover_concept,
                "chapters": [
                    {"title": "Sparky's Big Problem", "summary": "Introduce Sparky, a little dragon who can't breathe fire like his friends. He feels sad and left out.", "image_placeholders_needed": 1},
                    {"title": "Trying Everything", "summary": "Sparky tries different funny ways to make fire (eating spicy peppers, jumping up and down) but nothing works.", "image_placeholders_needed": 2},
                    {"title": "A Kind Friend", "summary": "Sparky meets a wise old owl who tells him everyone has unique talents.", "image_placeholders_needed": 1},
                    {"title": "Discovering a New Talent", "summary": "Sparky discovers he can blow beautiful, sparkling bubbles instead of fire, which delight his friends.", "image_placeholders_needed": 2},
                    {"title": "The Bubble Festival", "summary": "Sparky becomes the star of the annual forest festival with his amazing bubble show, learning to embrace his uniqueness.", "image_placeholders_needed": 1}
                ],
                "theme": fallback_theme,
                "key_elements": fallback_key_elements
            }

        # Generate unique project ID
        project_id = f"book_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        # Create BookPlan object from the parsed (or fallback) dictionary
        # Use provided parameters to override LLM output if specified
        final_title = title if title else plan_dict.get("title", "Untitled Book")
        final_genre = genre if genre else plan_dict.get("genre", "Unknown Genre")
        final_target_audience = target_audience if target_audience else plan_dict.get("target_audience", "General Audience")
        final_writing_style = writing_style_guide if writing_style_guide else plan_dict.get("writing_style_guide", "Standard writing style.")
        final_image_style = image_style_guide if image_style_guide else plan_dict.get("image_style_guide", "Standard image style.")
        final_cover_concept = cover_concept if cover_concept else plan_dict.get("cover_concept", "A generic book cover.")
        final_theme = theme if theme else plan_dict.get("theme")
        final_key_elements = key_elements if key_elements else plan_dict.get("key_elements", [])
        
        book_plan = BookPlan(
            project_id=project_id,
            title=final_title,
            genre=final_genre,
            target_audience=final_target_audience,
            writing_style_guide=final_writing_style,
            image_style_guide=final_image_style,
            cover_concept=final_cover_concept,
            chapters=[ChapterOutline(**ch) for ch in plan_dict.get("chapters", [])],
            theme=final_theme,
            key_elements=final_key_elements
        )
        
        print(f"IdeatorAgent: Generated book plan for '{book_plan.title}' with Project ID: {book_plan.project_id}")
        return book_plan