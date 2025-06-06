"""
Character processing module for the Children's Book Generator.

This module handles character description extraction from text descriptions
or uploaded images, creating structured character data for consistent use
throughout the book generation process.
"""

import json
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from ..ai_clients.openai_client import OpenAIClient
from ..utils.config import load_prompt, get_output_path, CHARACTERS_DIR


class CharacterProcessor:
    """Handles character description extraction and processing."""
    
    def __init__(self, openai_client: Optional[OpenAIClient] = None):
        """
        Initialize the character processor.
        
        Args:
            openai_client: OpenAI client instance. If None, creates a new one.
        """
        self.openai_client = openai_client or OpenAIClient()
        self.character_prompt = load_prompt("character_description")
    
    def extract_character_from_text(
        self,
        character_description: str,
        character_name: str = "",
        character_type: str = "main"
    ) -> Dict[str, Any]:
        """
        Extract structured character description from text.
        
        Args:
            character_description: Text description of the character
            character_name: Optional character name
            character_type: Type of character (main, secondary, background)
            
        Returns:
            Structured character description dictionary
        """
        # Prepare input content
        input_content = character_description
        if character_name:
            input_content = f"Character Name: {character_name}\nDescription: {character_description}"
        
        # Extract character description using OpenAI
        character_data = self.openai_client.extract_character_description(
            input_content=input_content,
            prompt_template=self.character_prompt
        )
        
        # Ensure character type is set
        if "character_type" not in character_data or not character_data["character_type"]:
            character_data["character_type"] = character_type
        
        # Ensure character name is set
        if character_name and ("character_name" not in character_data or not character_data["character_name"]):
            character_data["character_name"] = character_name
        
        return character_data
    
    def extract_character_from_image(
        self,
        image_paths: List[Union[str, Path]],
        character_name: str = "",
        character_type: str = "main",
        additional_description: str = ""
    ) -> Dict[str, Any]:
        """
        Extract structured character description from images.
        
        Args:
            image_paths: List of paths to character images
            character_name: Optional character name
            character_type: Type of character (main, secondary, background)
            additional_description: Additional text description to supplement the image
            
        Returns:
            Structured character description dictionary
        """
        # Prepare input content
        input_content = "Please analyze the provided image(s) and create a detailed character description."
        if character_name:
            input_content += f" The character's name is {character_name}."
        if additional_description:
            input_content += f" Additional information: {additional_description}"
        
        # Convert paths to Path objects
        image_paths = [Path(p) for p in image_paths]
        
        # Extract character description using OpenAI with images
        character_data = self.openai_client.extract_character_description(
            input_content=input_content,
            images=image_paths,
            prompt_template=self.character_prompt
        )
        
        # Ensure character type is set
        if "character_type" not in character_data or not character_data["character_type"]:
            character_data["character_type"] = character_type
        
        # Ensure character name is set
        if character_name and ("character_name" not in character_data or not character_data["character_name"]):
            character_data["character_name"] = character_name
        
        return character_data
    
    def save_character_description(
        self,
        character_data: Dict[str, Any],
        filename: Optional[str] = None
    ) -> Path:
        """
        Save character description to a JSON file.
        
        Args:
            character_data: Character description dictionary
            filename: Optional custom filename. If None, uses character name.
            
        Returns:
            Path to the saved file
        """
        if filename is None:
            char_name = character_data.get("character_name", "unknown_character")
            # Clean filename
            char_name = "".join(c for c in char_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            char_name = char_name.replace(' ', '_').lower()
            filename = f"{char_name}.json"
        
        # Ensure filename has .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Get output path
        output_path = get_output_path(CHARACTERS_DIR, filename)
        
        # Save character data
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(character_data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def load_character_description(self, filename: str) -> Dict[str, Any]:
        """
        Load character description from a JSON file.
        
        Args:
            filename: Name of the character file
            
        Returns:
            Character description dictionary
        """
        file_path = CHARACTERS_DIR / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Character file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def process_multiple_characters(
        self,
        character_inputs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process multiple characters from various input types.
        
        Args:
            character_inputs: List of character input dictionaries with format:
                {
                    "type": "text" or "image",
                    "content": "text description" or ["image_path1", "image_path2"],
                    "name": "character name",
                    "character_type": "main|secondary|background",
                    "additional_description": "optional additional text"
                }
        
        Returns:
            List of processed character description dictionaries
        """
        processed_characters = []
        
        for char_input in character_inputs:
            input_type = char_input.get("type", "text")
            content = char_input.get("content", "")
            name = char_input.get("name", "")
            char_type = char_input.get("character_type", "main")
            additional_desc = char_input.get("additional_description", "")
            
            try:
                if input_type == "text":
                    character_data = self.extract_character_from_text(
                        character_description=content,
                        character_name=name,
                        character_type=char_type
                    )
                elif input_type == "image":
                    # Ensure content is a list for image paths
                    if isinstance(content, str):
                        content = [content]
                    
                    character_data = self.extract_character_from_image(
                        image_paths=content,
                        character_name=name,
                        character_type=char_type,
                        additional_description=additional_desc
                    )
                else:
                    raise ValueError(f"Unsupported input type: {input_type}")
                
                # Save character description
                saved_path = self.save_character_description(character_data)
                character_data["_saved_path"] = str(saved_path)
                
                processed_characters.append(character_data)
                
            except Exception as e:
                print(f"Error processing character '{name}': {str(e)}")
                # Continue with other characters
                continue
        
        return processed_characters
    
    def validate_character_data(self, character_data: Dict[str, Any]) -> bool:
        """
        Validate that character data has required fields.
        
        Args:
            character_data: Character description dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = [
            "character_name",
            "character_type", 
            "species",
            "ideogram_character_seed",
            "physical_description",
            "consistency_formula"
        ]
        
        for field in required_fields:
            if field not in character_data:
                print(f"Missing required field: {field}")
                return False
        
        # Validate physical_description structure
        phys_desc = character_data.get("physical_description", {})
        if not isinstance(phys_desc, dict):
            print("physical_description must be a dictionary")
            return False
        
        # Validate required subfields in physical_description
        required_phys_fields = [
            "size",
            "exact_colors", 
            "distinctive_features",
            "fixed_elements",
            "proportions",
            "facial_structure"
        ]
        
        for field in required_phys_fields:
            if field not in phys_desc:
                print(f"Missing required physical_description field: {field}")
                return False
        
        # Validate exact_colors structure
        exact_colors = phys_desc.get("exact_colors", {})
        if not isinstance(exact_colors, dict):
            print("exact_colors must be a dictionary")
            return False
        
        required_color_fields = ["primary", "secondary", "details"]
        for field in required_color_fields:
            if field not in exact_colors:
                print(f"Missing required exact_colors field: {field}")
                return False
        
        # Validate facial_structure
        facial_structure = phys_desc.get("facial_structure", {})
        if not isinstance(facial_structure, dict):
            print("facial_structure must be a dictionary")
            return False
        
        required_facial_fields = ["eyes", "nose", "mouth"]
        for field in required_facial_fields:
            if field not in facial_structure:
                print(f"Missing required facial_structure field: {field}")
                return False
        
        return True
    
    def convert_old_format_to_new(self, old_character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert old character format to new enhanced format.
        
        Args:
            old_character_data: Character data in old format
            
        Returns:
            Character data in new enhanced format
        """
        # Start with existing data
        new_data = old_character_data.copy()
        
        # Get physical description for conversion
        phys_desc = old_character_data.get("physical_description", {})
        
        # Generate ideogram_character_seed from existing data
        char_name = old_character_data.get("character_name", "character")
        species = old_character_data.get("species", "")
        size = phys_desc.get("size", "")
        colors = phys_desc.get("colors", [])
        distinctive_features = phys_desc.get("distinctive_features", [])
        
        # Create immutable character seed
        seed_parts = [char_name, species, size]
        if colors:
            seed_parts.append(f"colored {', '.join(colors)}")
        if distinctive_features:
            seed_parts.extend(distinctive_features[:2])  # Take first 2 features
        
        new_data["ideogram_character_seed"] = ", ".join(filter(None, seed_parts))
        
        # Convert colors array to exact_colors object
        if "colors" in phys_desc:
            exact_colors = {
                "primary": colors[0] if len(colors) > 0 else "",
                "secondary": colors[1] if len(colors) > 1 else "",
                "details": ", ".join(colors[2:]) if len(colors) > 2 else ""
            }
        else:
            exact_colors = {"primary": "", "secondary": "", "details": ""}
        
        # Update physical_description with new structure
        new_phys_desc = {
            "size": phys_desc.get("size", ""),
            "exact_colors": exact_colors,
            "distinctive_features": phys_desc.get("distinctive_features", []),
            "fixed_elements": phys_desc.get("clothing_accessories", []),  # Convert accessories to fixed elements
            "proportions": phys_desc.get("body_type", ""),
            "facial_structure": {
                "eyes": "",
                "nose": "",
                "mouth": ""
            }
        }
        
        # Try to parse facial_features if available
        facial_features = phys_desc.get("facial_features", "")
        if facial_features:
            # Simple parsing - look for eye and nose mentions
            if "eyes" in facial_features.lower():
                new_phys_desc["facial_structure"]["eyes"] = facial_features
            if "nose" in facial_features.lower():
                new_phys_desc["facial_structure"]["nose"] = facial_features
            if "mouth" in facial_features.lower() or "smile" in facial_features.lower():
                new_phys_desc["facial_structure"]["mouth"] = facial_features
        
        # Fill in missing facial structure with distinctive features
        for feature in distinctive_features:
            if "eyes" in feature.lower() and not new_phys_desc["facial_structure"]["eyes"]:
                new_phys_desc["facial_structure"]["eyes"] = feature
            elif "nose" in feature.lower() and not new_phys_desc["facial_structure"]["nose"]:
                new_phys_desc["facial_structure"]["nose"] = feature
        
        # Set defaults for empty fields
        if not new_phys_desc["facial_structure"]["eyes"]:
            new_phys_desc["facial_structure"]["eyes"] = "standard eyes"
        if not new_phys_desc["facial_structure"]["nose"]:
            new_phys_desc["facial_structure"]["nose"] = "standard nose"
        if not new_phys_desc["facial_structure"]["mouth"]:
            new_phys_desc["facial_structure"]["mouth"] = "friendly expression"
        
        new_data["physical_description"] = new_phys_desc
        
        # Generate consistency_formula
        consistency_parts = [new_data["ideogram_character_seed"]]
        visual_notes = old_character_data.get("visual_style_notes", "")
        if visual_notes:
            consistency_parts.append(visual_notes)
        
        new_data["consistency_formula"] = ". ".join(consistency_parts)
        
        # Generate style_anchors from existing data
        style_anchors = []
        consistency_keywords = old_character_data.get("consistency_keywords", [])
        if consistency_keywords:
            style_anchors.extend(consistency_keywords)
        
        # Add default style anchors for children's books
        style_anchors.extend(["children's book style", "friendly", "colorful"])
        
        new_data["style_anchors"] = list(set(style_anchors))  # Remove duplicates
        
        return new_data
    
    def upgrade_character_file(self, filename: str) -> Dict[str, Any]:
        """
        Load a character file and upgrade it to new format if needed.
        
        Args:
            filename: Name of the character file
            
        Returns:
            Character data in new format
        """
        character_data = self.load_character_description(filename)
        
        # Check if already in new format
        if "ideogram_character_seed" in character_data and "consistency_formula" in character_data:
            return character_data
        
        # Convert to new format
        print(f"Converting {filename} to new character format...")
        upgraded_data = self.convert_old_format_to_new(character_data)
        
        # Save upgraded data
        self.save_character_description(upgraded_data, filename)
        
        return upgraded_data

