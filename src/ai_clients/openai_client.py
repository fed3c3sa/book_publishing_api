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
            visual_analysis_prompt = f"""You are an expert character designer analyzing this image with extraordinary precision. Examine every visible detail and provide an exhaustive visual description for character "{character_name}".

CRITICAL: Extract EVERY possible specific detail visible in the image. Be incredibly precise and thorough.

ANALYZE AND DESCRIBE IN EXTREME DETAIL:

**HAIR:**
- Exact color (not just "blonde" but "golden honey blonde with lighter highlights")
- Precise texture (straight, wavy, curly, coarse, fine, silky, etc.)
- Exact length and how it falls (shoulder-length, past shoulders, layered, etc.)
- Specific style (how it's parted, styled, natural vs styled)
- Any unique characteristics (cowlicks, flyaways, volume, etc.)

**FACE STRUCTURE:**
- Exact face shape (oval, round, heart-shaped, square, etc.)
- Forehead: height, width, any distinctive features
- Eyebrows: shape, thickness, color, arch, grooming
- Eyes: exact shape, size, color, expression, lid type, lashes, spacing
- Nose: precise shape, size, width, bridge, nostrils, profile
- Mouth: lip shape, fullness, color, width, natural expression
- Cheeks: fullness, bone structure, any dimples or distinctive features
- Chin: shape, prominence, any cleft or distinctive characteristics
- Jawline: strength, definition, shape

**SKIN:**
- Exact skin tone (not just "light" but specific undertones and description)
- Texture and appearance (smooth, freckled, etc.)
- Any visible markings, moles, freckles, or distinctive features

**BODY AND POSTURE:**
- Exact posture and how they're positioned
- Body proportions visible in the image
- Shoulder width and positioning
- Arm positioning and length
- Hand positioning, size, any visible characteristics
- Overall build and physique that's visible

**CLOTHING - BE EXTREMELY SPECIFIC:**
- Upper body garment: exact type, color, pattern, fit, material appearance, neckline, sleeves
- Lower body garment: exact type, color, pattern, fit, material appearance, length
- Any layers or additional clothing pieces
- Fit and how the clothing sits on the body
- Any wrinkles, texture, or distinctive characteristics

**ACCESSORIES AND DETAILS:**
- Jewelry: exact description of any rings, necklaces, earrings, bracelets
- Any hair accessories (clips, bands, etc.)
- Any other accessories visible (watches, bags, etc.)
- Specific details about materials, colors, styles

**SETTING AND CONTEXT:**
- Background elements that might suggest lifestyle or personality
- Lighting and how it affects the appearance
- Any props or items that suggest interests or characteristics

**EXPRESSION AND PERSONALITY INDICATORS:**
- Exact facial expression and what it conveys
- Eye expression and gaze direction
- Mouth expression (smile type, neutral, etc.)
- Overall demeanor and vibe projected
- Confidence level suggested by posture and expression

**DISTINCTIVE FEATURES:**
- Any unique or memorable characteristics that make this person stand out
- Features that would be essential for consistent artistic reproduction
- Proportional relationships between features

Be extraordinarily specific about colors - don't say "blue dress" say "deep navy blue dress with small white floral pattern" or whatever you actually observe.

Describe textures, materials, and how things appear to feel.

Include measurements and proportions relative to other features.

This description will be used to create identical artistic reproductions, so include every detail that an artist would need to draw this person consistently across multiple images."""
            
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
            comprehensive_prompt = f"""Extract the specific details from this visual analysis and organize them into JSON format.

VISUAL ANALYSIS OF {character_name}:
{visual_description}

Based on the analysis above, create a JSON character description. Use the exact details mentioned - for example:
- Hair color is described as "Golden blonde with lighter sun-kissed highlights"
- Dress is described as "Sleeveless dress with thin straps, featuring a vibrant pattern of large red flowers and blue leaves on a light green background"
- Face shape is described as "Oval face shape"
- Eyes are described as "Almond-shaped, medium size, light brown color"
- And so on...

Extract ALL these specific details and put them in the JSON structure below:

{{
  "character_name": "{character_name}",
  "character_type": "main",
  "species": "human",
  "age_category": "young adult", 
  "gender_presentation": "female",
  
  "ideogram_character_seed": "A young woman with golden blonde wavy hair past her shoulders, wearing a vibrant floral dress with red flowers and blue leaves on light green, gentle smile, casual elegance in natural outdoor setting",
  
  "physical_description": {{
    "overall_impression": "Confident yet relaxed with casual elegance, approachable demeanor",
    "size": "medium human size",
    "build_physique": "Slim and athletic build",
    "height_weight": "Proportional build for age",
    
    "exact_colors": {{
      "primary": "Light green background with large red flowers and blue leaves (dress pattern)",
      "secondary": "Golden blonde with lighter sun-kissed highlights (hair)",
      "accent": "Thin gold (necklace) and pearl white (earrings)",
      "details": "Vibrant floral pattern with red flowers, blue leaves on light green dress background",
      "seasonal_variations": "none"
    }},
    
    "head_face": {{
      "head_shape": "Oval face shape",
      "facial_structure": {{
        "eyes": "Almond-shaped, medium size, light brown color, with calm and relaxed expression",
        "nose": "Straight with gentle slope, medium width, slightly rounded nostrils",
        "mouth": "Medium fullness, soft pink color, with subtle natural smile",
        "cheeks": "Slightly prominent cheekbones with smooth contour",
        "chin": "Softly rounded with no cleft",
        "forehead": "Medium height and width, smooth with no distinctive features"
      }},
      "hair_fur_covering": {{
        "type": "hair",
        "color": "Golden blonde with lighter sun-kissed highlights",
        "texture": "Naturally wavy with slightly tousled appearance",
        "length": "Falls just past the shoulders",
        "style": "Center-parted with natural waves cascading down",
        "special_features": "Slight volume with a few flyaways, giving casual beachy look"
      }},
      "ears": "Normal human ears",
      "other_facial_features": "Light brown eyebrows, medium thickness, gently arched, well-groomed"
    }},
    
    "body_structure": {{
      "torso": "Proportional with visible shoulders, medium shoulder width with gentle slope",
      "arms_hands": "Right arm relaxed by the side, hands not fully visible",
      "legs_feet": "Not fully visible in analysis",
      "tail": "none",
      "wings": "none",
      "other_appendages": "none"
    }},
    
    "skin_surface": {{
      "texture": "Smooth with healthy, even appearance",
      "patterns": "No visible markings or freckles",
      "markings": "None visible",
      "special_properties": "Light skin with warm undertones"
    }},
    
    "distinctive_features": [
      "Golden blonde wavy hair with natural highlights",
      "Vibrant floral dress pattern with red flowers and blue leaves",
      "Gentle smile with relaxed expression",
      "Almond-shaped light brown eyes",
      "Oval face shape with soft features"
    ],
    "fixed_elements": [
      "Hair color and wavy texture",
      "Dress pattern and colors",
      "Gentle facial expression",
      "Proportional balanced features"
    ],
    "proportions": "Balanced facial features with harmonious proportions",
    
    "mobility_posture": {{
      "typical_posture": "Relaxed and slightly angled to the side",
      "gait": "Confident and graceful",
      "gesture_patterns": "Confident yet relaxed demeanor",
      "flexibility": "Natural human flexibility"
    }}
  }},
  
  "clothing_accessories": {{
    "regular_outfit": {{
      "upper_body": "Sleeveless dress with thin straps, featuring vibrant pattern of large red flowers and blue leaves on light green background, deep V neckline with ruffled edge",
      "lower_body": "Continuation of the flowing dress",
      "footwear": "Not visible in analysis",
      "undergarments": "Appropriate undergarments",
      "style": "Casual summery elegance with loose and flowing fit"
    }},
    "accessories": {{
      "jewelry": "Simple thin gold necklace and pearl stud earrings",
      "functional_items": "None visible",
      "decorative_items": "Floral dress pattern serves as decoration",
      "special_items": "None"
    }},
    "seasonal_alternate_outfits": "Summer variations of floral dress style",
    "clothing_preferences": "Casual elegance with floral patterns and natural fabrics"
  }},
  
  "personality_psychology": {{
    "core_personality_traits": ["Gentle", "Confident", "Relaxed", "Approachable", "Elegant"],
    "emotional_characteristics": {{
      "dominant_emotions": ["Calm", "Content", "Friendly"],
      "emotional_range": "Confident yet relaxed with casual elegance",
      "emotional_triggers": "Social situations and creative expression",
      "emotional_expression": "Gentle and authentic with subtle smile"
    }},
    "social_behavior": {{
      "interaction_style": "Approachable and relaxed",
      "communication_pattern": "Clear and warm",
      "relationship_approach": "Friendly and genuine",
      "conflict_resolution": "Diplomatic and understanding"
    }},
    "cognitive_traits": {{
      "intelligence_type": "Social and aesthetic intelligence",
      "learning_style": "Visual and experiential",
      "problem_solving": "Thoughtful and creative",
      "attention_span": "Good focus when interested"
    }},
    "motivations_values": {{
      "primary_motivations": "Personal expression and authentic connections",
      "core_values": "Authenticity and natural beauty",
      "fears_concerns": "Normal social considerations",
      "aspirations": "Creative fulfillment and meaningful relationships"
    }}
  }},
  
  "background_context": {{
    "origin_story": "Comes from supportive background that values natural beauty and authenticity",
    "current_living_situation": "Comfortable lifestyle with appreciation for outdoor settings",
    "social_economic_status": "Middle class comfort with quality accessories",
    "cultural_background": "Contemporary Western culture",
    "education_experience": "Well-educated with refined aesthetic sense",
    "significant_relationships": "Strong connections with family and friends",
    "life_experiences": "Positive experiences that built confidence and poise"
  }},
  
  "behavioral_patterns": {{
    "daily_routines": "Well-groomed lifestyle with attention to natural beauty",
    "hobbies_interests": "Fashion, outdoor activities, social gatherings",
    "skills_talents": "Aesthetic sense, social skills, natural grace",
    "quirks_habits": "Attention to styling details while maintaining natural look",
    "reaction_patterns": "Calm and measured responses with gentle approach",
    "comfort_items": "Floral patterns, natural fabrics, delicate jewelry"
  }},
  
  "voice_communication": {{
    "speaking_voice": "Warm and clear with gentle tone",
    "vocabulary_style": "Articulate and genuine",
    "catchphrases": "Positive and encouraging expressions",
    "non_verbal_communication": "Relaxed body language with gentle expressions",
    "laugh_type": "Genuine warm laughter matching gentle smile",
    "crying_expression": "Graceful emotional expression"
  }},
  
  "story_role_dynamics": {{
    "narrative_function": "Protagonist or wise supportive friend character",
    "character_arc_potential": "Growth through relationships and self-discovery",
    "relationship_dynamics": "Natural connector and supportive friend",
    "conflict_sources": "Internal growth challenges and external obstacles",
    "symbolic_meaning": "Represents natural beauty, confidence, and authentic self-expression"
  }},
  
  "consistency_formula": "Always depict with golden blonde wavy hair past shoulders, vibrant floral dress (red flowers, blue leaves, light green background), gentle smile, almond-shaped light brown eyes, oval face, relaxed confident posture in natural lighting",
  "style_anchors": ["Realistic portrait", "Natural golden hour lighting", "Vibrant floral patterns", "Soft natural textures", "Casual elegance"],
  "visual_style_notes": "Use warm natural lighting like sunset/golden hour, emphasize the floral dress pattern details, capture the gentle relaxed expression, highlight the natural wavy hair texture"
}}

Use this structure with the exact details extracted from the visual analysis above."""
            
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

