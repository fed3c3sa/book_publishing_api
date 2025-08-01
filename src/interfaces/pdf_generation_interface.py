"""
Interface for PDF generation services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional

from ..domain.models import BookPlan, TextData


class PDFGenerationInterface(ABC):
    """Abstract interface for PDF generation services."""
    
    @abstractmethod
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
        """
        pass
    
    @abstractmethod
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
        """
        pass