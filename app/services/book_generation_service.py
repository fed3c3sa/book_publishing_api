"""
Book Generation Service
Handles book cover generation and order management
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Import modules from local services
from .character_processing import CharacterProcessor
from .book_planning import BookPlanner
from .content_generation import ImageGenerator
from .utils.config import load_config
from .storage_service import CloudStorageService

class BookGenerationService:
    """Service for handling book cover generation and order management"""
    
    def __init__(self):
        """Initialize the service with required processors"""
        self.character_processor = CharacterProcessor()
        self.book_planner = BookPlanner()
        self.image_generator = ImageGenerator()
        self.config = load_config()
        
        # Initialize Cloud Storage service
        self.storage_service = CloudStorageService()
        
        # Create directory structure in Cloud Storage
        self.storage_service.create_directory_structure([
            'covers/', 'orders/', 'characters/', 'plans/', 'images/', 'texts/', 'books/'
        ])
    
    def generate_cover_and_save_order(
        self,
        order_id: str,
        book_title: str,
        story_idea: str,
        num_pages: int,
        age_group: str,
        language: str,
        art_style: str,
        characters_data: List[Dict[str, Any]],
        themes: List[str],
        customer_email: str,
        customer_name: str
    ) -> Dict[str, Any]:
        """
        Generate book cover and save order information
        
        Args:
            order_id: Unique order identifier
            book_title: Title of the book
            story_idea: Story concept
            num_pages: Number of pages
            age_group: Target age group
            language: Book language
            art_style: Artistic style
            characters_data: Character information
            themes: Story themes
            customer_email: Customer email
            customer_name: Customer name
            
        Returns:
            Dictionary with cover path and order data
        """
        try:
            # Process characters
            processed_characters = []
            if characters_data:
                processed_characters = self.character_processor.process_multiple_characters(characters_data)
            
            # Create a minimal book plan (just for cover generation)
            book_plan = self.book_planner.create_book_plan(
                story_idea=story_idea,
                characters=processed_characters,
                num_pages=num_pages,
                age_group=age_group,
                language=language,
                book_title=book_title,
                themes=themes
            )
            
            # Generate cover image
            cover_image_path = self.image_generator.generate_book_cover(
                book_plan=book_plan,
                characters=processed_characters,
                art_style=art_style
            )
            print(f"Cover generated at: {cover_image_path}")
            
            # Read the generated cover file and upload to Cloud Storage
            if not Path(cover_image_path).exists():
                raise FileNotFoundError(f"Generated cover file does not exist: {cover_image_path}")
            
            # Read the image file
            with open(cover_image_path, 'rb') as f:
                image_data = f.read()
            
            # Upload to Cloud Storage
            cloud_cover_url = self.storage_service.save_cover_image(order_id, image_data)
            print(f"Cover uploaded to Cloud Storage: {cloud_cover_url}")
            
            # Get public URL for the cover
            public_cover_url = self.storage_service.get_public_url(f"covers/cover_{order_id}.png")
            
            # Create order data
            order_data = {
                'order_id': order_id,
                'customer_name': customer_name,
                'customer_email': customer_email,
                'book_title': book_title,
                'story_idea': story_idea,
                'num_pages': num_pages,
                'age_group': age_group,
                'language': language,
                'art_style': art_style,
                'characters': characters_data,
                'themes': themes,
                'cover_path': cloud_cover_url,
                'cover_public_url': public_cover_url,
                'order_date': datetime.now().isoformat(),
                'status': 'cover_generated',
                'payment_status': 'pending'
            }
            
            # Save order to Cloud Storage
            order_cloud_url = self.storage_service.save_order_data(order_id, order_data)
            print(f"Order data saved to Cloud Storage: {order_cloud_url}")
            
            return {
                'cover_path': public_cover_url,
                'cover_cloud_path': cloud_cover_url,
                'order_data': order_data
            }
            
        except Exception as e:
            print(f"Error in book generation service: {str(e)}")
            raise e
    
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        Retrieve order information
        
        Args:
            order_id: Order identifier
            
        Returns:
            Order data dictionary
        """
        cloud_file_path = f"orders/order_{order_id}.json"
        
        if not self.storage_service.file_exists(cloud_file_path):
            raise FileNotFoundError(f"Order {order_id} not found")
        
        return self.storage_service.download_json(cloud_file_path)
    
    def update_order_status(self, order_id: str, status: str, **kwargs) -> None:
        """
        Update order status and additional fields
        
        Args:
            order_id: Order identifier
            status: New status
            **kwargs: Additional fields to update
        """
        order_data = self.get_order(order_id)
        order_data['status'] = status
        
        # Update additional fields
        for key, value in kwargs.items():
            order_data[key] = value
        
        # Save updated order to Cloud Storage
        self.storage_service.save_order_data(order_id, order_data) 