"""
PDF generation service implementation.

This service handles creating PDFs from book plans, images, and text data
using ReportLab for PDF creation.
"""

import uuid
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from PIL import Image

from ..interfaces.pdf_generation_interface import PDFGenerationInterface
from ..domain.models import BookPlan, TextData
from ..exceptions import PDFGenerationError
from ..utils.config import BOOKS_DIR, get_output_path


class PDFGenerationService(PDFGenerationInterface):
    """
    PDF generation service implementation.
    
    This service creates PDFs from book data using ReportLab.
    """
    
    def __init__(self):
        """Initialize the PDF generation service."""
        pass
    
    def create_book_pdf(
        self,
        book_plan: BookPlan,
        page_images: Dict[int, str],
        page_texts: Dict[int, TextData],
        output_filename: Optional[str] = None
    ) -> str:
        """
        Create a complete PDF book.
        
        Args:
            book_plan: Complete book plan
            page_images: Dictionary mapping page numbers to image file paths
            page_texts: Dictionary mapping page numbers to TextData models
            output_filename: Optional custom filename for the PDF
            
        Returns:
            Path to the generated PDF file
            
        Raises:
            PDFGenerationError: If PDF generation fails
        """
        try:
            # Generate output filename if not provided
            if not output_filename:
                book_id = str(uuid.uuid4())
                output_filename = f"book_{book_id}.pdf"
            
            # Ensure output directory exists
            output_path = get_output_path() / output_filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create PDF
            c = canvas.Canvas(str(output_path), pagesize=letter)
            width, height = letter
            
            # Get sorted page numbers (including cover which is page 0)
            all_pages = sorted(set(list(page_images.keys()) + list(page_texts.keys())))
            
            for page_num in all_pages:
                # Add image if available
                if page_num in page_images and Path(page_images[page_num]).exists():
                    try:
                        # Load and resize image to fit page
                        img_path = page_images[page_num]
                        img = Image.open(img_path)
                        
                        # Calculate dimensions to fit page while maintaining aspect ratio
                        img_width, img_height = img.size
                        aspect_ratio = img_width / img_height
                        
                        # Use most of the page, leaving margins
                        max_width = width - (2 * inch)
                        max_height = height - (2 * inch)
                        
                        if aspect_ratio > 1:  # Wide image
                            draw_width = max_width
                            draw_height = draw_width / aspect_ratio
                        else:  # Tall image
                            draw_height = max_height
                            draw_width = draw_height * aspect_ratio
                        
                        # Center the image
                        x_pos = (width - draw_width) / 2
                        y_pos = (height - draw_height) / 2
                        
                        c.drawImage(img_path, x_pos, y_pos, width=draw_width, height=draw_height)
                        
                    except Exception as e:
                        print(f"Warning: Could not add image for page {page_num}: {e}")
                
                # Add text if available
                if page_num in page_texts:
                    try:
                        text_data = page_texts[page_num]
                        if isinstance(text_data, TextData):
                            text_content = text_data.main_text
                        else:
                            # Handle dict format
                            text_content = text_data.get('main_text', text_data.get('text', ''))
                        
                        if text_content:
                            # Add text at bottom of page
                            c.setFont("Helvetica", 14)
                            text_y = 1 * inch
                            
                            # Word wrap text to fit page width
                            max_text_width = width - (2 * inch)
                            words = text_content.split()
                            lines = []
                            current_line = []
                            
                            for word in words:
                                test_line = ' '.join(current_line + [word])
                                if c.stringWidth(test_line) <= max_text_width:
                                    current_line.append(word)
                                else:
                                    if current_line:
                                        lines.append(' '.join(current_line))
                                        current_line = [word]
                                    else:
                                        lines.append(word)  # Single word too long
                            
                            if current_line:
                                lines.append(' '.join(current_line))
                            
                            # Draw text lines
                            for line in lines:
                                c.drawString(1 * inch, text_y, line)
                                text_y -= 20  # Move to next line
                                
                    except Exception as e:
                        print(f"Warning: Could not add text for page {page_num}: {e}")
                
                # Start new page (except for last page)
                if page_num != all_pages[-1]:
                    c.showPage()
            
            # Save the PDF
            c.save()
            
            return str(output_path)
            
        except Exception as e:
            raise PDFGenerationError(
                f"PDF generation failed: {str(e)}",
                book_title=book_plan.book_title if book_plan else None
            )
    
    def create_html_version(
        self,
        book_plan: BookPlan,
        page_images: Dict[int, str],
        page_texts: Dict[int, TextData],
        output_filename: Optional[str] = None
    ) -> str:
        """
        Create an HTML version of the book.
        
        Args:
            book_plan: Complete book plan
            page_images: Dictionary mapping page numbers to image file paths
            page_texts: Dictionary mapping page numbers to TextData models
            output_filename: Optional custom filename for the HTML
            
        Returns:
            Path to the generated HTML file
            
        Raises:
            PDFGenerationError: If HTML generation fails
        """
        try:
            # Generate output filename if not provided
            if not output_filename:
                book_id = str(uuid.uuid4())
                output_filename = f"book_{book_id}.html"
            
            # Ensure output directory exists
            output_path = get_output_path() / output_filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create HTML content
            book_title = book_plan.book_title if book_plan else "Children's Book"
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{book_title}</title>
    <style>
        body {{ font-family: 'Comic Sans MS', cursive; margin: 20px; }}
        .page {{ margin-bottom: 40px; page-break-after: always; }}
        .page img {{ max-width: 100%; height: auto; }}
        .page-text {{ margin-top: 20px; font-size: 18px; line-height: 1.6; }}
        h1 {{ color: #2c3e50; text-align: center; }}
    </style>
</head>
<body>
    <h1>{book_title}</h1>
"""
            
            # Get sorted page numbers
            all_pages = sorted(set(list(page_images.keys()) + list(page_texts.keys())))
            
            for page_num in all_pages:
                html_content += f'    <div class="page" id="page-{page_num}">\n'
                
                # Add image if available
                if page_num in page_images and Path(page_images[page_num]).exists():
                    img_path = Path(page_images[page_num])
                    # Use relative path for images
                    html_content += f'        <img src="{img_path.name}" alt="Page {page_num} illustration" />\n'
                
                # Add text if available
                if page_num in page_texts:
                    text_data = page_texts[page_num]
                    if isinstance(text_data, TextData):
                        text_content = text_data.main_text
                    else:
                        text_content = text_data.get('main_text', text_data.get('text', ''))
                    
                    if text_content:
                        html_content += f'        <div class="page-text">{text_content}</div>\n'
                
                html_content += '    </div>\n'
            
            html_content += """</body>
</html>"""
            
            # Write HTML file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return str(output_path)
            
        except Exception as e:
            raise PDFGenerationError(
                f"HTML generation failed: {str(e)}",
                book_title=book_plan.book_title if book_plan else None
            )