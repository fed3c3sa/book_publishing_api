# tools/pdf_generator_tool.py
# This tool is largely conceptual for this project as the ImpaginatorAgent uses ReportLab directly.
# If PDF generation were a more complex, LLM-driven task, this tool might be used by an agent.

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import letter
import os

def generate_pdf_from_structured_content(
    output_pdf_path: str,
    title: str,
    chapters_data: list, # List of dicts, e.g., [{"title": "Ch1", "text_markdown": "...", "images": [{"path": "img1.png", "caption": "..."}]}]
    pdf_config: dict
) -> str:
    """
    Generates a PDF from structured content using ReportLab.
    This is a simplified version of what the ImpaginatorAgent does directly.

    Args:
        output_pdf_path (str): The full path to save the generated PDF.
        title (str): The title of the book.
        chapters_data (list): A list of chapter data, where each chapter is a dictionary
                              containing at least "title" and "text_markdown".
                              It can optionally contain "images" as a list of image paths or objects.
        pdf_config (dict): Configuration for PDF styling (margins, fonts, image sizes).

    Returns:
        str: Path to the generated PDF or an error message.
    """
    doc = SimpleDocTemplate(output_pdf_path, pagesize=letter,
                            rightMargin=pdf_config.get("margin_cm", 2.54)*cm,
                            leftMargin=pdf_config.get("margin_cm", 2.54)*cm,
                            topMargin=pdf_config.get("margin_cm", 2.54)*cm,
                            bottomMargin=pdf_config.get("margin_cm", 2.54)*cm)
    styles = getSampleStyleSheet()
    story_elements = []

    # Title Page
    story_elements.append(Paragraph(title, styles["h1"]))
    story_elements.append(PageBreak())

    for chapter in chapters_data:
        story_elements.append(Paragraph(chapter.get("title", "Untitled Chapter"), styles["h2"]))
        story_elements.append(Spacer(1, 0.2*inch))
        
        # Basic handling of markdown (ReportLab doesn't directly support full Markdown)
        # For simplicity, splitting by newlines to create paragraphs.
        # A more robust solution would use a Markdown to ReportLab Platypus converter.
        text_paragraphs = chapter.get("text_markdown", "").split("\n\n")
        for para_text in text_paragraphs:
            if para_text.strip():
                story_elements.append(Paragraph(para_text.strip(), styles["Normal"]))
                story_elements.append(Spacer(1, 0.1*inch))
        
        # Placeholder for image handling if chapter_data included image paths
        # for img_info in chapter.get("images", []):
        #     if os.path.exists(img_info.get("path")):
        #         try:
        #             img = Image(img_info.get("path"), width=pdf_config.get("body_image_width_inch", 4)*inch)
        #             img.hAlign = "CENTER"
        #             story_elements.append(img)
        #             story_elements.append(Spacer(1, 0.2*inch))
        #         except Exception as e:
        #             print(f"PDFTool: Error adding image {img_info.get(	path	)}: {e}")

        story_elements.append(PageBreak())

    try:
        doc.build(story_elements)
        return f"Successfully generated PDF: {output_pdf_path}"
    except Exception as e:
        return f"Error building PDF with tool: {e}"

if __name__ == "__main__":
    # Example Usage (for testing the tool directly)
    sample_pdf_config = {
        "margin_cm": 2.0,
        "body_image_width_inch": 4.5
    }
    sample_chapters = [
        {"title": "Chapter 1: The Beginning", "text_markdown": "This is the first paragraph.\n\nThis is the second paragraph with more text."},
        {"title": "Chapter 2: The Middle", "text_markdown": "Content for the second chapter.\n\nIt was very exciting."}
    ]
    if not os.path.exists("/home/ubuntu/book_writing_agent/outputs/tool_test"):
        os.makedirs("/home/ubuntu/book_writing_agent/outputs/tool_test")

    result = generate_pdf_from_structured_content(
        output_pdf_path="/home/ubuntu/book_writing_agent/outputs/tool_test/sample_tool_book.pdf",
        title="My Sample Book via Tool",
        chapters_data=sample_chapters,
        pdf_config=sample_pdf_config
    )
    print(result)

