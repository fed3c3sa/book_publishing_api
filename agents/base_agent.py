# agents/base_agent.py
from smolagents import CodeAgent, InferenceClientModel
from typing import List, Dict, Any, Optional
import yaml

class BaseBookAgent(CodeAgent):
    """
    Base class for all agents in the book writing project.
    It extends smolagents.CodeAgent to provide common functionalities
    like loading prompts from YAML files.
    """
    def __init__(self, model: InferenceClientModel, tools: List[callable] = None, system_prompt_path: Optional[str] = None, **kwargs):
        """
        Initializes the BaseBookAgent.

        Args:
            model (InferenceClientModel): An instantiated language model client (e.g., OpenAIChatModel, OllamaChatModel).
            tools (List[callable], optional): A list of tools available to the agent. Defaults to an empty list.
            system_prompt_path (Optional[str]): Path to a YAML file containing system prompts.
                                                If None, a default system prompt is used or no specific system prompt is set.
            **kwargs: Additional arguments to pass to the CodeAgent constructor.
        """
        self.prompts = {}
        if system_prompt_path:
            try:
                with open(system_prompt_path, "r") as f:
                    self.prompts = yaml.safe_load(f)
            except FileNotFoundError:
                print(f"Warning: Prompt file not found at {system_prompt_path}. Using default prompts or no prompts.")
            except yaml.YAMLError as e:
                print(f"Warning: Error parsing YAML from {system_prompt_path}: {e}. Using default prompts or no prompts.")

        # Use a generic system prompt if a specific one isn't loaded or provided by a subclass
        # Subclasses can override this by passing their own system_prompt to super().__init__
        # or by setting self.system_prompt directly after super().__init__ call.
        effective_system_prompt = self.prompts.get("default_system_prompt", "You are a helpful AI assistant.")
        
        # Ensure tools is a list, even if None is passed
        agent_tools = tools if tools is not None else []

        super().__init__(
            model=model, # Pass the model instance directly
            tools=agent_tools,
            # system_prompt=effective_system_prompt, # Removed due to TypeError with smolagents base class
            **kwargs
        )
        # Store the system prompt for potential use by the agent's own methods
        self.system_prompt = effective_system_prompt
    def load_prompt_template(self, prompt_key: str) -> str:
        """
        Loads a specific prompt template from the loaded YAML file.

        Args:
            prompt_key (str): The key for the desired prompt in the YAML file.

        Returns:
            str: The prompt template string, or a default message if not found.
        """
        return self.prompts.get(prompt_key, f"Prompt 	{prompt_key}	 not found.")

