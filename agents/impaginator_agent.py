# agents/impaginator_agent.py
from .base_agent import BaseBookAgent
from smolagents import InferenceClientModel # Ensure InferenceClientModel is imported for type hinting
from typing import List, Dict, Any, Optional
from data_models.story_content import StoryContent
from data_models.generated_image import GeneratedImage
import os
import yaml
import re
import weasyprint
from jinja2 import Environment, FileSystemLoader, select_autoescape

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
            system_prompt_path="/home/federico/Desktop/personal/book_publishing_api/prompts/impaginator_prompts.yaml",
            **kwargs
        )
        self.project_id = project_id
        self.project_output_dir = os.path.join(output_dir, project_id)
        os.makedirs(self.project_output_dir, exist_ok=True)
        self.pdf_config = pdf_config
        
        # Create templates directory if it doesn't exist
        self.templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Initialize Jinja2 environment for HTML templates
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def create_book_pdf(self, story_content: StoryContent, generated_images: List[GeneratedImage], cover_image_path: Optional[str] = None) -> str:
        """
        Creates the book PDF from story content and images using HTML/CSS and WeasyPrint.

        Args:
            story_content (StoryContent): The textual content of the book, including image placeholders.
            generated_images (List[GeneratedImage]): A list of generated image objects with their paths.
            cover_image_path (Optional[str]): Path to the cover image. If None, no cover page is added.

        Returns:
            str: The path to the generated PDF file or an error message.
        """
        try:
            # Create HTML output directory
            html_dir = os.path.join(self.project_output_dir, "html")
            os.makedirs(html_dir, exist_ok=True)
            
            # Create images directory for the HTML
            images_dir = os.path.join(html_dir, "images")
            os.makedirs(images_dir, exist_ok=True)
            
            # Copy images to the HTML directory
            import shutil
            image_map = {}
            for img in generated_images:
                if img.image_path and os.path.exists(img.image_path):
                    img_filename = os.path.basename(img.image_path)
                    dest_path = os.path.join(images_dir, img_filename)
                    shutil.copy2(img.image_path, dest_path)
                    image_map[img.placeholder_id] = os.path.join("images", img_filename)
            
            # Copy cover image if it exists
            html_cover_path = None
            if cover_image_path and os.path.exists(cover_image_path):
                cover_filename = os.path.basename(cover_image_path)
                dest_cover_path = os.path.join(images_dir, cover_filename)
                shutil.copy2(cover_image_path, dest_cover_path)
                html_cover_path = os.path.join("images", cover_filename)
            
            # Prepare data for the template
            book_data = {
                "title": story_content.book_plan.title,
                "cover_image_path": html_cover_path,
                "chapters": [],
                "page_size": self.pdf_config.get("page_size", "letter"),
                "margin": self.pdf_config.get("margin_cm", 2.54),
                "font_family": self.pdf_config.get("font_family", "'Noto Sans', 'Noto Sans CJK SC', sans-serif"),
                "font_size": self.pdf_config.get("font_size", 12),
                "title_font_size": self.pdf_config.get("title_font_size", 24),
                "chapter_title_font_size": self.pdf_config.get("chapter_title_font_size", 20),
                "text_color": self.pdf_config.get("text_color", "#333333"),
                "background_color": self.pdf_config.get("background_color", "#ffffff"),
                "title_color": self.pdf_config.get("title_color", "#000000"),
                "chapter_title_color": self.pdf_config.get("chapter_title_color", "#333333"),
                "show_page_numbers": self.pdf_config.get("show_page_numbers", True),
                "border_width": self.pdf_config.get("border_width", 2),
                "border_style": self.pdf_config.get("border_style", "solid"),
                "border_color": self.pdf_config.get("border_color", "#dddddd"),
                "border_radius": self.pdf_config.get("border_radius", 5),
                "theme": self.pdf_config.get("theme", "children")
            }
            
            # Process chapters
            for chapter in story_content.chapters_content:
                chapter_data = {
                    "title": chapter.title,
                    "content_blocks": []
                }
                
                # Split text by paragraphs and image placeholders
                paragraphs = chapter.text_markdown.split("\n\n")
                for para_idx, para_text in enumerate(paragraphs):
                    if not para_text.strip():
                        continue
                    
                    # Check if paragraph contains image placeholder
                    img_match = re.search(r'\[IMAGE: (.*?)\]', para_text)
                    if img_match:
                        placeholder_id = img_match.group(1).strip()
                        
                        # If image is in the middle of text, split and create text-with-image block
                        if placeholder_id in image_map:
                            parts = re.split(r'\[IMAGE: .*?\]', para_text)
                            if len(parts) > 1 and (parts[0].strip() and parts[1].strip()):
                                # Text with wrapped image
                                image_position = "right" if para_idx % 2 == 0 else "left"
                                chapter_data["content_blocks"].append({
                                    "type": "text_with_image",
                                    "text_content": " ".join(parts).strip(),
                                    "image_path": image_map[placeholder_id],
                                    "image_alt_text": f"{chapter.title}",
                                    "image_position": image_position
                                })
                            else:
                                # Text followed by image
                                for part in parts:
                                    if part.strip():
                                        chapter_data["content_blocks"].append({
                                            "type": "text",
                                            "content": part.strip(),
                                            "decorative_border": para_idx % 5 == 0  # Add decorative border to some paragraphs
                                        })
                                
                                # Add image after text
                                chapter_data["content_blocks"].append({
                                    "type": "image",
                                    "path": image_map[placeholder_id],
                                    "alt_text": f"{chapter.title}",
                                    "caption": f"{chapter.title}"
                                })
                        else:
                            # Just add text without image
                            chapter_data["content_blocks"].append({
                                "type": "text",
                                "content": re.sub(r'\[IMAGE: .*?\]', '', para_text).strip(),
                                "decorative_border": para_idx % 5 == 0
                            })
                    else:
                        # Regular paragraph without image
                        chapter_data["content_blocks"].append({
                            "type": "text",
                            "content": para_text.strip(),
                            "decorative_border": para_idx % 5 == 0
                        })
                
                book_data["chapters"].append(chapter_data)
            
            # Render HTML template
            template = self.jinja_env.get_template("book.html")
            html_content = template.render(**book_data)
            
            # Save HTML file
            html_filename = f"{story_content.book_plan.title.replace(' ', '_').lower()}_book.html"
            html_path = os.path.join(html_dir, html_filename)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            # Generate PDF from HTML using WeasyPrint
            pdf_filename = f"{story_content.book_plan.title.replace(' ', '_').lower()}_book.pdf"
            pdf_path = os.path.join(self.project_output_dir, pdf_filename)
            
            # Create WeasyPrint HTML object with base URL to resolve relative paths
            html = weasyprint.HTML(filename=html_path, base_url=html_dir)
            html.write_pdf(pdf_path)
            
            print(f"ImpaginatorAgent: Successfully generated PDF: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            error_message = f"ImpaginatorAgent: Error building PDF: {e}"
            print(error_message)
            return error_message
