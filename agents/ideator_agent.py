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

    def generate_initial_idea(self, user_prompt: str, trend_analysis: Optional[Dict[str, Any]] = None) -> BookPlan:
        """
        Generates a detailed book plan based on a user prompt and optional trend analysis.

        Args:
            user_prompt (str): The user's initial idea or requirements for the book.
            trend_analysis (Optional[Dict[str, Any]]): Optional trend data to inform the idea.

        Returns:
            BookPlan: A detailed plan for the book.
        """
        prompt_template = self.load_prompt_template("generate_book_plan_prompt")
        
        trend_info_str = "No trend analysis provided." 
        if trend_analysis:
            trend_info_str = json.dumps(trend_analysis, indent=2)

        formatted_prompt = prompt_template.format(
            user_prompt=user_prompt,
            trend_analysis=trend_info_str
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
            plan_dict = {
                "title": "The Magical Forest Adventure",
                "genre": "Children's Fantasy",
                "target_audience": "Ages 6-10",
                "writing_style_guide": "Simple, engaging language with vivid descriptions. Positive and encouraging tone.",
                "image_style_guide": "Colorful, whimsical illustrations. Friendly characters. Bright and inviting scenes.",
                "cover_concept": "A group of diverse children and friendly animals at the entrance of a vibrant, sunlit magical forest.",
                "chapters": [
                    {"title": "The Mysterious Map", "summary": "Children find a mysterious map in their grandmother's attic.", "image_placeholders_needed": 2},
                    {"title": "Journey into the Whispering Woods", "summary": "They follow the map into a local woods that transforms into a magical forest.", "image_placeholders_needed": 3},
                    {"title": "Meeting the Forest Guardians", "summary": "The children meet talking animals who are guardians of the forest.", "image_placeholders_needed": 2}
                ],
                "theme": "Friendship and adventure",
                "key_elements": ["Magical transformation", "Animal friends", "Discovery and wonder"]
            }
        except Exception as e:
            print(f"IdeatorAgent: Unexpected error during LLM execution: {e}. Using fallback plan.")
            # More comprehensive fallback for any other execution errors
            plan_dict = {
                "title": "The Little Dragon Who Couldn't Breathe Fire",
                "genre": "Children's Picture Book",
                "target_audience": "Ages 3-6",
                "writing_style_guide": "Simple, repetitive, and rhythmic language. Focus on themes of friendship, perseverance, and self-acceptance. Short sentences, easy vocabulary. Encouraging and warm tone.",
                "image_style_guide": "Soft, watercolor-style illustrations. Cute and expressive characters. Pastel color palette. Full-page spreads with minimal text overlay where appropriate.",
                "cover_concept": "A small, sad-looking green dragon trying to puff out a tiny wisp of smoke, with friendly animal friends looking on encouragingly. Sunny meadow background.",
                "chapters": [
                    {"title": "Sparky's Big Problem", "summary": "Introduce Sparky, a little dragon who can't breathe fire like his friends. He feels sad and left out.", "image_placeholders_needed": 1},
                    {"title": "Trying Everything", "summary": "Sparky tries different funny ways to make fire (eating spicy peppers, jumping up and down) but nothing works.", "image_placeholders_needed": 2},
                    {"title": "A Kind Friend", "summary": "Sparky meets a wise old owl who tells him everyone has unique talents.", "image_placeholders_needed": 1},
                    {"title": "Discovering a New Talent", "summary": "Sparky discovers he can blow beautiful, sparkling bubbles instead of fire, which delight his friends.", "image_placeholders_needed": 2},
                    {"title": "The Bubble Festival", "summary": "Sparky becomes the star of the annual forest festival with his amazing bubble show, learning to embrace his uniqueness.", "image_placeholders_needed": 1}
                ],
                "theme": "Self-acceptance and celebrating differences",
                "key_elements": ["Cute dragon character", "Supportive friends", "Problem-solving", "Happy resolution"]
            }

        # Generate unique project ID
        project_id = f"book_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        # Create BookPlan object from the parsed (or fallback) dictionary
        book_plan = BookPlan(
            project_id=project_id,
            title=plan_dict.get("title", "Untitled Book"),
            genre=plan_dict.get("genre", "Unknown Genre"),
            target_audience=plan_dict.get("target_audience", "General Audience"),
            writing_style_guide=plan_dict.get("writing_style_guide", "Standard writing style."),
            image_style_guide=plan_dict.get("image_style_guide", "Standard image style."),
            cover_concept=plan_dict.get("cover_concept", "A generic book cover."),
            chapters=[ChapterOutline(**ch) for ch in plan_dict.get("chapters", [])],
            theme=plan_dict.get("theme"),
            key_elements=plan_dict.get("key_elements", [])
        )
        
        print(f"IdeatorAgent: Generated book plan for '{book_plan.title}' with Project ID: {book_plan.project_id}")
        return book_plan