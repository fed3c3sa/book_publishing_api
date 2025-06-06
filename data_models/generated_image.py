# data_models/generated_image.py
from typing import Optional
from dataclasses import dataclass

@dataclass
class GeneratedImage:
    """Represents an image that has been generated by the ImageCreatorAgent."""
    placeholder_id: str  # The ID of the placeholder this image fulfills (e.g., "chapter1_image1", "cover")
    prompt_used: str     # The actual prompt used to generate this image
    image_path: str      # The local file path to the generated image
    error_message: Optional[str] = None # If generation failed, this contains the error

