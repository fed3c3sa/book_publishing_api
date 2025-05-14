# agents/impaginator_agent.py
from .base_agent import BaseBookAgent
from smolagents import InferenceClientModel # Ensure InferenceClientModel is imported for type hinting
from typing import List, Dict, Any, Optional
from data_models.story_content import StoryContent
from data_models.generated_image import GeneratedImage
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import letter
import os
import yaml
import re

class ImpaginatorAgent(BaseBookAgent):
    """Agent responsible for taking text and images and producing a formatted PDF book."""

    def __init__(self, model: InferenceClientModel, project_id: str, output_dir: str, pdf_config: Dict[str, Any], tools: List[Any] = None, **kwargs):
        """
        Initializes the ImpaginatorAgent.

        Args:
            model (InferenceClientModel): An instantiated language model client.
            project_id (str): The unique identifier for the current book project.
            output_dir (str): The base directory where the final PDF will be saved.
            pdf_config (Dict[str, Any]): Configuration for PDF generation (fonts, margins, etc.).
            tools (List[Any], optional): List of tools for the agent. Defaults to an empty list.
            **kwargs: Additional arguments for CodeAgent.
        """
        agent_tools = tools if tools is not None else []
        super().__init__(
            model=model, # Pass the model instance directly
            tools=agent_tools,
            system_prompt_path="/home/ubuntu/book_writing_agent/prompts/impaginator_prompts.yaml",
            **kwargs
        )
        self.project_id = project_id
        self.project_output_dir = os.path.join(output_dir, project_id)
        os.makedirs(self.project_output_dir, exist_ok=True)
        self.pdf_config = pdf_config

    def create_book_pdf(self, story_content: StoryContent, generated_images: List[GeneratedImage], cover_image_path: Optional[str] = None) -> str:
        """
        Creates the book PDF from story content and images.

        Args:
            story_content (StoryContent): The textual content of the book, including image placeholders.
            generated_images (List[GeneratedImage]): A list of generated image objects with their paths.
            cover_image_path (Optional[str]): Path to the cover image. If None, no cover page is added.

        Returns:
            str: The path to the generated PDF file or an error message.
        """
        pdf_filename = os.path.join(self.project_output_dir, f"{story_content.book_plan.title.replace(' ', '_').lower()}_book.pdf")
        doc = SimpleDocTemplate(pdf_filename, pagesize=letter,
                                rightMargin=self.pdf_config.get("margin_cm", 2.54)*cm,
                                leftMargin=self.pdf_config.get("margin_cm", 2.54)*cm,
                                topMargin=self.pdf_config.get("margin_cm", 2.54)*cm,
                                bottomMargin=self.pdf_config.get("margin_cm", 2.54)*cm)
        styles = getSampleStyleSheet()
        story_elements = []

        # Title Page
        story_elements.append(Paragraph(story_content.book_plan.title, styles["h1"]))
        story_elements.append(Spacer(1, 0.5*inch))
        if cover_image_path and os.path.exists(cover_image_path):
            try:
                img = Image(cover_image_path, width=self.pdf_config.get("cover_image_width_inch", 4)*inch, height=self.pdf_config.get("cover_image_height_inch", 6)*inch)
                story_elements.append(img)
            except Exception as e:
                print(f"ImpaginatorAgent: Error adding cover image {cover_image_path}: {e}")
        story_elements.append(PageBreak())

        # Body Content
        image_map = {img.placeholder_id: img.image_path for img in generated_images if img.image_path and os.path.exists(img.image_path)}

        for chapter in story_content.chapters_content:
            story_elements.append(Paragraph(chapter.title, styles["h2"]))
            story_elements.append(Spacer(1, 0.2*inch))
            
            paragraphs = chapter.text_markdown.split("\n\n") # Split by double newline for paragraphs
            for para_text in paragraphs:
                if not para_text.strip():
                    continue
                
                # Handle image placeholders within or between paragraphs
                parts = re.split(r'(\[IMAGE: .*?\])', para_text) # Split by [IMAGE: id] pattern, keeping delimiter
                for part in parts:
                    if not part.strip():
                        continue
                    img_match = re.fullmatch(r'\[IMAGE: (.*?)\]', part.strip()) # Match only if the part is an image placeholder
                    if img_match:
                        placeholder_id = img_match.group(1).strip()
                        if placeholder_id in image_map:
                            try:
                                img_path = image_map[placeholder_id]
                                img = Image(img_path, width=self.pdf_config.get("body_image_width_inch", 4)*inch) # Adjust width as needed
                                img.hAlign = 'CENTER'
                                story_elements.append(img)
                                story_elements.append(Spacer(1, 0.2*inch))
                            except Exception as e:
                                print(f"ImpaginatorAgent: Error adding image {img_path} for placeholder {placeholder_id}: {e}")
                                story_elements.append(Paragraph(f"[Image: {placeholder_id} - Error loading]", styles["Italic"]))
                        else:
                            story_elements.append(Paragraph(f"[Image: {placeholder_id} - Path not found or invalid]", styles["Italic"]))
                    else:
                        # This is a text part
                        story_elements.append(Paragraph(part, styles["Normal"]))
                story_elements.append(Spacer(1, 0.1*inch)) # Spacer after each original paragraph block
            story_elements.append(PageBreak())

        try:
            doc.build(story_elements)
            print(f"ImpaginatorAgent: Successfully generated PDF: {pdf_filename}")
            return pdf_filename
        except Exception as e:
            print(f"ImpaginatorAgent: Error building PDF: {e}")
            return f"Error building PDF: {e}"

