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
        # Prepare input content with proper character name formatting
        input_content = "Please analyze the provided image(s) and create a detailed character description."
        if character_name:
            input_content += f" The character's name is {character_name}."
        if additional_description:
            input_content += f" {additional_description}"
        
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
        
        # Ensure character name is set - prioritize the provided name
        if character_name:
            character_data["character_name"] = character_name
        elif "character_name" not in character_data or not character_data["character_name"]:
            character_data["character_name"] = "Unknown Character"
        
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
        Validate that character data has required fields for the comprehensive format.
        
        Args:
            character_data: Character description dictionary
            
        Returns:
            True if valid, False otherwise
        """
        # Core required fields
        required_fields = [
            "character_name",
            "character_type", 
            "species",
            "age_category",
            "gender_presentation",
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
            "overall_impression",
            "size",
            "build_physique", 
            "height_weight",
            "exact_colors",
            "head_face",
            "body_structure",
            "skin_surface",
            "distinctive_features",
            "fixed_elements",
            "proportions",
            "mobility_posture"
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
        
        required_color_fields = ["primary", "secondary", "accent", "details", "seasonal_variations"]
        for field in required_color_fields:
            if field not in exact_colors:
                print(f"Missing required exact_colors field: {field}")
                return False
        
        # Validate head_face structure
        head_face = phys_desc.get("head_face", {})
        if not isinstance(head_face, dict):
            print("head_face must be a dictionary")
            return False
        
        required_head_face_fields = ["head_shape", "facial_structure", "hair_fur_covering", "ears", "other_facial_features"]
        for field in required_head_face_fields:
            if field not in head_face:
                print(f"Missing required head_face field: {field}")
                return False
        
        # Validate facial_structure within head_face
        facial_structure = head_face.get("facial_structure", {})
        if not isinstance(facial_structure, dict):
            print("facial_structure must be a dictionary")
            return False
        
        required_facial_fields = ["eyes", "nose", "mouth", "cheeks", "chin", "forehead"]
        for field in required_facial_fields:
            if field not in facial_structure:
                print(f"Missing required facial_structure field: {field}")
                return False
        
        # Validate hair_fur_covering structure
        hair_fur = head_face.get("hair_fur_covering", {})
        if not isinstance(hair_fur, dict):
            print("hair_fur_covering must be a dictionary")
            return False
        
        required_hair_fur_fields = ["type", "color", "texture", "length", "style", "special_features"]
        for field in required_hair_fur_fields:
            if field not in hair_fur:
                print(f"Missing required hair_fur_covering field: {field}")
                return False
        
        # Validate body_structure
        body_structure = phys_desc.get("body_structure", {})
        if not isinstance(body_structure, dict):
            print("body_structure must be a dictionary")
            return False
        
        required_body_fields = ["torso", "arms_hands", "legs_feet", "tail", "wings", "other_appendages"]
        for field in required_body_fields:
            if field not in body_structure:
                print(f"Missing required body_structure field: {field}")
                return False
        
        # Validate skin_surface
        skin_surface = phys_desc.get("skin_surface", {})
        if not isinstance(skin_surface, dict):
            print("skin_surface must be a dictionary")
            return False
        
        required_skin_fields = ["texture", "patterns", "markings", "special_properties"]
        for field in required_skin_fields:
            if field not in skin_surface:
                print(f"Missing required skin_surface field: {field}")
                return False
        
        # Validate mobility_posture
        mobility_posture = phys_desc.get("mobility_posture", {})
        if not isinstance(mobility_posture, dict):
            print("mobility_posture must be a dictionary")
            return False
        
        required_mobility_fields = ["typical_posture", "gait", "gesture_patterns", "flexibility"]
        for field in required_mobility_fields:
            if field not in mobility_posture:
                print(f"Missing required mobility_posture field: {field}")
                return False
        
        # Validate optional but important sections
        optional_sections = [
            "clothing_accessories",
            "personality_psychology", 
            "background_context",
            "behavioral_patterns",
            "voice_communication",
            "story_role_dynamics"
        ]
        
        for section in optional_sections:
            if section in character_data and not isinstance(character_data[section], dict):
                print(f"{section} must be a dictionary if present")
                return False
        
        # Validate clothing_accessories structure if present
        if "clothing_accessories" in character_data:
            clothing = character_data["clothing_accessories"]
            required_clothing_fields = ["regular_outfit", "accessories", "seasonal_alternate_outfits", "clothing_preferences"]
            for field in required_clothing_fields:
                if field not in clothing:
                    print(f"Missing required clothing_accessories field: {field}")
                    return False
            
            # Validate regular_outfit structure
            regular_outfit = clothing.get("regular_outfit", {})
            if not isinstance(regular_outfit, dict):
                print("regular_outfit must be a dictionary")
                return False
            
            required_outfit_fields = ["upper_body", "lower_body", "footwear", "undergarments", "style"]
            for field in required_outfit_fields:
                if field not in regular_outfit:
                    print(f"Missing required regular_outfit field: {field}")
                    return False
            
            # Validate accessories structure
            accessories = clothing.get("accessories", {})
            if not isinstance(accessories, dict):
                print("accessories must be a dictionary")
                return False
            
            required_accessory_fields = ["jewelry", "functional_items", "decorative_items", "special_items"]
            for field in required_accessory_fields:
                if field not in accessories:
                    print(f"Missing required accessories field: {field}")
                    return False
        
        # Validate personality_psychology structure if present
        if "personality_psychology" in character_data:
            personality = character_data["personality_psychology"]
            required_personality_fields = ["core_personality_traits", "emotional_characteristics", "social_behavior", "cognitive_traits", "motivations_values"]
            for field in required_personality_fields:
                if field not in personality:
                    print(f"Missing required personality_psychology field: {field}")
                    return False
            
            # Validate nested personality structures
            for nested_field in ["emotional_characteristics", "social_behavior", "cognitive_traits", "motivations_values"]:
                if nested_field in personality and not isinstance(personality[nested_field], dict):
                    print(f"personality_psychology.{nested_field} must be a dictionary")
                    return False
        
        # Validate background_context structure if present  
        if "background_context" in character_data:
            background = character_data["background_context"]
            required_background_fields = ["origin_story", "current_living_situation", "social_economic_status", "cultural_background", "education_experience", "significant_relationships", "life_experiences"]
            for field in required_background_fields:
                if field not in background:
                    print(f"Missing required background_context field: {field}")
                    return False
        
        # Validate behavioral_patterns structure if present
        if "behavioral_patterns" in character_data:
            behavioral = character_data["behavioral_patterns"]
            required_behavioral_fields = ["daily_routines", "hobbies_interests", "skills_talents", "quirks_habits", "reaction_patterns", "comfort_items"]
            for field in required_behavioral_fields:
                if field not in behavioral:
                    print(f"Missing required behavioral_patterns field: {field}")
                    return False
        
        # Validate voice_communication structure if present
        if "voice_communication" in character_data:
            voice = character_data["voice_communication"]
            required_voice_fields = ["speaking_voice", "vocabulary_style", "catchphrases", "non_verbal_communication", "laugh_type", "crying_expression"]
            for field in required_voice_fields:
                if field not in voice:
                    print(f"Missing required voice_communication field: {field}")
                    return False
        
        # Validate story_role_dynamics structure if present
        if "story_role_dynamics" in character_data:
            story_role = character_data["story_role_dynamics"]
            required_story_fields = ["narrative_function", "character_arc_potential", "relationship_dynamics", "conflict_sources", "symbolic_meaning"]
            for field in required_story_fields:
                if field not in story_role:
                    print(f"Missing required story_role_dynamics field: {field}")
                    return False
        
        return True
    
    def convert_old_format_to_new(self, old_character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert old character format to new comprehensive enhanced format.
        
        Args:
            old_character_data: Character data in old format
            
        Returns:
            Character data in new comprehensive enhanced format
        """
        # Start with existing data
        new_data = old_character_data.copy()
        
        # Get physical description for conversion
        phys_desc = old_character_data.get("physical_description", {})
        
        # Add new core fields with defaults
        if "age_category" not in new_data:
            new_data["age_category"] = "unknown"
        if "gender_presentation" not in new_data:
            new_data["gender_presentation"] = "neutral"
        
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
                "accent": colors[2] if len(colors) > 2 else "",
                "details": ", ".join(colors[3:]) if len(colors) > 3 else "",
                "seasonal_variations": ""
            }
        else:
            exact_colors = {
                "primary": "", 
                "secondary": "", 
                "accent": "",
                "details": "",
                "seasonal_variations": ""
            }
        
        # Parse facial_features if available
        facial_features = phys_desc.get("facial_features", "")
        facial_structure = {
            "eyes": "",
            "nose": "",
            "mouth": "",
            "cheeks": "",
            "chin": "",
            "forehead": ""
        }
        
        # Try to parse facial_features into structure
        if facial_features:
            if "eyes" in facial_features.lower():
                facial_structure["eyes"] = facial_features
            if "nose" in facial_features.lower():
                facial_structure["nose"] = facial_features
            if "mouth" in facial_features.lower() or "smile" in facial_features.lower():
                facial_structure["mouth"] = facial_features
        
        # Fill in missing facial structure with distinctive features
        for feature in distinctive_features:
            if "eyes" in feature.lower() and not facial_structure["eyes"]:
                facial_structure["eyes"] = feature
            elif "nose" in feature.lower() and not facial_structure["nose"]:
                facial_structure["nose"] = feature
            elif "mouth" in feature.lower() and not facial_structure["mouth"]:
                facial_structure["mouth"] = feature
        
        # Set defaults for empty facial fields
        if not facial_structure["eyes"]:
            facial_structure["eyes"] = "standard expressive eyes"
        if not facial_structure["nose"]:
            facial_structure["nose"] = "standard nose"
        if not facial_structure["mouth"]:
            facial_structure["mouth"] = "friendly expression"
        if not facial_structure["cheeks"]:
            facial_structure["cheeks"] = "standard cheeks"
        if not facial_structure["chin"]:
            facial_structure["chin"] = "standard chin"
        if not facial_structure["forehead"]:
            facial_structure["forehead"] = "standard forehead"
        
        # Create comprehensive physical_description with new structure
        new_phys_desc = {
            "overall_impression": f"A {species} with {size} build and distinctive appearance",
            "size": phys_desc.get("size", "medium"),
            "build_physique": phys_desc.get("body_type", "standard build"),
            "height_weight": f"Proportionate {size} size for their species",
            "exact_colors": exact_colors,
            
            "head_face": {
                "head_shape": "standard proportions for species",
                "facial_structure": facial_structure,
                "hair_fur_covering": {
                    "type": "fur" if species != "human" else "hair",
                    "color": exact_colors["primary"],
                    "texture": "soft",
                    "length": "medium",
                    "style": "natural",
                    "special_features": ""
                },
                "ears": "typical for species",
                "other_facial_features": ""
            },
            
            "body_structure": {
                "torso": "proportionate",
                "arms_hands": "standard proportions",
                "legs_feet": "standard proportions", 
                "tail": "species appropriate" if species != "human" else "none",
                "wings": "none",
                "other_appendages": "none"
            },
            
            "skin_surface": {
                "texture": "smooth" if species == "human" else "furry",
                "patterns": ", ".join(colors[1:]) if len(colors) > 1 else "solid",
                "markings": "",
                "special_properties": ""
            },
            
            "distinctive_features": phys_desc.get("distinctive_features", []),
            "fixed_elements": phys_desc.get("clothing_accessories", []),  # Convert accessories to fixed elements
            "proportions": f"Standard proportions with {phys_desc.get('body_type', 'balanced')} build",
            
            "mobility_posture": {
                "typical_posture": "upright and confident",
                "gait": "steady walk",
                "gesture_patterns": "expressive hand movements",
                "flexibility": "normal range of motion"
            }
        }
        
        new_data["physical_description"] = new_phys_desc
        
        # Add clothing_accessories section
        new_data["clothing_accessories"] = {
            "regular_outfit": {
                "upper_body": "age-appropriate top",
                "lower_body": "comfortable bottoms",
                "footwear": "suitable shoes or bare feet/paws",
                "undergarments": "appropriate undergarments",
                "style": "casual and comfortable"
            },
            "accessories": {
                "jewelry": "",
                "functional_items": "",
                "decorative_items": "",
                "special_items": ""
            },
            "seasonal_alternate_outfits": "weather-appropriate variations",
            "clothing_preferences": "comfort over fashion"
        }
        
        # Add personality_psychology section
        personality_traits = old_character_data.get("personality_traits", [])
        new_data["personality_psychology"] = {
            "core_personality_traits": personality_traits,
            "emotional_characteristics": {
                "dominant_emotions": ["happy", "curious"],
                "emotional_range": "wide range of emotions",
                "emotional_triggers": "based on situation",
                "emotional_expression": "open and honest"
            },
            "social_behavior": {
                "interaction_style": "friendly",
                "communication_pattern": "clear and direct",
                "relationship_approach": "trusting and loyal",
                "conflict_resolution": "peaceful discussion"
            },
            "cognitive_traits": {
                "intelligence_type": "balanced",
                "learning_style": "visual and hands-on",
                "problem_solving": "creative and intuitive",
                "attention_span": "good focus when interested"
            },
            "motivations_values": {
                "primary_motivations": "helping others and learning",
                "core_values": "friendship and honesty",
                "fears_concerns": "age-appropriate worries",
                "aspirations": "to grow and make friends"
            }
        }
        
        # Add background_context section
        new_data["background_context"] = {
            "origin_story": "Comes from a loving environment",
            "current_living_situation": "stable and supportive home",
            "social_economic_status": "comfortable middle class",
            "cultural_background": "diverse and inclusive",
            "education_experience": "age-appropriate learning",
            "significant_relationships": "family and close friends",
            "life_experiences": "typical childhood adventures"
        }
        
        # Add behavioral_patterns section
        new_data["behavioral_patterns"] = {
            "daily_routines": "structured but flexible schedule",
            "hobbies_interests": "age-appropriate activities",
            "skills_talents": "developing natural abilities",
            "quirks_habits": "endearing personal habits",
            "reaction_patterns": "thoughtful responses",
            "comfort_items": "favorite toy or blanket"
        }
        
        # Add voice_communication section
        new_data["voice_communication"] = {
            "speaking_voice": "clear and age-appropriate",
            "vocabulary_style": "simple but expressive",
            "catchphrases": "",
            "non_verbal_communication": "expressive gestures and faces",
            "laugh_type": "genuine and joyful",
            "crying_expression": "tears when upset"
        }
        
        # Add story_role_dynamics section
        char_type = old_character_data.get("character_type", "main")
        new_data["story_role_dynamics"] = {
            "narrative_function": char_type + " character",
            "character_arc_potential": "room for growth and learning",
            "relationship_dynamics": "forms strong bonds with others",
            "conflict_sources": "age-appropriate challenges",
            "symbolic_meaning": "represents childhood wonder and growth"
        }
        
        # Generate enhanced consistency_formula
        consistency_parts = [new_data["ideogram_character_seed"]]
        visual_notes = old_character_data.get("visual_style_notes", "")
        if visual_notes:
            consistency_parts.append(visual_notes)
        consistency_parts.append("consistent character design for children's book")
        
        new_data["consistency_formula"] = ". ".join(consistency_parts)
        
        # Generate style_anchors from existing data
        style_anchors = []
        consistency_keywords = old_character_data.get("consistency_keywords", [])
        if consistency_keywords:
            style_anchors.extend(consistency_keywords)
        
        # Add default style anchors for children's books
        style_anchors.extend([
            "children's book illustration", 
            "friendly and approachable", 
            "colorful and vibrant",
            "soft and rounded features",
            "expressive and engaging"
        ])
        
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
    
    def create_comprehensive_character_template(
        self,
        character_name: str = "",
        character_type: str = "main",
        species: str = "human"
    ) -> Dict[str, Any]:
        """
        Create a comprehensive character template with all required fields.
        
        Args:
            character_name: Name of the character
            character_type: Type of character (main, secondary, background)
            species: Species/type of the character
            
        Returns:
            Complete character template dictionary
        """
        return {
            "character_name": character_name,
            "character_type": character_type,
            "species": species,
            "age_category": "child",
            "gender_presentation": "neutral",
            
            "ideogram_character_seed": f"{character_name}, {species}, friendly children's book character",
            
            "physical_description": {
                "overall_impression": f"A friendly {species} character with appealing features",
                "size": "medium",
                "build_physique": "healthy and active",
                "height_weight": "proportionate for age and species",
                
                "exact_colors": {
                    "primary": "warm and inviting color",
                    "secondary": "complementary accent color",
                    "accent": "highlight color for details",
                    "details": "specific color placements",
                    "seasonal_variations": "any seasonal color changes"
                },
                
                "head_face": {
                    "head_shape": "rounded and friendly",
                    "facial_structure": {
                        "eyes": "large, expressive, warm eyes",
                        "nose": "small, cute nose",
                        "mouth": "friendly smile",
                        "cheeks": "soft, rounded cheeks",
                        "chin": "gentle chin",
                        "forehead": "smooth forehead"
                    },
                    "hair_fur_covering": {
                        "type": "hair" if species == "human" else "fur",
                        "color": "natural color",
                        "texture": "soft and touchable",
                        "length": "medium length",
                        "style": "neat and tidy",
                        "special_features": "any unique hair/fur features"
                    },
                    "ears": "appropriately sized for species",
                    "other_facial_features": "any additional facial features"
                },
                
                "body_structure": {
                    "torso": "proportionate and healthy",
                    "arms_hands": "active and expressive hands",
                    "legs_feet": "strong and capable",
                    "tail": "none" if species == "human" else "species appropriate tail",
                    "wings": "none unless flying species",
                    "other_appendages": "any additional limbs or features"
                },
                
                "skin_surface": {
                    "texture": "smooth" if species == "human" else "species appropriate",
                    "patterns": "any natural patterns or markings",
                    "markings": "distinctive marks or features",
                    "special_properties": "any magical or special characteristics"
                },
                
                "distinctive_features": ["feature1", "feature2", "feature3"],
                "fixed_elements": ["consistent element1", "consistent element2"],
                "proportions": "child-friendly proportions with slightly larger head",
                
                "mobility_posture": {
                    "typical_posture": "confident and approachable",
                    "gait": "energetic and purposeful",
                    "gesture_patterns": "expressive and animated",
                    "flexibility": "age-appropriate agility"
                }
            },
            
            "clothing_accessories": {
                "regular_outfit": {
                    "upper_body": "comfortable, colorful top",
                    "lower_body": "practical bottoms for play",
                    "footwear": "appropriate shoes or bare feet",
                    "undergarments": "appropriate undergarments",
                    "style": "child-friendly and practical"
                },
                "accessories": {
                    "jewelry": "simple, age-appropriate jewelry if any",
                    "functional_items": "useful items they carry",
                    "decorative_items": "fun decorative elements",
                    "special_items": "magical or significant items"
                },
                "seasonal_alternate_outfits": "weather-appropriate clothing changes",
                "clothing_preferences": "comfort and freedom of movement prioritized"
            },
            
            "personality_psychology": {
                "core_personality_traits": ["curious", "kind", "brave", "imaginative"],
                "emotional_characteristics": {
                    "dominant_emotions": ["joy", "wonder", "compassion"],
                    "emotional_range": "full spectrum of healthy emotions",
                    "emotional_triggers": "situations that evoke strong feelings",
                    "emotional_expression": "open and honest emotional communication"
                },
                "social_behavior": {
                    "interaction_style": "friendly and inclusive",
                    "communication_pattern": "clear and age-appropriate",
                    "relationship_approach": "trusting but cautious with strangers",
                    "conflict_resolution": "talking through problems peacefully"
                },
                "cognitive_traits": {
                    "intelligence_type": "creative and emotional intelligence",
                    "learning_style": "hands-on and visual learning",
                    "problem_solving": "innovative and collaborative",
                    "attention_span": "good focus on interesting topics"
                },
                "motivations_values": {
                    "primary_motivations": "learning, helping others, having fun",
                    "core_values": "friendship, honesty, kindness, fairness",
                    "fears_concerns": "age-appropriate fears like darkness or separation",
                    "aspirations": "to make friends and have adventures"
                }
            },
            
            "background_context": {
                "origin_story": "loving family background with supportive environment",
                "current_living_situation": "safe, nurturing home with family",
                "social_economic_status": "comfortable middle-class background",
                "cultural_background": "inclusive and diverse cultural influences",
                "education_experience": "age-appropriate schooling and learning",
                "significant_relationships": "close family bonds and developing friendships",
                "life_experiences": "typical childhood experiences with some unique adventures"
            },
            
            "behavioral_patterns": {
                "daily_routines": "balanced routine of play, learning, and rest",
                "hobbies_interests": "age-appropriate hobbies and creative activities",
                "skills_talents": "developing natural talents and abilities",
                "quirks_habits": "endearing personal habits and mannerisms",
                "reaction_patterns": "thoughtful and age-appropriate responses",
                "comfort_items": "favorite toy, blanket, or comfort object"
            },
            
            "voice_communication": {
                "speaking_voice": "clear, warm, age-appropriate voice",
                "vocabulary_style": "expanding vocabulary with simple expressions",
                "catchphrases": "favorite expressions or sayings",
                "non_verbal_communication": "expressive body language and gestures",
                "laugh_type": "genuine, infectious laughter",
                "crying_expression": "natural tears when sad or frustrated"
            },
            
            "story_role_dynamics": {
                "narrative_function": f"{character_type} character driving story forward",
                "character_arc_potential": "growth through challenges and learning",
                "relationship_dynamics": "forms meaningful connections with others",
                "conflict_sources": "age-appropriate internal and external challenges",
                "symbolic_meaning": "represents childhood wonder, growth, and possibility"
            },
            
            "consistency_formula": f"{character_name}, {species}, consistent children's book character with distinctive appearance and personality",
            "style_anchors": [
                "children's book illustration",
                "warm and inviting",
                "colorful and vibrant",
                "soft rounded features",
                "expressive and engaging",
                "friendly and approachable"
            ],
            "visual_style_notes": "warm, child-friendly art style with soft lighting and vibrant colors that appeal to young readers"
        }
    
    def generate_character_analysis_report(self, character_data: Dict[str, Any]) -> str:
        """
        Generate a comprehensive character analysis report in readable format.
        
        Args:
            character_data: Complete character description dictionary
            
        Returns:
            Formatted string report of the character analysis
        """
        report = []
        
        # Header
        name = character_data.get("character_name", "Unknown Character")
        report.append(f"={'='*60}")
        report.append(f"COMPREHENSIVE CHARACTER ANALYSIS: {name.upper()}")
        report.append(f"={'='*60}")
        report.append("")
        
        # Basic Information
        report.append("BASIC INFORMATION")
        report.append("-" * 20)
        report.append(f"Name: {name}")
        report.append(f"Character Type: {character_data.get('character_type', 'Unknown')}")
        report.append(f"Species: {character_data.get('species', 'Unknown')}")
        report.append(f"Age Category: {character_data.get('age_category', 'Unknown')}")
        report.append(f"Gender Presentation: {character_data.get('gender_presentation', 'Unknown')}")
        report.append("")
        
        # Character Seed & Consistency
        report.append("CHARACTER CONSISTENCY FORMULA")
        report.append("-" * 35)
        report.append(f"Ideogram Seed: {character_data.get('ideogram_character_seed', 'Not defined')}")
        report.append(f"Consistency Formula: {character_data.get('consistency_formula', 'Not defined')}")
        report.append("")
        
        # Physical Description
        phys_desc = character_data.get("physical_description", {})
        report.append("PHYSICAL DESCRIPTION")
        report.append("-" * 25)
        report.append(f"Overall Impression: {phys_desc.get('overall_impression', 'Not described')}")
        report.append(f"Size: {phys_desc.get('size', 'Not specified')}")
        report.append(f"Build/Physique: {phys_desc.get('build_physique', 'Not described')}")
        report.append(f"Height/Weight: {phys_desc.get('height_weight', 'Not specified')}")
        report.append(f"Proportions: {phys_desc.get('proportions', 'Not described')}")
        report.append("")
        
        # Colors
        exact_colors = phys_desc.get("exact_colors", {})
        report.append("COLOR SCHEME")
        report.append("-" * 15)
        report.append(f"Primary Color: {exact_colors.get('primary', 'Not specified')}")
        report.append(f"Secondary Color: {exact_colors.get('secondary', 'Not specified')}")
        report.append(f"Accent Color: {exact_colors.get('accent', 'Not specified')}")
        report.append(f"Color Details: {exact_colors.get('details', 'Not specified')}")
        report.append(f"Seasonal Variations: {exact_colors.get('seasonal_variations', 'None')}")
        report.append("")
        
        # Head and Face
        head_face = phys_desc.get("head_face", {})
        report.append("HEAD AND FACIAL FEATURES")
        report.append("-" * 30)
        report.append(f"Head Shape: {head_face.get('head_shape', 'Not described')}")
        
        facial_structure = head_face.get("facial_structure", {})
        report.append("Facial Structure:")
        report.append(f"  Eyes: {facial_structure.get('eyes', 'Not described')}")
        report.append(f"  Nose: {facial_structure.get('nose', 'Not described')}")
        report.append(f"  Mouth: {facial_structure.get('mouth', 'Not described')}")
        report.append(f"  Cheeks: {facial_structure.get('cheeks', 'Not described')}")
        report.append(f"  Chin: {facial_structure.get('chin', 'Not described')}")
        report.append(f"  Forehead: {facial_structure.get('forehead', 'Not described')}")
        
        hair_fur = head_face.get("hair_fur_covering", {})
        report.append("Hair/Fur Coverage:")
        report.append(f"  Type: {hair_fur.get('type', 'Not specified')}")
        report.append(f"  Color: {hair_fur.get('color', 'Not specified')}")
        report.append(f"  Texture: {hair_fur.get('texture', 'Not specified')}")
        report.append(f"  Length: {hair_fur.get('length', 'Not specified')}")
        report.append(f"  Style: {hair_fur.get('style', 'Not specified')}")
        report.append(f"  Special Features: {hair_fur.get('special_features', 'None')}")
        
        report.append(f"Ears: {head_face.get('ears', 'Not described')}")
        report.append(f"Other Facial Features: {head_face.get('other_facial_features', 'None')}")
        report.append("")
        
        # Body Structure
        body_structure = phys_desc.get("body_structure", {})
        report.append("BODY STRUCTURE")
        report.append("-" * 20)
        report.append(f"Torso: {body_structure.get('torso', 'Not described')}")
        report.append(f"Arms/Hands: {body_structure.get('arms_hands', 'Not described')}")
        report.append(f"Legs/Feet: {body_structure.get('legs_feet', 'Not described')}")
        report.append(f"Tail: {body_structure.get('tail', 'Not applicable')}")
        report.append(f"Wings: {body_structure.get('wings', 'Not applicable')}")
        report.append(f"Other Appendages: {body_structure.get('other_appendages', 'None')}")
        report.append("")
        
        # Distinctive Features
        distinctive_features = phys_desc.get("distinctive_features", [])
        fixed_elements = phys_desc.get("fixed_elements", [])
        report.append("DISTINCTIVE FEATURES & FIXED ELEMENTS")
        report.append("-" * 40)
        report.append("Distinctive Features:")
        for feature in distinctive_features:
            report.append(f"  • {feature}")
        report.append("Fixed Elements (Always Present):")
        for element in fixed_elements:
            report.append(f"  • {element}")
        report.append("")
        
        # Clothing and Accessories
        clothing = character_data.get("clothing_accessories", {})
        if clothing:
            report.append("CLOTHING AND ACCESSORIES")
            report.append("-" * 30)
            regular_outfit = clothing.get("regular_outfit", {})
            report.append("Regular Outfit:")
            report.append(f"  Upper Body: {regular_outfit.get('upper_body', 'Not specified')}")
            report.append(f"  Lower Body: {regular_outfit.get('lower_body', 'Not specified')}")
            report.append(f"  Footwear: {regular_outfit.get('footwear', 'Not specified')}")
            report.append(f"  Style: {regular_outfit.get('style', 'Not specified')}")
            
            accessories = clothing.get("accessories", {})
            report.append("Accessories:")
            report.append(f"  Jewelry: {accessories.get('jewelry', 'None')}")
            report.append(f"  Functional Items: {accessories.get('functional_items', 'None')}")
            report.append(f"  Decorative Items: {accessories.get('decorative_items', 'None')}")
            report.append(f"  Special Items: {accessories.get('special_items', 'None')}")
            report.append("")
        
        # Personality and Psychology
        personality = character_data.get("personality_psychology", {})
        if personality:
            report.append("PERSONALITY AND PSYCHOLOGY")
            report.append("-" * 35)
            
            core_traits = personality.get("core_personality_traits", [])
            report.append("Core Personality Traits:")
            for trait in core_traits:
                report.append(f"  • {trait}")
            
            emotional_chars = personality.get("emotional_characteristics", {})
            report.append("Emotional Characteristics:")
            report.append(f"  Dominant Emotions: {', '.join(emotional_chars.get('dominant_emotions', []))}")
            report.append(f"  Emotional Range: {emotional_chars.get('emotional_range', 'Not described')}")
            report.append(f"  Emotional Expression: {emotional_chars.get('emotional_expression', 'Not described')}")
            
            motivations = personality.get("motivations_values", {})
            report.append("Motivations and Values:")
            report.append(f"  Primary Motivations: {motivations.get('primary_motivations', 'Not described')}")
            report.append(f"  Core Values: {motivations.get('core_values', 'Not described')}")
            report.append(f"  Aspirations: {motivations.get('aspirations', 'Not described')}")
            report.append("")
        
        # Background Context
        background = character_data.get("background_context", {})
        if background:
            report.append("BACKGROUND CONTEXT")
            report.append("-" * 25)
            report.append(f"Origin Story: {background.get('origin_story', 'Not provided')}")
            report.append(f"Current Living Situation: {background.get('current_living_situation', 'Not described')}")
            report.append(f"Cultural Background: {background.get('cultural_background', 'Not specified')}")
            report.append(f"Significant Relationships: {background.get('significant_relationships', 'Not described')}")
            report.append("")
        
        # Behavioral Patterns
        behavioral = character_data.get("behavioral_patterns", {})
        if behavioral:
            report.append("BEHAVIORAL PATTERNS")
            report.append("-" * 25)
            report.append(f"Daily Routines: {behavioral.get('daily_routines', 'Not described')}")
            report.append(f"Hobbies/Interests: {behavioral.get('hobbies_interests', 'Not specified')}")
            report.append(f"Skills/Talents: {behavioral.get('skills_talents', 'Not described')}")
            report.append(f"Quirks/Habits: {behavioral.get('quirks_habits', 'Not described')}")
            report.append(f"Comfort Items: {behavioral.get('comfort_items', 'None specified')}")
            report.append("")
        
        # Voice and Communication
        voice = character_data.get("voice_communication", {})
        if voice:
            report.append("VOICE AND COMMUNICATION")
            report.append("-" * 30)
            report.append(f"Speaking Voice: {voice.get('speaking_voice', 'Not described')}")
            report.append(f"Vocabulary Style: {voice.get('vocabulary_style', 'Not described')}")
            report.append(f"Catchphrases: {voice.get('catchphrases', 'None')}")
            report.append(f"Laugh Type: {voice.get('laugh_type', 'Not described')}")
            report.append("")
        
        # Story Role Dynamics
        story_role = character_data.get("story_role_dynamics", {})
        if story_role:
            report.append("STORY ROLE DYNAMICS")
            report.append("-" * 25)
            report.append(f"Narrative Function: {story_role.get('narrative_function', 'Not defined')}")
            report.append(f"Character Arc Potential: {story_role.get('character_arc_potential', 'Not described')}")
            report.append(f"Relationship Dynamics: {story_role.get('relationship_dynamics', 'Not described')}")
            report.append(f"Symbolic Meaning: {story_role.get('symbolic_meaning', 'Not defined')}")
            report.append("")
        
        # Style Information
        style_anchors = character_data.get("style_anchors", [])
        report.append("VISUAL STYLE INFORMATION")
        report.append("-" * 30)
        report.append("Style Anchors:")
        for anchor in style_anchors:
            report.append(f"  • {anchor}")
        report.append(f"Visual Style Notes: {character_data.get('visual_style_notes', 'Not provided')}")
        report.append("")
        
        report.append("=" * 60)
        report.append("END OF CHARACTER ANALYSIS")
        report.append("=" * 60)
        
        return "\n".join(report)

