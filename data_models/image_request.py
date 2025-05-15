# data_models/image_request.py
from typing import Optional
from dataclasses import dataclass

@dataclass
class ImageRequest:
    """Represents a request to generate a single image."""
    placeholder_id: str # The unique ID for this image (e.g., "chapter1_image1", "cover")
    prompt: str         # The detailed prompt for image generation
    style_guide: str    # The overall style guide for the image
    output_path: str    # The full path where the generated image should be saved
    is_cover: bool = False # Flag to indicate if this is for the book cover

