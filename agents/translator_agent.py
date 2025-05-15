# agents/translator_agent.py
from smolagents import CodeAgent, InferenceClientModel # Ensure InferenceClientModel is imported for type hinting
from typing import Dict, Any, Optional, List
import json # For parsing LLM output if it"s JSON
import yaml

class TranslatorAgent(CodeAgent):
    """Agent responsible for translating text into a specified language."""

    def __init__(self, model: InferenceClientModel, tools: List[Any] = None, system_prompt_path: str = "/home/ubuntu/fixed_agents/translator_prompts.yaml", **kwargs):
        """
        Initializes the TranslatorAgent.

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

    def translate_text(self, text_to_translate: str, target_language: str, source_language: str = "English") -> str:
        """
        Translates the given text to the target language using the agent"s LLM.

        Args:
            text_to_translate (str): The text to be translated.
            target_language (str): The language to translate the text into (e.g., "French", "Spanish").
            source_language (str): The source language of the text (e.g., "English").

        Returns:
            str: The translated text.
        """
        prompt_template = self.load_prompt_template("translate_text_prompt")
        
        formatted_prompt = prompt_template.format(
            source_language=source_language, 
            target_language=target_language, 
            text=text_to_translate
        )

        print(f"TranslatorAgent: Translating text from {source_language} to {target_language}.")
        # translated_text = self.run(formatted_prompt)
        
        print(f"TranslatorAgent: (Placeholder) LLM would translate text here. Simulating translation.")
        translated_text = f"(Ceci est une version traduite en {target_language} de: {text_to_translate[:100]}...)"
        
        print(f"TranslatorAgent: Text translation complete.")
        return translated_text

