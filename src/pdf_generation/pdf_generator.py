"""
PDF generation module for the Children's Book Generator.

This module handles assembling generated images and text into a final PDF book,
with alternating image pages and text pages.
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import textwrap
import io

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors

from ..utils.config import get_output_path, BOOKS_DIR


class PDFGenerator:
    """Handles PDF generation for children's books."""
    
    def __init__(self):
        """Initialize the PDF generator."""
        self.page_size = A4  # Standard page size
        self.margin = 0.8 * inch  # Margin for frames
        
    def create_book_pdf(
        self,
        book_plan: Dict[str, Any],
        page_images: Dict[int, str],
        page_texts: Dict[int, Dict[str, Any]],
        output_filename: Optional[str] = None
    ) -> str:
        """
        Create a complete PDF book with alternating image and text pages.
        
        Args:
            book_plan: Complete book plan data
            page_images: Dictionary mapping page numbers to image file paths
            page_texts: Dictionary mapping page numbers to text data
            output_filename: Optional custom filename for the PDF
            
        Returns:
            Path to the generated PDF file
        """
        book_title = book_plan.get("book_title", "Untitled Book")
        
        if output_filename is None:
            # Clean book title for filename
            clean_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            clean_title = clean_title.replace(' ', '_').lower()
            output_filename = f"{clean_title}.pdf"
        
        # Ensure filename has .pdf extension
        if not output_filename.endswith('.pdf'):
            output_filename += '.pdf'
        
        # Get output path
        output_path = get_output_path(BOOKS_DIR, output_filename)
        
        # Create PDF with new alternating layout
        self._create_alternating_layout_pdf(
            output_path=output_path,
            book_plan=book_plan,
            page_images=page_images,
            page_texts=page_texts
        )
        
        return str(output_path)
    
    def _create_alternating_layout_pdf(
        self,
        output_path: Path,
        book_plan: Dict[str, Any],
        page_images: Dict[int, str],
        page_texts: Dict[int, Dict[str, Any]]
    ) -> None:
        """
        Create PDF with alternating image and text pages.
        
        Args:
            output_path: Path where the PDF will be saved
            book_plan: Complete book plan data
            page_images: Dictionary mapping page numbers to image file paths
            page_texts: Dictionary mapping page numbers to text data
        """
        # Create canvas for custom page layout
        c = canvas.Canvas(str(output_path), pagesize=self.page_size)
        page_width, page_height = self.page_size
        
        # Get all pages from book plan
        pages = book_plan.get("pages", [])
        pages_sorted = sorted(pages, key=lambda x: x.get("page_number", 0))
        
        pdf_page_number = 1
        
        # Add cover page if available (no title overlay)
        if 0 in page_images:
            self._add_cover_page_no_title(c, page_images[0], pdf_page_number)
            pdf_page_number += 1
        
        # Add alternating image and text pages for each story page
        for page_data in pages_sorted:
            page_number = page_data.get("page_number", 0)
            page_type = page_data.get("page_type", "story")
            
            # Skip cover page (already handled)
            if page_type == "cover":
                continue
            
            # Get image and text for this page
            image_path = page_images.get(page_number)
            text_data = page_texts.get(page_number)
            
            if image_path:
                # Add image page
                self._add_image_page_with_frame(c, image_path, pdf_page_number)
                pdf_page_number += 1
                
                if text_data:
                    # Add text page
                    self._add_text_page_with_frame(c, text_data, pdf_page_number)
                    pdf_page_number += 1
        
        # Save the PDF
        c.save()
    
    def _add_cover_page_no_title(
        self,
        canvas_obj: canvas.Canvas,
        cover_image_path: str,
        page_number: int
    ) -> None:
        """
        Add cover page with full-page image and NO title overlay.
        
        Args:
            canvas_obj: ReportLab canvas object
            cover_image_path: Path to the cover image
            page_number: Page number for positioning
        """
        page_width, page_height = self.page_size
        
        # Add background image (full page)
        if Path(cover_image_path).exists():
            canvas_obj.drawImage(
                cover_image_path,
                0, 0,
                width=page_width,
                height=page_height,
                preserveAspectRatio=True,
                mask='auto'
            )
        
        # Start new page
        canvas_obj.showPage()
    
    def _add_image_page_with_frame(
        self,
        canvas_obj: canvas.Canvas,
        image_path: str,
        page_number: int
    ) -> None:
        """
        Add an image page with elegant rounded frame.
        
        Args:
            canvas_obj: ReportLab canvas object
            image_path: Path to the page image
            page_number: Page number for positioning
        """
        page_width, page_height = self.page_size
        
        if not Path(image_path).exists():
            canvas_obj.showPage()
            return
        
        # Create framed image using PIL
        framed_image_path = self._create_framed_image(image_path)
        
        # Calculate image dimensions with margin
        image_margin = self.margin
        available_width = page_width - (2 * image_margin)
        available_height = page_height - (2 * image_margin)
        
        # Add the framed image
        canvas_obj.drawImage(
            framed_image_path,
            image_margin,
            image_margin,
            width=available_width,
            height=available_height,
            preserveAspectRatio=True,
            mask='auto'
        )
        
        # Start new page
        canvas_obj.showPage()
    
    def _create_framed_image(self, image_path: str) -> str:
        """
        Create a framed version of the image with rounded corners.
        
        Args:
            image_path: Path to the original image
            
        Returns:
            Path to the framed image
        """
        # Load the original image
        original_image = Image.open(image_path)
        
        # Define frame parameters
        frame_thickness = 20
        corner_radius = 30
        frame_color = (139, 69, 19)  # Elegant brown color
        
        # Calculate new dimensions with frame
        new_width = original_image.width + (2 * frame_thickness)
        new_height = original_image.height + (2 * frame_thickness)
        
        # Create new image with frame
        framed_image = Image.new('RGBA', (new_width, new_height), (255, 255, 255, 0))
        
        # Create frame background
        frame_bg = Image.new('RGB', (new_width, new_height), frame_color)
        
        # Create rounded corners mask
        mask = Image.new('L', (new_width, new_height), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, new_width, new_height], corner_radius, fill=255)
        
        # Apply rounded corners to frame
        frame_bg.putalpha(mask)
        
        # Paste frame onto framed image
        framed_image.paste(frame_bg, (0, 0))
        
        # Create inner rounded corners for the image
        inner_mask = Image.new('L', original_image.size, 0)
        inner_draw = ImageDraw.Draw(inner_mask)
        inner_draw.rounded_rectangle([0, 0, original_image.width, original_image.height], corner_radius-10, fill=255)
        
        # Apply inner rounded corners to original image
        original_image = original_image.convert('RGBA')
        original_image.putalpha(inner_mask)
        
        # Paste original image onto frame
        framed_image.paste(original_image, (frame_thickness, frame_thickness), original_image)
        
        # Save framed image to temporary location
        framed_image_path = image_path.replace('.png', '_framed.png')
        framed_image.save(framed_image_path)
        
        return framed_image_path
    
    def _add_text_page_with_frame(
        self,
        canvas_obj: canvas.Canvas,
        text_data: Dict[str, Any],
        page_number: int
    ) -> None:
        """
        Add a text page with cool font, all caps, and elegant frame.
        
        Args:
            canvas_obj: ReportLab canvas object
            text_data: Text data for the page
            page_number: Page number for positioning
        """
        page_width, page_height = self.page_size
        
        # Get page text
        page_text = text_data.get("page_text", "").upper()  # Convert to all caps
        if not page_text:
            canvas_obj.showPage()
            return
        
        # Draw elegant frame around the page
        self._draw_text_page_frame(canvas_obj, page_width, page_height)
        
        # Text styling - cool font, large size
        font_name = "Helvetica-Bold"
        font_size = 18
        line_height = font_size * 1.4
        
        # Text area dimensions (inside frame)
        text_margin = self.margin + 30  # Extra margin inside frame
        text_width = page_width - (2 * text_margin)
        
        # Wrap text to fit width
        canvas_obj.setFont(font_name, font_size)
        
        # Calculate text wrapping
        words = page_text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            text_width_test = canvas_obj.stringWidth(test_line, font_name, font_size)
            
            if text_width_test <= text_width - 40:  # Leave padding
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Calculate total text height
        total_text_height = len(lines) * line_height
        
        # Center text vertically on page
        start_y = (page_height + total_text_height) / 2
        
        # Set text color to elegant dark color
        canvas_obj.setFillColor(colors.Color(0.2, 0.2, 0.3))  # Dark blue-gray
        
        # Draw each line centered
        for i, line in enumerate(lines):
            line_y = start_y - (i * line_height)
            
            # Center text horizontally
            text_width_actual = canvas_obj.stringWidth(line, font_name, font_size)
            text_x = (page_width - text_width_actual) / 2
            
            canvas_obj.drawString(text_x, line_y, line)
        
        # Add page number at bottom
        self._add_page_number(canvas_obj, page_number, page_width, page_height)
        
        # Start new page
        canvas_obj.showPage()
    
    def _draw_text_page_frame(
        self,
        canvas_obj: canvas.Canvas,
        page_width: float,
        page_height: float
    ) -> None:
        """
        Draw an elegant frame around the text page.
        
        Args:
            canvas_obj: ReportLab canvas object
            page_width: Page width
            page_height: Page height
        """
        # Frame parameters
        frame_margin = self.margin / 2
        frame_thickness = 3
        
        # Set frame color - elegant dark brown
        canvas_obj.setStrokeColor(colors.Color(0.4, 0.3, 0.2))
        canvas_obj.setLineWidth(frame_thickness)
        
        # Draw outer frame
        canvas_obj.rect(
            frame_margin,
            frame_margin,
            page_width - (2 * frame_margin),
            page_height - (2 * frame_margin),
            fill=0,
            stroke=1
        )
        
        # Draw inner decorative frame
        inner_margin = frame_margin + 15
        canvas_obj.setLineWidth(1)
        canvas_obj.rect(
            inner_margin,
            inner_margin,
            page_width - (2 * inner_margin),
            page_height - (2 * inner_margin),
            fill=0,
            stroke=1
        )
    
    def _add_page_number(
        self,
        canvas_obj: canvas.Canvas,
        page_number: int,
        page_width: float,
        page_height: float
    ) -> None:
        """
        Add page number at bottom of page.
        
        Args:
            canvas_obj: ReportLab canvas object
            page_number: Page number
            page_width: Page width
            page_height: Page height
        """
        # Page number styling
        font_name = "Helvetica"
        font_size = 12
        
        canvas_obj.setFont(font_name, font_size)
        canvas_obj.setFillColor(colors.Color(0.5, 0.5, 0.5))  # Gray color
        
        # Position at bottom center
        page_num_text = str(page_number)
        text_width = canvas_obj.stringWidth(page_num_text, font_name, font_size)
        text_x = (page_width - text_width) / 2
        text_y = self.margin / 2
        
        canvas_obj.drawString(text_x, text_y, page_num_text)
    
    def create_html_version(
        self,
        book_plan: Dict[str, Any],
        page_images: Dict[int, str],
        page_texts: Dict[int, Dict[str, Any]],
        output_filename: Optional[str] = None
    ) -> str:
        """
        Create an HTML version of the book with alternating layout.
        
        Args:
            book_plan: Complete book plan data
            page_images: Dictionary mapping page numbers to image file paths
            page_texts: Dictionary mapping page numbers to text data
            output_filename: Optional custom filename for the HTML
            
        Returns:
            Path to the generated HTML file
        """
        book_title = book_plan.get("book_title", "Untitled Book")
        
        if output_filename is None:
            # Clean book title for filename
            clean_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            clean_title = clean_title.replace(' ', '_').lower()
            output_filename = f"{clean_title}.html"
        
        # Ensure filename has .html extension
        if not output_filename.endswith('.html'):
            output_filename += '.html'
        
        # Get output path
        output_path = get_output_path(BOOKS_DIR, output_filename)
        
        # Generate HTML content with new layout
        html_content = self._generate_alternating_html_content(
            book_plan=book_plan,
            page_images=page_images,
            page_texts=page_texts
        )
        
        # Save HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_path)
    
    def _generate_alternating_html_content(
        self,
        book_plan: Dict[str, Any],
        page_images: Dict[int, str],
        page_texts: Dict[int, Dict[str, Any]]
    ) -> str:
        """
        Generate HTML content for the book with alternating layout.
        
        Args:
            book_plan: Complete book plan data
            page_images: Dictionary mapping page numbers to image file paths
            page_texts: Dictionary mapping page numbers to text data
            
        Returns:
            Complete HTML content as string
        """
        book_title = book_plan.get("book_title", "Untitled Book")
        
        # Get all pages from book plan
        pages = book_plan.get("pages", [])
        pages_sorted = sorted(pages, key=lambda x: x.get("page_number", 0))
        
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "    <meta charset='UTF-8'>",
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            f"    <title>{book_title}</title>",
            "    <style>",
            "        body { font-family: 'Helvetica', sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }",
            "        .book-container { max-width: 800px; margin: 0 auto; }",
            "        .cover-page { text-align: center; margin-bottom: 40px; }",
            "        .cover-image { max-width: 100%; height: auto; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }",
            "        .page-spread { display: flex; margin-bottom: 40px; gap: 20px; align-items: stretch; }",
            "        .image-page { flex: 1; }",
            "        .image-page img { width: 100%; height: auto; border: 8px solid #8B4513; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }",
            "        .text-page { flex: 1; border: 3px solid #664228; border-radius: 10px; padding: 40px; background: white; display: flex; flex-direction: column; justify-content: center; position: relative; }",
            "        .text-content { font-size: 18px; font-weight: bold; text-transform: uppercase; color: #333344; text-align: center; line-height: 1.6; }",
            "        .page-number { position: absolute; bottom: 10px; left: 50%; transform: translateX(-50%); font-size: 12px; color: #888; }",
            "        @media (max-width: 768px) { .page-spread { flex-direction: column; } }",
            "    </style>",
            "</head>",
            "<body>",
            "    <div class='book-container'>",
            f"        <h1 style='text-align: center; color: #333; margin-bottom: 40px;'>{book_title}</h1>"
        ]
        
        # Add cover page if available
        if 0 in page_images:
            cover_image_name = Path(page_images[0]).name
            html_parts.extend([
                "        <div class='cover-page'>",
                f"            <img src='{cover_image_name}' alt='Book Cover' class='cover-image'>",
                "        </div>"
            ])
        
        page_counter = 1
        
        # Add alternating image and text pages
        for page_data in pages_sorted:
            page_number = page_data.get("page_number", 0)
            page_type = page_data.get("page_type", "story")
            
            # Skip cover page
            if page_type == "cover":
                continue
            
            image_path = page_images.get(page_number)
            text_data = page_texts.get(page_number)
            
            if image_path and text_data:
                image_name = Path(image_path).name
                page_text = text_data.get("page_text", "").upper()
                
                html_parts.extend([
                    "        <div class='page-spread'>",
                    "            <div class='image-page'>",
                    f"                <img src='{image_name}' alt='Page {page_number} Illustration'>",
                    "            </div>",
                    "            <div class='text-page'>",
                    f"                <div class='text-content'>{page_text}</div>",
                    f"                <div class='page-number'>{page_counter + 1}</div>",
                    "            </div>",
                    "        </div>"
                ])
                page_counter += 2  # Two pages per spread
        
        html_parts.extend([
            "    </div>",
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html_parts)

