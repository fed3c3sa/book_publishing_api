"""
Character processing service implementation.

This service handles simple character processing using frontend input directly
without AI expansion or complex processing.
"""

import json
from typing import List
from pathlib import Path

from ..interfaces.character_service_interface import CharacterServiceInterface
from ..domain.models import Character, CharacterInput, InputType
from ..exceptions import (
    CharacterProcessingError,
    CharacterValidationError,
    CharacterNotFoundError,
)
from ..utils.config import CHARACTERS_DIR, get_output_path


class CharacterService(CharacterServiceInterface):
    """
    Character processing service implementation.
    
    This service creates basic character structures from frontend input
    without AI processing or expansion.
    """
    
    def __init__(self):
        """Initialize the character service - no AI processing needed."""
        pass
    
    def process_character_input(self, character_input: CharacterInput) -> Character:
        """
        Process a single character input and return a complete Character model.
        
        Args:
            character_input: Input data for character processing
            
        Returns:
            Complete Character model
            
        Raises:
            CharacterProcessingError: If processing fails
        """
        try:
            if character_input.type == InputType.TEXT:
                return self._process_text_character(character_input)
            elif character_input.type == InputType.IMAGE:
                return self._process_image_character(character_input)
            else:
                # Handle both enum and string values for input type
                input_type_str = character_input.type.value if hasattr(character_input.type, 'value') else str(character_input.type)
                raise CharacterProcessingError(
                    f"Unsupported input type: {character_input.type}",
                    character_name=character_input.name,
                    input_type=input_type_str
                )
                
        except Exception as e:
            if isinstance(e, CharacterProcessingError):
                raise
            
            # Handle both enum and string values for input type
            input_type_str = character_input.type.value if hasattr(character_input.type, 'value') else str(character_input.type)
            raise CharacterProcessingError(
                f"Failed to process character '{character_input.name}': {str(e)}",
                character_name=character_input.name,
                input_type=input_type_str
            )
    
    def _process_text_character(self, character_input: CharacterInput) -> Character:
        """Process character from text description - just use frontend input as-is."""
        if not isinstance(character_input.content, str):
            raise CharacterProcessingError(
                "Text input must be a string",
                character_name=character_input.name
            )
        
        # Simply create a basic character structure using frontend input directly
        return Character(
            character_name=character_input.name or "Unnamed Character",
            character_type=character_input.character_type,
            species="character",
            age_category="child",
            gender_presentation="neutral",
            ideogram_character_seed=f"{character_input.name}, {character_input.content}",
            physical_description=self._create_minimal_physical_description(character_input.content),
            clothing_accessories=self._create_minimal_clothing(),
            personality_psychology=self._create_minimal_personality(character_input.content),
            background_context=self._create_minimal_background(),
            behavioral_patterns=self._create_minimal_behavior(),
            voice_communication=self._create_minimal_voice(),
            story_role_dynamics=self._create_minimal_story_role(character_input.character_type),
            consistency_formula=f"{character_input.name}: {character_input.content}",
            style_anchors=["children's book illustration", "friendly", "colorful"],
            visual_style_notes="child-friendly illustration style",
            ai_expanded=False,
            behavior_source="user_input",
            original_user_description=character_input.content
        )
    
    def _process_image_character(self, character_input: CharacterInput) -> Character:
        """Process character from image(s) - just use frontend input as-is."""
        if not isinstance(character_input.content, list):
            image_paths = [character_input.content]
        else:
            image_paths = character_input.content
        
        # Basic validation that files exist
        for path in image_paths:
            if not Path(path).exists():
                raise CharacterProcessingError(
                    f"Image file not found: {path}",
                    character_name=character_input.name
                )
        
        # Create basic character using image path and any additional description
        description = character_input.additional_description or f"Character from image: {', '.join(image_paths)}"
        
        return Character(
            character_name=character_input.name or "Unnamed Character",
            character_type=character_input.character_type,
            species="character", 
            age_category="child",
            gender_presentation="neutral",
            ideogram_character_seed=f"{character_input.name}, character from uploaded image",
            physical_description=self._create_minimal_physical_description(description),
            clothing_accessories=self._create_minimal_clothing(),
            personality_psychology=self._create_minimal_personality(description),
            background_context=self._create_minimal_background(),
            behavioral_patterns=self._create_minimal_behavior(),
            voice_communication=self._create_minimal_voice(),
            story_role_dynamics=self._create_minimal_story_role(character_input.character_type),
            consistency_formula=f"{character_input.name}: character from uploaded image",
            style_anchors=["children's book illustration", "friendly", "colorful"],
            visual_style_notes="child-friendly illustration style",
            ai_expanded=False,
            behavior_source="user_input",
            original_user_description=description
        )
    
    def _create_minimal_physical_description(self, description: str):
        """Create minimal physical description."""
        from ..domain.models import (
            PhysicalDescription, ExactColors, HeadFace, FacialStructure,
            HairFurCovering, BodyStructure, SkinSurface, MobilityPosture
        )
        
        return PhysicalDescription(
            overall_impression=description,
            size="medium",
            build_physique="friendly character",
            height_weight="appropriate for children's book",
            exact_colors=ExactColors(
                primary="colorful", secondary="", accent="", details="", seasonal_variations=""
            ),
            head_face=HeadFace(
                head_shape="friendly",
                facial_structure=FacialStructure(
                    eyes="expressive", nose="cute", mouth="smiling", 
                    cheeks="rosy", chin="gentle", forehead="smooth"
                ),
                hair_fur_covering=HairFurCovering(
                    type="hair", color="natural", texture="soft", 
                    length="medium", style="neat", special_features=""
                ),
                ears="normal", other_facial_features=""
            ),
            body_structure=BodyStructure(
                torso="proportionate", arms_hands="expressive", legs_feet="steady",
                tail="none", wings="none", other_appendages="none"
            ),
            skin_surface=SkinSurface(
                texture="smooth", patterns="none", markings="none", special_properties=""
            ),
            distinctive_features=[description],
            fixed_elements=["friendly appearance"],
            proportions="child-friendly proportions",
            mobility_posture=MobilityPosture(
                typical_posture="confident", gait="cheerful", 
                gesture_patterns="animated", flexibility="good"
            )
        )
    
    def _create_minimal_clothing(self):
        """Create minimal clothing description."""
        from ..domain.models import ClothingAccessories, RegularOutfit, Accessories
        
        return ClothingAccessories(
            regular_outfit=RegularOutfit(
                upper_body="comfortable shirt", lower_body="casual pants",
                footwear="appropriate shoes", undergarments="standard", style="casual"
            ),
            accessories=Accessories(
                jewelry="", functional_items="", decorative_items="", special_items=""
            ),
            seasonal_alternate_outfits="weather appropriate",
            clothing_preferences="comfort and practicality"
        )
    
    def _create_minimal_personality(self, description: str):
        """Create minimal personality."""
        from ..domain.models import (
            PersonalityPsychology, EmotionalCharacteristics, SocialBehavior,
            CognitiveTraits, MotivationsValues
        )
        
        return PersonalityPsychology(
            core_personality_traits=["friendly", "curious", "kind"],
            emotional_characteristics=EmotionalCharacteristics(
                dominant_emotions=["happy", "excited"], emotional_range="full spectrum",
                emotional_triggers="story events", emotional_expression="open"
            ),
            social_behavior=SocialBehavior(
                interaction_style="friendly", communication_pattern="clear",
                relationship_approach="trusting", conflict_resolution="peaceful"
            ),
            cognitive_traits=CognitiveTraits(
                intelligence_type="creative", learning_style="visual",
                problem_solving="intuitive", attention_span="good"
            ),
            motivations_values=MotivationsValues(
                primary_motivations="adventure and friendship", core_values="kindness",
                fears_concerns="age-appropriate", aspirations="growth"
            )
        )
    
    def _create_minimal_background(self):
        """Create minimal background."""
        from ..domain.models import BackgroundContext
        
        return BackgroundContext(
            origin_story="loving family", current_living_situation="happy home",
            social_economic_status="comfortable", cultural_background="inclusive",
            education_experience="learning", significant_relationships="family and friends",
            life_experiences="typical childhood"
        )
    
    def _create_minimal_behavior(self):
        """Create minimal behavior patterns."""
        from ..domain.models import BehavioralPatterns
        
        return BehavioralPatterns(
            daily_routines="balanced", hobbies_interests="age-appropriate activities",
            skills_talents="natural abilities", quirks_habits="endearing habits",
            reaction_patterns="thoughtful", comfort_items="favorite toy"
        )
    
    def _create_minimal_voice(self):
        """Create minimal voice communication."""
        from ..domain.models import VoiceCommunication
        
        return VoiceCommunication(
            speaking_voice="clear and cheerful", vocabulary_style="age-appropriate",
            catchphrases="", non_verbal_communication="expressive gestures",
            laugh_type="joyful", crying_expression="when sad"
        )
    
    def _create_minimal_story_role(self, character_type):
        """Create minimal story role."""
        from ..domain.models import StoryRoleDynamics
        
        # Handle both enum and string values for character type
        char_type_str = character_type.value if hasattr(character_type, 'value') else str(character_type)
        return StoryRoleDynamics(
            narrative_function=f"{char_type_str} character",
            character_arc_potential="growth through story",
            relationship_dynamics="forms connections",
            conflict_sources="story challenges",
            symbolic_meaning="childhood wonder"
        )
    
    def process_multiple_characters(self, character_inputs: List[CharacterInput]) -> List[Character]:
        """
        Process multiple character inputs.
        
        Args:
            character_inputs: List of character input data
            
        Returns:
            List of processed Character models
        """
        characters = []
        
        for character_input in character_inputs:
            try:
                character = self.process_character_input(character_input)
                
                # Save character
                saved_path = self.save_character(character)
                
                # Add saved path to metadata (not part of the model)
                character_dict = character.dict()
                character_dict["_saved_path"] = str(saved_path)
                
                characters.append(character)
                
            except CharacterProcessingError:
                # Re-raise character processing errors
                raise
            except Exception as e:
                # Continue with other characters on unexpected errors
                print(f"Error processing character '{character_input.name}': {str(e)}")
                continue
        
        return characters
    
    def save_character(self, character: Character, filename: str = None) -> Path:
        """
        Save character to file.
        
        Args:
            character: Character model to save
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        if filename is None:
            char_name = character.character_name
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
            json.dump(character.dict(), f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def load_character(self, filename: str) -> Character:
        """
        Load character from file.
        
        Args:
            filename: Name of character file
            
        Returns:
            Character model
            
        Raises:
            CharacterNotFoundError: If file is not found
        """
        file_path = CHARACTERS_DIR / filename
        if not file_path.exists():
            raise CharacterNotFoundError(
                f"Character file not found: {file_path}",
                character_name=filename
            )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
            
            return Character(**character_data)
            
        except Exception as e:
            raise CharacterProcessingError(
                f"Failed to load character from {file_path}: {str(e)}",
                character_name=filename
            )
    
    def validate_character(self, character: Character) -> bool:
        """
        Validate character data completeness.
        
        Args:
            character: Character to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Pydantic validation happens automatically when creating Character model
            # Additional business logic validation can be added here
            
            # Basic validation checks
            if not character.character_name.strip():
                return False
            
            if not character.ideogram_character_seed.strip():
                return False
            
            if not character.consistency_formula.strip():
                return False
            
            return True
            
        except Exception:
            return False