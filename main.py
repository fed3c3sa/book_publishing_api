# main.py
import yaml
import os
import shutil
from datetime import datetime
import uuid

# Assuming smolagents and necessary models are installed and configured
# For actual LLM interaction, you would need an API key for OpenAI or a running Ollama instance.
# from smolagents.models.ollama import OllamaChatModel
# from smolagents.models.openai import OpenAIServerModel
from smolagents import InferenceClientModel # Generic model placeholder
from smolagents import OpenAIServerModel

from agents import (
    IdeatorAgent,
    StoryWriterAgent,
    ImageCreatorAgent,
    ImpaginatorAgent,
    TrendFinderAgent,
    StyleImitatorAgent,
    TranslatorAgent
)
from data_models.book_plan import BookPlan
from data_models.story_content import StoryContent
from data_models.generated_image import GeneratedImage

# Placeholder for a generic model client if specific ones aren't set up
# This would need to be replaced with a concrete implementation like OpenAIServerModel or OllamaChatModel
class OpenAIServerModel(InferenceClientModel):
    def __init__(self, model_name="placeholder_model", **kwargs):
        super().__init__(model_name=model_name, **kwargs)
        self.model_name = model_name # Ensure model_name is set as an instance attribute
        print(f"Initialized OpenAIServerModel: {model_name}")

    def complete(self, prompt: str, **kwargs) -> str:
        print(f"OpenAIServerModel received prompt (first 100 chars): {prompt[:100]}...")
        # Simulate a generic response structure if needed by agents
        if "JSON object" in prompt or "JSON report" in prompt:
            return "{\"simulated_response\": \"This is a placeholder JSON response from the LLM.\"}"
        return f"This is a placeholder LLM response to: {prompt[:50]}..."

    async def acomplete(self, prompt: str, **kwargs) -> str:
        # Placeholder for async completion if needed by smolagents base classes
        print(f"OpenAIServerModel (async) received prompt (first 100 chars): {prompt[:100]}...")
        if "JSON object" in prompt or "JSON report" in prompt:
            return "{\"simulated_response\": \"This is an async placeholder JSON response from the LLM.\"}"
        return f"This is an async placeholder LLM response to: {prompt[:50]}..."


