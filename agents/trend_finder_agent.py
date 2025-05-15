# agents/trend_finder_agent.py
from smolagents import CodeAgent, InferenceClientModel # Ensure InferenceClientModel is imported for type hinting
from typing import Dict, Any, List, Optional
import json # For parsing LLM output if it"s JSON
import yaml

class TrendFinderAgent(CodeAgent):
    """Agent responsible for finding trends related to a book topic on Amazon or the web."""

    def __init__(self, model: InferenceClientModel, tools: List[Any] = None, system_prompt_path: str = "/home/ubuntu/fixed_agents/trend_finder_prompts.yaml", **kwargs):
        """
        Initializes the TrendFinderAgent.

        Args:
            model (InferenceClientModel): An instantiated language model client.
            tools (List[Any], optional): List of tools for the agent (e.g., WebSearchTool instance).
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

    def find_trends(self, topic: str, genre: Optional[str] = None) -> Dict[str, Any]:
        """
        Searches for trends related to the given topic and genre using available tools.

        Args:
            topic (str): The main topic of the book.
            genre (Optional[str]): The genre of the book.

        Returns:
            Dict[str, Any]: A dictionary containing trend analysis, popular keywords, etc.
        """
        search_query_amazon = f"top selling books on Amazon about {topic}"
        if genre:
            search_query_amazon += f" in {genre} genre"
        
        search_query_general = f"book trends for {topic}"
        if genre:
            search_query_general += f" {genre}"

        prompt_template = self.load_prompt_template("analyze_search_results_prompt")

        llm_task_prompt = (
            f"Analyze book trends for topic: 	{topic}	 and genre: 	{genre}	. "
            f"First, perform web searches for relevant information, including top-selling books on Amazon and general book trends. "
            f"Use queries like 	{search_query_amazon}	 and 	{search_query_general}	. "
            f"Then, synthesize the findings into a structured JSON report covering popular keywords, common elements in successful books, reader insights, and potential niche areas. "
            f"Use the following structure for your JSON output: {{{{topic}}}}: \"...\", {{{{genre}}}}: \"...\", {{{{popular_keywords}}}}: [], {{{{common_elements}}}}: [], {{{{reader_insights_summary}}}}: \"...\", {{{{potential_niches}}}}: []}}}}"
        )

        print(f"TrendFinderAgent: Starting trend analysis for topic: \\'{topic}\\', genre: \\'{genre}\\'.")
        # response_text = self.run(llm_task_prompt)

        print(f"TrendFinderAgent: (Placeholder) LLM would perform searches and analyze results here. Simulating trend analysis.")
        trend_analysis = {
            "topic": topic,
            "genre": genre,
            "popular_keywords": ["magical creatures", "friendship story", "childrens adventure"],
            "common_elements": ["brave protagonist", "talking animals", "hidden world"],
            "reader_insights_summary": "Readers love heartwarming stories with beautiful illustrations and a positive message.",
            "potential_niches": ["books about kindness for early readers", "interactive forest adventure books"]
        }
        print(f"TrendFinderAgent: Trend analysis complete - {json.dumps(trend_analysis, indent=2)}")
        return trend_analysis

