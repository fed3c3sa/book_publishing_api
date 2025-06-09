"""
OpenAI GPT-4o integration module for the Children's Book Generator.

This module provides a client for interacting with OpenAI's GPT-4o model
for text generation, character description, and book planning.
"""

import json
import base64
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import openai
from openai import OpenAI

from ..utils.config import load_config


class OpenAIClient:
    """Client for interacting with OpenAI GPT-4o API."""
    
    def __init__(self, config: Optional[Dict[str, str]] = None):
        """
        Initialize the OpenAI client.
        
        Args:
            config: Configuration dictionary. If None, loads from environment.
        """
        if config is None:
            config = load_config()
        
        # Get organization ID, but skip if it's empty or placeholder
        org_id = config.get("openai_org_id")
        if org_id and org_id.strip() and org_id.strip() != "your_openai_org_id_here":
            org_id = org_id.strip()
        else:
            org_id = None
        
        self.client = OpenAI(
            api_key=config["openai_api_key"],
            organization=org_id
        )
        
        # Default model configuration
        self.model = "gpt-4o"
        self.max_tokens = 4000
        self.temperature = 0.7
    
    def encode_image(self, image_path: Union[str, Path]) -> str:
        """
        Encode an image to base64 for API submission.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image string
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def create_completion(
        self,
        prompt: str,
        system_message: str = "You are a helpful assistant.",
        images: Optional[List[Union[str, Path]]] = None,
        force_json: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Create a completion using GPT-4o.
        
        Args:
            prompt: The user prompt
            system_message: System message to set context
            images: List of image paths to include in the request
            force_json: Whether to force JSON output format
            temperature: Temperature for generation (overrides default)
            max_tokens: Max tokens for generation (overrides default)
            
        Returns:
            Generated text response
        """
        # Prepare messages
        messages = [
            {"role": "system", "content": system_message}
        ]
        
        # Prepare user message content
        user_content = [{"type": "text", "text": prompt}]
        
        # Add images if provided
        if images:
            for image_path in images:
                # Determine image format
                image_path = Path(image_path)
                if image_path.suffix.lower() in ['.jpg', '.jpeg']:
                    media_type = "image/jpeg"
                elif image_path.suffix.lower() == '.png':
                    media_type = "image/png"
                elif image_path.suffix.lower() == '.webp':
                    media_type = "image/webp"
                else:
                    raise ValueError(f"Unsupported image format: {image_path.suffix}")
                
                # Encode image
                base64_image = self.encode_image(image_path)
                
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{media_type};base64,{base64_image}"
                    }
                })
        
        messages.append({"role": "user", "content": user_content})
        
        # Prepare request parameters
        request_params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.max_tokens
        }
        
        # Force JSON output if requested
        if force_json:
            request_params["response_format"] = {"type": "json_object"}
        
        try:
            response = self.client.chat.completions.create(**request_params)
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def extract_character_description(
        self,
        input_content: str,
        images: Optional[List[Union[str, Path]]] = None,
        prompt_template: str = ""
    ) -> Dict[str, Any]:
        """
        Extract structured character description from text or images.
        
        Args:
            input_content: Text description of the character
            images: List of character images to analyze
            prompt_template: Custom prompt template to use
            
        Returns:
            Structured character description as dictionary
        """
        # Use different comprehensive approaches for images vs text
        if images:
            # Two-step approach for images: First get detailed visual analysis, then expand to comprehensive format
            character_name = "Unknown Character"
            if "name is" in input_content.lower():
                parts = input_content.lower().split("name is")
                if len(parts) > 1:
                    name_part = parts[1].strip().rstrip('.').strip()
                    if name_part:
                        character_name = name_part.title()
            elif input_content.strip():
                words = input_content.strip().split()
                if len(words) > 0 and words[0].istitle():
                    character_name = words[0]
            
            # Step 1: Get detailed visual analysis (simpler prompt that works with images)
            visual_analysis_prompt = f"""Analyze this image and provide a detailed visual description for character "{character_name}".

Focus on being extremely specific about visual details for consistent image generation:

Describe in detail:
- Exact hair color, style, length, texture (be very specific)
- Precise eye color, shape, expression, eyebrows
- Exact skin tone and any visible markings
- Detailed clothing description including colors, materials, fit, style
- Any jewelry or accessories with specific descriptions
- Body proportions, posture, and build
- Facial features: nose shape, mouth, cheeks, chin, forehead
- Overall style impression and vibe
- Any distinctive features that make this person unique

Be as specific as possible about colors (not just "blue" but "deep ocean blue" or "bright sky blue").
Describe proportions and sizes precisely.
Include clothing textures and materials if visible.

Write a comprehensive visual description that an artist could use to draw this character identically."""
            
            print("🔄 Step 1: Getting detailed visual analysis...")
            visual_description = self.create_completion(
                prompt=visual_analysis_prompt,
                system_message="You are an expert character designer analyzing images for consistent reproduction. Be extremely detailed and specific.",
                images=images,
                force_json=False,  # Get text description first
                temperature=0.2
            )
            
            if not visual_description:
                print("Warning: Failed to get visual analysis from image")
                return self._create_fallback_character_data(input_content, images)
            
            print("✅ Step 1 completed: Visual analysis obtained")
            print("🔄 Step 2: Converting to comprehensive character format...")
            
            # Step 2: Convert visual analysis to comprehensive character format
            comprehensive_prompt = f"""You are an expert character designer. Convert this detailed visual description into a comprehensive character profile in JSON format.

Character name: {character_name}
Visual description from image analysis: {visual_description}

Create a complete character description using this exact JSON structure:

{{
  "character_name": "{character_name}",
  "character_type": "main",
  "species": "human",
  "age_category": "determine from description",
  "gender_presentation": "determine from description",
  
  "ideogram_character_seed": "comprehensive description for visual consistency",
  
  "physical_description": {{
    "overall_impression": "extract from visual description",
    "size": "determine size/build from description",
    "build_physique": "extract body type and posture details",
    "height_weight": "describe proportions mentioned",
    
    "exact_colors": {{
      "primary": "most dominant color mentioned",
      "secondary": "second most prominent color",
      "accent": "accent colors for details",
      "details": "specific color placements mentioned",
      "seasonal_variations": "none unless mentioned"
    }},
    
    "head_face": {{
      "head_shape": "extract from facial description",
      "facial_structure": {{
        "eyes": "extract eye details from description",
        "nose": "extract nose details",
        "mouth": "extract mouth details",
        "cheeks": "extract cheek details",
        "chin": "extract chin details",
        "forehead": "extract forehead details"
      }},
      "hair_fur_covering": {{
        "type": "hair",
        "color": "extract exact hair color",
        "texture": "extract hair texture",
        "length": "extract hair length",
        "style": "extract hair style",
        "special_features": "any unique hair features mentioned"
      }},
      "ears": "extract ear details if mentioned",
      "other_facial_features": "any other facial features mentioned"
    }},
    
    "body_structure": {{
      "torso": "extract torso details",
      "arms_hands": "extract arm/hand details",
      "legs_feet": "extract leg/foot details",
      "tail": "none",
      "wings": "none",
      "other_appendages": "none unless mentioned"
    }},
    
    "skin_surface": {{
      "texture": "extract skin texture details",
      "patterns": "any patterns mentioned",
      "markings": "any markings mentioned",
      "special_properties": "any special characteristics"
    }},
    
    "distinctive_features": ["list unique features that make character recognizable"],
    "fixed_elements": ["elements that must always be present"],
    "proportions": "extract proportion details from description",
    
    "mobility_posture": {{
      "typical_posture": "extract posture from description",
      "gait": "infer movement style",
      "gesture_patterns": "infer from pose",
      "flexibility": "infer from appearance"
    }}
  }},
  
  "clothing_accessories": {{
    "regular_outfit": {{
      "upper_body": "extract upper clothing details",
      "lower_body": "extract lower clothing details",
      "footwear": "extract footwear or bare feet",
      "undergarments": "appropriate undergarments",
      "style": "extract overall clothing style"
    }},
    "accessories": {{
      "jewelry": "extract jewelry details",
      "functional_items": "extract functional accessories",
      "decorative_items": "extract decorative items",
      "special_items": "any special accessories"
    }},
    "seasonal_alternate_outfits": "suggest variations based on current outfit",
    "clothing_preferences": "infer from current choices"
  }},
  
  "personality_psychology": {{
    "core_personality_traits": ["infer 4-6 traits from appearance and expression"],
    "emotional_characteristics": {{
      "dominant_emotions": ["emotions suggested by expression"],
      "emotional_range": "range suggested by expressiveness",
      "emotional_triggers": "age-appropriate triggers",
      "emotional_expression": "how they express emotions"
    }},
    "social_behavior": {{
      "interaction_style": "infer from approachability",
      "communication_pattern": "infer from expression",
      "relationship_approach": "infer from demeanor",
      "conflict_resolution": "age-appropriate resolution style"
    }},
    "cognitive_traits": {{
      "intelligence_type": "infer from expression and style",
      "learning_style": "infer preferred learning approach",
      "problem_solving": "infer approach from appearance",
      "attention_span": "age-appropriate attention span"
    }},
    "motivations_values": {{
      "primary_motivations": "age-appropriate motivations",
      "core_values": "values suggested by presentation",
      "fears_concerns": "age-appropriate concerns",
      "aspirations": "age-appropriate dreams"
    }}
  }},
  
  "background_context": {{
    "origin_story": "background suggested by appearance",
    "current_living_situation": "lifestyle suggested by grooming/clothing",
    "social_economic_status": "comfort level suggested by presentation",
    "cultural_background": "any cultural elements in styling",
    "education_experience": "education suggested by presentation",
    "significant_relationships": "relationships suggested by confidence level",
    "life_experiences": "experiences appropriate for apparent age"
  }},
  
  "behavioral_patterns": {{
    "daily_routines": "routines suggested by presentation",
    "hobbies_interests": "interests suggested by style choices",
    "skills_talents": "abilities suggested by confident appearance",
    "quirks_habits": "unique traits suggested by expression",
    "reaction_patterns": "response style suggested by demeanor",
    "comfort_items": "items that would provide comfort"
  }},
  
  "voice_communication": {{
    "speaking_voice": "voice type suggested by facial structure",
    "vocabulary_style": "communication style for age",
    "catchphrases": "expressions that would fit character",
    "non_verbal_communication": "gestures and expressions observed",
    "laugh_type": "laugh style suggested by expression",
    "crying_expression": "how they would express sadness"
  }},
  
  "story_role_dynamics": {{
    "narrative_function": "role suggested by confident/approachable appearance",
    "character_arc_potential": "growth potential for apparent age",
    "relationship_dynamics": "how they would interact with others",
    "conflict_sources": "age-appropriate challenges",
    "symbolic_meaning": "what this character represents"
  }},
  
  "consistency_formula": "precise formula for maintaining identical appearance across images",
  "style_anchors": ["art style keywords that work with this character"],
  "visual_style_notes": "optimal artistic approach for this character"
}}

Extract all details from the visual description and organize them into this comprehensive format. Be specific and detailed to ensure consistent image generation."""
            
            response = self.create_completion(
                prompt=comprehensive_prompt,
                system_message="You are an expert character designer creating detailed specifications for consistent image generation. Respond only with valid JSON.",
                force_json=True,
                temperature=0.3
            )
            
        else:
            # Enhanced text processing with expansion for specificity
            expansion_prompt = f"""You are an expert character designer for children's books. Analyze the provided text description and either use it as-is if it's comprehensive, or significantly expand it if it lacks specificity needed for consistent image generation.

CRITICAL: Character descriptions must be extremely specific for consistent image generation across multiple images. If the provided description is vague or lacks visual details, expand it significantly while staying true to the original concept.

Original text: {input_content}

If the text is already comprehensive and specific, use the standard comprehensive format. If it's too general or vague, first expand it with specific details, then structure it comprehensively.

{prompt_template.format(input_content=input_content)}

EXPANSION GUIDELINES when text lacks specificity:
- Add specific colors instead of general terms
- Define exact proportions and sizes  
- Specify clothing materials, textures, and exact fit
- Add distinctive features that make the character unique
- Include personality traits that connect to appearance
- Add background context that explains their look and style
- Specify exact facial features for consistent reproduction
- Include behavioral patterns that influence their presentation

Focus on creating a character description so detailed that an artist could draw the character identically multiple times."""
            
            response = self.create_completion(
                prompt=expansion_prompt,
                system_message="You are an expert character designer for children's books. Always respond with valid JSON. Expand vague descriptions to be highly specific for consistent image generation.",
                force_json=True,
                temperature=0.3
            )
        
        # Handle None response
        if response is None:
            print("Warning: OpenAI API returned None response")
            return self._create_fallback_character_data(input_content, images)
        
        try:
            character_data = json.loads(response)
            
            # Validate that we got a dictionary
            if not isinstance(character_data, dict):
                print(f"Warning: Expected dictionary, got {type(character_data)}")
                return self._create_fallback_character_data(input_content, images)
            
            print("✅ Step 2 completed: Comprehensive character format created")
            return character_data
            
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse character description JSON: {str(e)}")
            print(f"Raw response: {response}")
            return self._create_fallback_character_data(input_content, images)
        except Exception as e:
            print(f"Warning: Unexpected error in character extraction: {str(e)}")
            return self._create_fallback_character_data(input_content, images)
    
    def _create_fallback_character_data(
        self, 
        input_content: str, 
        images: Optional[List[Union[str, Path]]] = None
    ) -> Dict[str, Any]:
        """
        Create a basic character data structure as fallback when AI processing fails.
        
        Args:
            input_content: Original input content
            images: List of image paths if provided
            
        Returns:
            Basic character data dictionary
        """
        # Try to extract character name from input content
        character_name = "Unknown Character"
        
        # Look for character name in various patterns
        lines = input_content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith("Character Name:"):
                character_name = line.replace("Character Name:", "").strip()
                break
            elif line.startswith("The character's name is"):
                character_name = line.replace("The character's name is", "").strip().rstrip('.')
                break
            elif "name is" in line.lower():
                # Extract name after "name is"
                parts = line.lower().split("name is")
                if len(parts) > 1:
                    name_part = parts[1].strip().rstrip('.').strip()
                    if name_part:
                        character_name = name_part.title()
                        break
        
        # Create description based on whether we have images or text
        if images:
            description = f"A character from an uploaded image. {input_content[:150] if input_content else 'Visual appearance to be determined from image.'}"
        else:
            description = input_content[:200] if input_content else "A friendly character"
        
        # Create minimal character data structure
        return {
            "character_name": character_name,
            "character_type": "main",
            "species": "human",
            "age_category": "child",
            "gender_presentation": "neutral",
            "ideogram_character_seed": f"A friendly {character_name} character",
            "consistency_formula": f"Always draw {character_name} with consistent features",
            "physical_description": {
                "overall_impression": description,
                "size": "medium",
                "build_physique": {
                    "body_type": "average",
                    "fitness_level": "healthy",
                    "posture": "upright"
                },
                "height_weight": {
                    "height_description": "average height",
                    "weight_description": "healthy weight",
                    "proportions": "well-proportioned"
                },
                "exact_colors": {
                    "primary": {"color": "brown", "description": "warm brown"},
                    "secondary": {"color": "beige", "description": "light beige"},
                    "accent": {"color": "blue", "description": "bright blue"},
                    "details": {"color": "white", "description": "clean white"},
                    "seasonal_variations": "colors remain consistent"
                },
                "head_face": {
                    "head_shape": "oval",
                    "facial_structure": {
                        "eyes": "friendly round eyes",
                        "nose": "small nose",
                        "mouth": "gentle smile",
                        "cheeks": "rounded cheeks",
                        "chin": "soft chin",
                        "forehead": "smooth forehead"
                    },
                    "hair_fur_covering": {
                        "type": "hair",
                        "color": "brown",
                        "texture": "smooth",
                        "length": "medium",
                        "style": "neat",
                        "special_features": "none"
                    },
                    "ears": "normal human ears",
                    "other_facial_features": "expressive face"
                },
                "body_structure": {
                    "torso": "proportional torso",
                    "arms_hands": "normal arms and hands",
                    "legs_feet": "normal legs and feet",
                    "tail": "none",
                    "wings": "none",
                    "other_appendages": "none"
                },
                "skin_surface": {
                    "texture": "smooth",
                    "patterns": "none",
                    "markings": "none",
                    "special_properties": "normal skin"
                },
                "distinctive_features": "friendly appearance",
                "fixed_elements": "consistent facial features",
                "proportions": "well-balanced proportions",
                "mobility_posture": {
                    "typical_posture": "upright and confident",
                    "gait": "normal walking",
                    "gesture_patterns": "friendly gestures",
                    "flexibility": "normal flexibility"
                }
            }
        }
    
    def create_book_plan(
        self,
        story_idea: str,
        num_pages: int,
        age_group: str,
        language: str,
        characters: List[Dict[str, Any]],
        prompt_template: str = ""
    ) -> Dict[str, Any]:
        """
        Create a structured book plan.
        
        Args:
            story_idea: The main story concept
            num_pages: Number of pages for the book
            age_group: Target age group (e.g., "3-5", "6-8")
            language: Language for the book
            characters: List of character descriptions
            prompt_template: Custom prompt template to use
            
        Returns:
            Structured book plan as dictionary
        """
        # Format the prompt
        formatted_prompt = prompt_template.format(
            story_idea=story_idea,
            num_pages=num_pages,
            age_group=age_group,
            language=language,
            characters=json.dumps(characters, indent=2)
        )
        
        # Create completion
        response = self.create_completion(
            prompt=formatted_prompt,
            system_message="You are an expert children's book author and story planner. Always respond with valid JSON.",
            force_json=True,
            temperature=0.5
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse book plan JSON: {str(e)}")
    
    def generate_image_prompt(
        self,
        page_description: str,
        characters_present: List[str],
        character_descriptions: Dict[str, Any],
        mood_tone: str,
        visual_elements: List[str],
        art_style: str,
        prompt_template: str = ""
    ) -> Dict[str, Any]:
        """
        Generate a detailed prompt for image generation.
        
        Args:
            page_description: Description of what happens on the page
            characters_present: List of character names present
            character_descriptions: Full character description data
            mood_tone: Mood and tone for the scene
            visual_elements: List of visual elements to include
            art_style: Desired art style
            prompt_template: Custom prompt template to use
            
        Returns:
            Structured image prompt as dictionary
        """
        # Format the prompt
        formatted_prompt = prompt_template.format(
            page_description=page_description,
            characters_present=", ".join(characters_present),
            character_descriptions=json.dumps(character_descriptions, indent=2),
            mood_tone=mood_tone,
            visual_elements=", ".join(visual_elements),
            art_style=art_style
        )
        
        # Create completion
        response = self.create_completion(
            prompt=formatted_prompt,
            system_message="You are an expert at creating detailed prompts for AI image generation. Always respond with valid JSON.",
            force_json=True,
            temperature=0.4
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse image prompt JSON: {str(e)}")
    
    def generate_page_text(
        self,
        page_description: str,
        characters_present: List[str],
        age_group: str,
        language: str,
        book_theme: str,
        previous_context: str = "",
        story_arc: str = "",
        prompt_template: str = ""
    ) -> Dict[str, Any]:
        """
        Generate text content for a book page.
        
        Args:
            page_description: Description of what happens on the page
            characters_present: List of character names present
            age_group: Target age group
            language: Language for the text
            book_theme: Overall theme of the book
            previous_context: Context from previous pages
            story_arc: Overall story arc information
            prompt_template: Custom prompt template to use
            
        Returns:
            Structured page text as dictionary
        """
        # Format the prompt
        formatted_prompt = prompt_template.format(
            page_description=page_description,
            characters_present=", ".join(characters_present),
            age_group=age_group,
            language=language,
            book_theme=book_theme,
            previous_context=previous_context,
            story_arc=story_arc
        )
        
        # Create completion
        response = self.create_completion(
            prompt=formatted_prompt,
            system_message="You are an expert children's book author. Always respond with valid JSON.",
            force_json=True,
            temperature=0.6
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse page text JSON: {str(e)}")

