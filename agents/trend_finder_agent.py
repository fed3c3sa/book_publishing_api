# agents/trend_finder_agent.py
from .base_agent import BaseBookAgent
from smolagents import InferenceClientModel # Ensure InferenceClientModel is imported for type hinting
from typing import Dict, Any, List, Optional
import json # For parsing LLM output if it"s JSON

class TrendFinderAgent(BaseBookAgent):
    """Agent responsible for finding trends related to a book topic on Amazon or the web."""

    def __init__(self, model: InferenceClientModel, tools: List[Any] = None, **kwargs):
        """
        Initializes the TrendFinderAgent.

        Args:
            model (InferenceClientModel): An instantiated language model client.
            tools (List[Any], optional): List of tools for the agent (e.g., WebSearchTool instance).
            **kwargs: Additional arguments for CodeAgent.
        """
        agent_tools = tools if tools is not None else []
        super().__init__(
            model=model, # Pass the model instance directly
            tools=agent_tools,
            system_prompt_path="/home/federico/Desktop/personal/book_publishing_api/prompts/trend_finder_prompts.yaml",
            **kwargs
        )

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

        # The agent will use its LLM to generate code that calls the WebSearchTool.
        # The prompt should guide the LLM to perform searches and analyze results.
        prompt_template = self.load_prompt_template("analyze_search_results_prompt")

        llm_task_prompt = (
            f"Analyze book trends for topic: '{topic}' and genre: '{genre}'. "
            f"First, perform web searches for relevant information, including top-selling books on Amazon and general book trends. "
            f"Use queries like '{search_query_amazon}' and '{search_query_general}'. "
            f"Then, synthesize the findings into a structured JSON report covering popular keywords, common elements in successful books, reader insights, and potential niche areas. "
            f"Use the following structure for your JSON output: {{{{topic}}}}: \"...\", {{{{genre}}}}: \"...\", {{{{popular_keywords}}}}: [], {{{{common_elements}}}}: [], {{{{reader_insights_summary}}}}: \"...\", {{{{potential_niches}}}}: []}}}}"
        )

        print(f"TrendFinderAgent: Starting trend analysis for topic: \'{topic}\', genre: \'{genre}\'.")
        # response_text = self.execute(llm_task_prompt) # This would involve LLM calling search tools

        # Placeholder implementation - replace with actual LLM interaction and parsing
        print(f"TrendFinderAgent: (Placeholder) LLM would perform searches and analyze results here. Simulating trend analysis.")
        # try:
        #     trend_analysis = json.loads(response_text)
        # except json.JSONDecodeError:
        #     print(f"TrendFinderAgent: Could not parse LLM response as JSON. Using fallback data.")
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

