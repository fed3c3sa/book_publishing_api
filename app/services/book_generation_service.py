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

class BookGenerationService:
    """Service for handling book cover generation and order management"""
    
    def __init__(self):
        """Initialize the service with required processors"""
        self.character_processor = CharacterProcessor()
        self.book_planner = BookPlanner()
        self.image_generator = ImageGenerator()
        self.config = load_config()
        
        # Ensure output directories exist
        self.covers_dir = Path('output/covers')
        self.orders_dir = Path('output/orders')
        self.covers_dir.mkdir(parents=True, exist_ok=True)
        self.orders_dir.mkdir(parents=True, exist_ok=True)
    
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
            
            # Save the cover to our output directory
            cover_filename = f"cover_{order_id}.png"
            final_cover_path = self.covers_dir / cover_filename
            
            # Copy the generated cover to our output directory
            if not Path(cover_image_path).exists():
                raise FileNotFoundError(f"Generated cover file does not exist: {cover_image_path}")
            
            shutil.copy2(cover_image_path, final_cover_path)
            print(f"Cover copied to: {final_cover_path}")
            
            # Verify the copy was successful
            if not final_cover_path.exists():
                raise FileNotFoundError("Failed to save cover file")
            
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
                'cover_path': str(final_cover_path),
                'order_date': datetime.now().isoformat(),
                'status': 'cover_generated',
                'payment_status': 'pending'
            }
            
            # Save order to JSON file
            order_file_path = self.orders_dir / f"order_{order_id}.json"
            with open(order_file_path, 'w', encoding='utf-8') as f:
                json.dump(order_data, f, indent=2, ensure_ascii=False)
            
            return {
                'cover_path': str(final_cover_path),
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
        order_file_path = self.orders_dir / f"order_{order_id}.json"
        
        if not order_file_path.exists():
            raise FileNotFoundError(f"Order {order_id} not found")
        
        with open(order_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
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
        
        # Save updated order
        order_file_path = self.orders_dir / f"order_{order_id}.json"
        with open(order_file_path, 'w', encoding='utf-8') as f:
            json.dump(order_data, f, indent=2, ensure_ascii=False) 