def load_config(config_path="config.yaml") -> dict:
    """Loads the main configuration file."""
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        print(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file {config_path} not found. Exiting.")
        exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing configuration file {config_path}: {e}. Exiting.")
        exit(1)

def main_workflow(config: dict, user_book_idea: str):
    """Orchestrates the main book creation workflow."""
    project_base_output_dir = config.get("output_directory", "/home/federico/Desktop/personal/book_publishing_api/outputs")
    # Create a unique project ID for this run
    project_id = f"book_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    current_project_output_dir = os.path.join(project_base_output_dir, project_id)
    os.makedirs(current_project_output_dir, exist_ok=True)
    print(f"Project output directory: {current_project_output_dir}")

    # --- Initialize LLM Model (Placeholder) ---
    # Replace with actual model initialization, e.g.:
    # llm_model = OpenAIServerModel(api_key=config["openai_api_key"], model_name="gpt-3.5-turbo")
    # llm_model = OllamaChatModel(model_name="llama2")
    openai_api_key = "openai-api-key"
    try:
        llm_model = OpenAIServerModel(
        api_key=openai_api_key,
        model_name=config.get("openai_llm_model", "gpt-4o") # Usa gpt-4o o un altro modello desiderato
        )
        print(f"Using LLM Model: {llm_model.model_name}")
    except Exception as e:
        print(f"Errore durante l'inizializzazione di OpenAIServerModel: {e}")
        return None, f"Errore inizializzazione LLM: {e}"
        print(f"Using LLM Model: {llm_model.model_name}")

    # --- Initialize Tools (Conceptual for now, agents might use them internally) ---
    # web_search_tool = WebSearchTool() # If using smolagents built-in
    # image_gen_tool = ImageGenerationToolWrapper() # If you have a custom tool wrapper
    # pdf_tool = PDFToolWrapper()
    # text_analysis_tool = TextAnalysisToolWrapper()
    # translation_tool = TranslationToolWrapper()

    # --- Initialize Agents ---
    print("\n--- Initializing Agents ---")
    ideator = IdeatorAgent(model=llm_model)
    story_writer = StoryWriterAgent(model=llm_model)
    image_creator = ImageCreatorAgent(model=llm_model, project_id=project_id, output_dir=project_base_output_dir)
    impaginator = ImpaginatorAgent(model=llm_model, project_id=project_id, output_dir=project_base_output_dir, pdf_config=config.get("pdf_layout", {}))
    
    # Optional Agents (can be initialized based on config or user request)
    trend_finder = None
    if config.get("enable_trend_finder", False):
        # trend_finder_tools = [web_search_tool] # Pass necessary tools
        trend_finder = TrendFinderAgent(model=llm_model, tools=[]) # tools=[] for placeholder
        print("TrendFinderAgent enabled.")

    style_imitator = None
    if config.get("enable_style_imitator", False):
        # style_imitator_tools = [text_analysis_tool] # Pass necessary tools
        style_imitator = StyleImitatorAgent(model=llm_model, tools=[])
        print("StyleImitatorAgent enabled.")

    translator = None
    if config.get("enable_translator", False):
        # translator_tools = [translation_tool]
        translator = TranslatorAgent(model=llm_model, tools=[])
        print("TranslatorAgent enabled.")

    # --- Workflow Execution ---
    print("\n--- Starting Book Creation Workflow ---")

    # 1. Trend Finding (Optional)
    trend_analysis_results = None
    if trend_finder:
        print("\nStep 1: Finding Trends...")
        topic_for_trends = config.get("trend_finder_topic", "childrens books about dragons")
        genre_for_trends = config.get("trend_finder_genre", "fantasy")
        trend_analysis_results = trend_finder.find_trends(topic=topic_for_trends, genre=genre_for_trends)
        print(f"Trend Analysis Results: {trend_analysis_results}")

    # 2. Idea Generation
    print("\nStep 2: Generating Book Plan...")
    book_plan: BookPlan = ideator.generate_initial_idea(user_prompt=user_book_idea, trend_analysis=trend_analysis_results)
    if not book_plan or not book_plan.chapters:
        print("Error: Failed to generate a valid book plan. Exiting.")
        return
    print(f"Book Plan Generated: 	{book_plan.title}	 with {len(book_plan.chapters)} chapters.")
    # Save book plan
    with open(os.path.join(current_project_output_dir, "book_plan.yaml"), "w") as f:
        yaml.dump(book_plan.__dict__, f, indent=2, default_flow_style=False, allow_unicode=True)

    # 3. Story Writing
    print("\nStep 3: Writing Story Content...")
    example_style_text = None
    if style_imitator and config.get("style_imitation_example_text"): # If style imitation is enabled and example provided
        print("Analyzing style of example text...")
        style_desc = style_imitator.analyze_style(config["style_imitation_example_text"])
        # The StoryWriterAgent would need to be adapted to use this style_desc, or the LLM prompt for StoryWriter updated.
        # For now, we might just pass the raw example text if the StoryWriter prompt supports it.
        example_style_text = config["style_imitation_example_text"]
        print("Style analysis complete. Will attempt to use for story writing.")

    story_content: StoryContent = story_writer.write_story(book_plan, style_example=example_style_text)
    if not story_content or not story_content.chapters_content:
        print("Error: Failed to generate story content. Exiting.")
        return
    print(f"Story Content Generated for 	{story_content.book_plan.title}	.")
    # Save story content (e.g., as JSON or individual chapter files)
    # For simplicity, let's just log it for now or save a summary
    with open(os.path.join(current_project_output_dir, "story_summary.txt"), "w") as f:
        f.write(f"Title: {story_content.book_plan.title}\n")
        for i, chap_content in enumerate(story_content.chapters_content):
            f.write(f"\nChapter {i+1}: {chap_content.title}\n")
            f.write(f"{chap_content.text_markdown[:200]}...\n") # Write a snippet
            f.write(f"Image Placeholders: {len(chap_content.image_placeholders)}\n")

    # 4. Image Creation
    print("\nStep 4: Generating Images...")
    generated_images: List[GeneratedImage] = image_creator.create_images(story_content, book_plan)
    print(f"Image Generation Complete. {len(generated_images)} images processed.")
    # Log generated image paths
    with open(os.path.join(current_project_output_dir, "image_log.txt"), "w") as f:
        for img in generated_images:
            f.write(f"Placeholder ID: {img.placeholder_id}, Path: {img.image_path}, Error: {img.error_message}\n")

    # 5. PDF Impagination
    print("\nStep 5: Creating Book PDF...")
    cover_image_obj = next((img for img in generated_images if img.placeholder_id == "cover" and img.image_path and not img.error_message), None)
    cover_path = cover_image_obj.image_path if cover_image_obj else None
    
    pdf_output_path = impaginator.create_book_pdf(story_content, generated_images, cover_image_path=cover_path)
    print(f"PDF Creation Result: {pdf_output_path}")

    # 6. Translation (Optional)
    if translator and config.get("translation_target_language"): 
        print("\nStep 6: Translating Book (Conceptual - translating title and chapter titles)...")
        target_lang = config["translation_target_language"]
        translated_title = translator.translate_text(book_plan.title, target_lang)
        print(f"Original Title: {book_plan.title} -> Translated Title ({target_lang}): {translated_title}")
        # In a full implementation, you would iterate through all text content.
        # For now, just a conceptual step.
        with open(os.path.join(current_project_output_dir, f"translation_summary_{target_lang}.txt"), "w") as f:
            f.write(f"Original Title: {book_plan.title}\nTranslated Title ({target_lang}): {translated_title}\n")
            for i, chap_outline in enumerate(book_plan.chapters):
                trans_chap_title = translator.translate_text(chap_outline.title, target_lang)
                f.write(f"Ch {i+1} Original: {chap_outline.title} -> Translated: {trans_chap_title}\n")

    print("\n--- Book Creation Workflow Completed ---")
    print(f"All outputs saved in project directory: {current_project_output_dir}")
    print(f"Final PDF (if successful): {pdf_output_path}")
    return current_project_output_dir, pdf_output_path

if __name__ == "__main__":
    cfg = load_config()
    initial_user_idea = cfg.get("default_user_book_idea", "A children's book about a curious squirrel who explores a magical garden.")
    
    # Clean up previous outputs if they exist to avoid clutter during testing
    # output_dir_to_clean = cfg.get("output_directory", "/home/federico/Desktop/personal/book_publishing_api/outputs")
    # if os.path.exists(output_dir_to_clean):
    #     print(f"Cleaning up previous output directory: {output_dir_to_clean}")
    #     # Be careful with shutil.rmtree!
    #     # for item in os.listdir(output_dir_to_clean):
    #     #     item_path = os.path.join(output_dir_to_clean, item)
    #     #     if os.path.isdir(item_path) and item.startswith("book_"):
    #     #         shutil.rmtree(item_path)
    #     # print("Cleanup complete.")

    main_workflow(config=cfg, user_book_idea=initial_user_idea)

