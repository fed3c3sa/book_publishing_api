"""Character processing utilities for book creation."""

import logging
from typing import Dict, Any, List, Optional

from data_models.character import Character

logger = logging.getLogger(__name__)


class CharacterProcessor:
    """Handles character description processing and analysis."""
    
    def __init__(self, config: Dict[str, Any], llm_model, image_description_agent=None):
        """Initialize the character processor."""
        self.config = config
        self.llm_model = llm_model
        self.image_description_agent = image_description_agent
        
    def process_existing_characters(self, characters: List[Character]) -> List[Character]:
        """
        Process existing character list, enhancing descriptions if needed.
        
        Args:
            characters: List of existing Character objects
            
        Returns:
            List of processed characters
        """
        try:
            logger.info(f"Processing {len(characters)} existing characters")
            processed_characters = []
            
            for character in characters:
                try:
                    # Validate character
                    if not character.name or not character.description:
                        logger.warning(f"Skipping invalid character: {character}")
                        continue
                        
                    # Enhance description if needed
                    enhanced_character = self._enhance_character(character)
                    processed_characters.append(enhanced_character)
                    
                    logger.debug(f"Processed character: {character.name}")
                    
                except Exception as e:
                    logger.warning(f"Failed to process character {character.name}: {e}")
                    # Include original character if enhancement fails
                    processed_characters.append(character)
                    
            logger.info(f"Successfully processed {len(processed_characters)} characters")
            return processed_characters
            
        except Exception as e:
            logger.error(f"Character processing failed: {e}")
            return characters  # Return original list on failure
            
    def process_characters_from_config(self) -> List[Character]:
        """
        Process character descriptions from configuration.
        
        Returns:
            List of processed Character objects
        """
        character_data_list = self.config.get("characters", [])
        
        if not character_data_list:
            logger.info("No character descriptions found in configuration")
            return []
            
        logger.info(f"Processing {len(character_data_list)} characters from configuration")
        
        characters = []
        for i, char_data in enumerate(character_data_list):
            try:
                character = self._create_character_from_config(char_data, i)
                if character:
                    characters.append(character)
                    
            except Exception as e:
                logger.warning(f"Failed to create character {i+1}: {e}")
                continue
                
        logger.info(f"Successfully created {len(characters)} characters from configuration")
        return characters
        
    def _create_character_from_config(self, char_data: Dict[str, Any], index: int) -> Optional[Character]:
        """
        Create a character object from configuration data.
        
        Args:
            char_data: Character data from configuration
            index: Character index for default naming
            
        Returns:
            Character object or None if creation fails
        """
        try:
            char_name = char_data.get("name", f"Character_{index+1}")
            char_role = char_data.get("role", "main")
            char_description = char_data.get("description", "")
            image_source = char_data.get("image_source", "text")
            
            logger.debug(f"Creating character: {char_name} (source: {image_source})")
            
            # Process image-based character if needed
            if image_source == "image" and self.image_description_agent and "image_data" in char_data:
                char_description = self._analyze_character_image(
                    char_data["image_data"], 
                    char_name
                )
                
            # Validate description
            if not char_description or not char_description.strip():
                char_description = f"A distinctive character named {char_name} with unique visual features that make them memorable and engaging for readers."
                logger.warning(f"Using fallback description for {char_name}")
                
            # Create Character object
            character = Character(
                name=char_name,
                description=char_description,
                role=char_role,
                image_source=image_source
            )
            
            logger.debug(f"Character '{char_name}' created successfully")
            return character
            
        except Exception as e:
            logger.error(f"Failed to create character from config: {e}")
            return None
            
    def _analyze_character_image(self, image_data: Any, character_name: str) -> str:
        """
        Analyze character image to generate description.
        
        Args:
            image_data: Image data for analysis
            character_name: Name of the character
            
        Returns:
            Generated character description
        """
        if not self.image_description_agent:
            logger.warning("Image description agent not available")
            return f"A character named {character_name} with distinctive visual features."
            
        try:
            logger.info(f"Analyzing uploaded image for character: {character_name}")
            
            # Analyze the image
            analyzed_description = self.image_description_agent.analyze_character_image(
                image_data=image_data,
                character_name=character_name
            )
            
            # Enhance with story context
            story_context = f"Book idea: {self.config.get('user_book_idea', 'General story')}"
            enhanced_description = self.image_description_agent.enhance_character_description(
                basic_description=analyzed_description,
                character_name=character_name,
                story_context=story_context
            )
            
            logger.info(f"Generated description for {character_name} from image analysis")
            return enhanced_description
            
        except Exception as e:
            logger.error(f"Image analysis failed for {character_name}: {e}")
            return f"A distinctive character named {character_name} with unique visual features that make them memorable and engaging for readers."
            
    def _enhance_character(self, character: Character) -> Character:
        """
        Enhance a character's description if needed.
        
        Args:
            character: Original character object
            
        Returns:
            Enhanced character object
        """
        # For now, just return the original character
        # In the future, this could include AI-based enhancement
        return character
        
    def validate_characters(self, characters: List[Character]) -> List[Character]:
        """
        Validate and filter character list.
        
        Args:
            characters: List of characters to validate
            
        Returns:
            List of valid characters
        """
        valid_characters = []
        
        for character in characters:
            try:
                # Basic validation
                if not character.name or not character.name.strip():
                    logger.warning("Skipping character with empty name")
                    continue
                    
                if not character.description or not character.description.strip():
                    logger.warning(f"Skipping character {character.name} with empty description")
                    continue
                    
                # Ensure valid role
                if character.role not in ["main", "secondary", "background"]:
                    character.role = "main"
                    logger.warning(f"Fixed invalid role for character {character.name}")
                    
                valid_characters.append(character)
                
            except Exception as e:
                logger.warning(f"Character validation failed for {getattr(character, 'name', 'unknown')}: {e}")
                continue
                
        logger.info(f"Validated {len(valid_characters)} out of {len(characters)} characters")
        return valid_characters 