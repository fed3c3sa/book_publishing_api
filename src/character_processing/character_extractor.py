"""
Character processing module for the Children's Book Generator.

This module handles character description extraction from text descriptions
or uploaded images, creating structured character data for consistent use
throughout the book generation process.
"""

import json
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from ..ai_clients.gemini_client import GeminiClient
from ..utils.config import load_prompt, get_output_path, CHARACTERS_DIR


class CharacterProcessor:
    """Handles character description extraction and processing."""
    
    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        """
        Initialize the character processor.
        
        Args:
            gemini_client: Gemini client instance. If None, creates a new one.
        """
        self.gemini_client = gemini_client or GeminiClient()
        self.character_prompt = load_prompt("character_description")
    
    def extract_character_from_text(
        self,
        character_description: str,
        character_name: str = "",
        character_type: str = "main"
    ) -> Dict[str, Any]:
        """
        Create a simple character structure from user text description without AI expansion.
        
        Args:
            character_description: Text description of the character
            character_name: Optional character name
            character_type: Type of character (main, secondary, background)
            
        Returns:
            Simple character description dictionary preserving original text
        """
        # Use the original user description without AI expansion
        print(f"🔄 Creating character from user text (preserving original description)...")
        
        # Create a simple character structure that preserves the user's original text
        character_data = self._create_simple_character_structure(
            character_name=character_name or "Unnamed Character",
            character_type=character_type,
            original_description=character_description
        )
        
        print(f"✅ Character created with original description preserved")
        return character_data
    
    def _create_simple_character_structure(
        self,
        character_name: str,
        character_type: str,
        original_description: str
    ) -> Dict[str, Any]:
        """
        Create a simple character structure that preserves the original user description.
        
        Args:
            character_name: Name of the character
            character_type: Type of character (main, secondary, background)
            original_description: The original user-provided description
            
        Returns:
            Simple character structure dictionary
        """
        # Create a minimal structure that preserves the original description
        # This bypasses AI expansion and keeps the user's exact words
        return {
            "character_name": character_name,
            "character_type": character_type,
            "species": "character",  # Generic species
            "age_category": "child",  # Default for children's books
            "gender_presentation": "neutral",  # Neutral default
            "ideogram_character_seed": f"{character_name}, {original_description[:100]}",  # Use original text for consistency
            "original_user_description": original_description,  # Preserve the exact user input
            "consistency_formula": f"{character_name} as described: {original_description[:50]}...",
            
            # Minimal physical description that references the original
            "physical_description": {
                "overall_impression": original_description,  # Use the user's exact words
                "size": "medium",
                "build_physique": "as described by user",
                "height_weight": "appropriate for story",
                "exact_colors": {
                    "primary": "as described",
                    "secondary": "",
                    "accent": "",
                    "details": "",
                    "seasonal_variations": ""
                },
                "head_face": {
                    "head_shape": "as described",
                    "facial_structure": {
                        "eyes": "as described",
                        "nose": "as described", 
                        "mouth": "as described",
                        "cheeks": "as described",
                        "chin": "as described",
                        "forehead": "as described"
                    },
                    "hair_fur_covering": {
                        "type": "as described",
                        "color": "as described",
                        "texture": "as described",
                        "length": "as described",
                        "style": "as described",
                        "special_features": ""
                    },
                    "ears": "as described",
                    "other_facial_features": ""
                },
                "body_structure": {
                    "torso": "as described",
                    "arms_hands": "as described",
                    "legs_feet": "as described",
                    "tail": "as described if any",
                    "wings": "as described if any",
                    "other_appendages": "as described if any"
                },
                "skin_surface": {
                    "texture": "as described",
                    "patterns": "as described",
                    "markings": "as described",
                    "special_properties": ""
                },
                "distinctive_features": [original_description],  # The whole description is the distinctive feature
                "fixed_elements": ["user-defined character"],
                "proportions": "as described by user",
                "mobility_posture": {
                    "typical_posture": "as described",
                    "gait": "as described",
                    "gesture_patterns": "as described",
                    "flexibility": "normal"
                }
            },
            
            # Additional structure to maintain compatibility
            "personality_psychology": {
                "core_personality_traits": [original_description],
                "emotional_characteristics": {
                    "dominant_emotions": ["as described"],
                    "emotional_range": "as described",
                    "emotional_triggers": "as described",
                    "emotional_expression": "as described"
                },
                "social_behavior": {
                    "social_preference": "as described",
                    "leadership_style": "as described",
                    "conflict_resolution": "as described",
                    "communication_style": "as described"
                },
                "cognitive_traits": {
                    "intelligence_type": "as described",
                    "learning_style": "as described",
                    "problem_solving": "as described",
                    "creativity_level": "as described"
                },
                "motivations_values": {
                    "core_values": ["as described"],
                    "life_goals": "as described",
                    "fears_concerns": "as described",
                    "what_drives_them": "as described"
                }
            },
            
            "behavior_source": "user_description",  # Flag to indicate this is user-provided
            "ai_expanded": False  # Flag to indicate this was NOT AI-expanded
        }
    
    # Simplified approach: we no longer expand characters from images via AI.
    # If needed later, this method can be reintroduced.
    def extract_character_from_image(self, *args, **kwargs):
        raise NotImplementedError("Image-based character extraction has been removed in simplified flow.")
    
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
                    # Simplified: create character from provided text info without AI
                    description = additional_desc or f"Character inferred from uploaded image(s)"
                    character_data = self.extract_character_from_text(
                        character_description=description,
                        character_name=name,
                        character_type=char_type
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
    
    # Heavy validation removed for simplified approach
    def validate_character_data(self, character_data: Dict[str, Any]) -> bool:
        required = ["character_name", "character_type", "ideogram_character_seed"]
        for k in required:
            if not character_data.get(k):
                print(f"Missing required field: {k}")
                return False
        return True
    
    # Legacy conversion removed in simplified approach
    def convert_old_format_to_new(self, old_character_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Legacy character conversion removed in simplified flow.")
    
    def upgrade_character_file(self, filename: str) -> Dict[str, Any]:
        raise NotImplementedError("Character file upgrade removed in simplified flow.")
    
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
    
    # Reporting removed in simplified approach
    def generate_character_analysis_report(self, character_data: Dict[str, Any]) -> str:
        raise NotImplementedError("Character analysis report removed in simplified flow.")

