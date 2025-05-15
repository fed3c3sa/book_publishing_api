# agents/style_imitator_agent.py
from smolagents import CodeAgent, InferenceClientModel # Ensure InferenceClientModel is imported for type hinting
from typing import Dict, Any, Optional, List
import json # For parsing LLM output if it"s JSON
import yaml

class StyleImitatorAgent(CodeAgent):
    """Agent responsible for analyzing and imitating a given writing style."""

    def __init__(self, model: InferenceClientModel, tools: List[Any] = None, system_prompt_path: str = "/home/ubuntu/fixed_agents/style_imitator_prompts.yaml", **kwargs):
        """
        Initializes the StyleImitatorAgent.

        Args:
            model (InferenceClientModel): An instantiated language model client.
            tools (List[Any], optional): List of tools for the agent. Defaults to an empty list.
            system_prompt_path (str): Path to a YAML file containing system prompts.
            **kwargs: Additional arguments for CodeAgent.
        """
        agent_tools = tools if tools is not None else []
        
        self.prompts = {}
        if system_prompt_path:
            try:
                with open(system_prompt_path, "r") as f:
                    self.prompts = yaml.safe_load(f)
            except FileNotFoundError:
                print(f"Warning: Prompt file not found at {system_prompt_path}. Using default prompts or no prompts.")
            except yaml.YAMLError as e:
                print(f"Warning: Error parsing YAML from {system_prompt_path}: {e}. Using default prompts or no prompts.")

        effective_system_prompt = self.prompts.get("default_system_prompt", "You are a helpful AI assistant.")

        super().__init__(
            model=model, 
            tools=agent_tools,
            # system_prompt=effective_system_prompt, # Removed based on BaseBookAgent's comment about TypeError
            **kwargs
        )
        self.system_prompt = effective_system_prompt # Set system_prompt attribute after super init

    def load_prompt_template(self, prompt_key: str) -> str:
        """
        Loads a specific prompt template from the loaded YAML file.

        Args:
            prompt_key (str): The key for the desired prompt in the YAML file.

        Returns:
            str: The prompt template string, or a default message if not found.
        """
        return self.prompts.get(prompt_key, f"Prompt 	{prompt_key}	 not found.")

    def analyze_style(self, example_text: str) -> Dict[str, Any]:
        """
        Analyzes the provided text to identify key stylistic elements.

        Args:
            example_text (str): The text whose style needs to be analyzed.

        Returns:
            Dict[str, Any]: A dictionary describing the style (e.g., tone, sentence structure, vocabulary).
        """
        prompt_template = self.load_prompt_template("analyze_style_prompt")
        formatted_prompt = prompt_template.format(text_to_analyze=example_text)

        print(f"StyleImitatorAgent: Analyzing style of provided text.")
        # response_text = self.run(formatted_prompt)
        
        print(f"StyleImitatorAgent: (Placeholder) LLM would analyze style here. Simulating style analysis.")
        style_analysis = {
            "tone": "humorous and witty",
            "sentence_structure": "mix of short, punchy sentences and longer, descriptive ones",
            "vocabulary": "rich and varied, with occasional colloquialisms",
            "pacing": "fast-paced",
            "other_notes": "Uses rhetorical questions frequently."
        }
        print(f"StyleImitatorAgent: Style analysis complete - {json.dumps(style_analysis, indent=2)}")
        return style_analysis

    def imitate_style(self, text_to_rewrite: str, style_description: Dict[str, Any]) -> str:
        """
        Rewrites the given text to match the described style.

        Args:
            text_to_rewrite (str): The original text to be rewritten.
            style_description (Dict[str, Any]): The style characteristics to imitate (as a dictionary).

        Returns:
            str: The rewritten text in the target style.
        """
        prompt_template = self.load_prompt_template("imitate_style_prompt")
        style_description_str = json.dumps(style_description, indent=2)
        formatted_prompt = prompt_template.format(original_text=text_to_rewrite, style_to_imitate=style_description_str)
        print(f"StyleImitatorAgent: Rewriting text to imitate style: {style_description.get('tone', 'unknown tone')}")
        # rewritten_text = self.run(formatted_prompt)
        print(f"StyleImitatorAgent: (Placeholder) LLM would rewrite text here. Simulating rewrite.")
        rewritten_text = f"(This is a wonderfully {style_description.get('tone', 'stylized')} version of: {text_to_rewrite[:100]}...)"
        print(f"StyleImitatorAgent: Text rewritten.")
        return rewritten_text

