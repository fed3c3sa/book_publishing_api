# agents/translator_agent.py
from .base_agent import BaseBookAgent
from smolagents import InferenceClientModel # Ensure InferenceClientModel is imported for type hinting
from typing import Dict, Any, Optional, List
import json # For parsing LLM output if it"s JSON

class TranslatorAgent(BaseBookAgent):
    """Agent responsible for translating text into a specified language."""

    def __init__(self, model: InferenceClientModel, tools: List[Any] = None, **kwargs):
        """
        Initializes the TranslatorAgent.

        Args:
            model (InferenceClientModel): An instantiated language model client.
            tools (List[Any], optional): List of tools for the agent. Defaults to an empty list.
            **kwargs: Additional arguments for CodeAgent.
        """
        agent_tools = tools if tools is not None else []
        super().__init__(
            model=model, # Pass the model instance directly
            tools=agent_tools,
            system_prompt_path="/home/ubuntu/book_writing_agent/prompts/translator_prompts.yaml",
            **kwargs
        )

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
        # translated_text = self.execute(formatted_prompt)
        
        # Placeholder implementation - replace with actual LLM interaction
        # The LLM, given the prompt, should directly return the translated text.
        print(f"TranslatorAgent: (Placeholder) LLM would translate text here. Simulating translation.")
        translated_text = f"(Ceci est une version traduite en {target_language} de: {text_to_translate[:100]}...)"
        
        print(f"TranslatorAgent: Text translation complete.")
        return translated_text

