"""
Pydantic models for the Children's Book Generator.

These models provide type safety, validation, and clear data structures
for all components of the book generation workflow.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field, validator, HttpUrl


# Enums for controlled vocabulary
class CharacterType(str, Enum):
    """Character role in the story."""
    MAIN = "main"
    SECONDARY = "secondary"
    BACKGROUND = "background"


class AgeCategory(str, Enum):
    """Character age category."""
    CHILD = "child"
    YOUNG_ADULT = "young_adult"
    MIDDLE_AGED = "middle_aged"
    ELDERLY = "elderly"


class InputType(str, Enum):
    """Type of character input."""
    TEXT = "text"
    IMAGE = "image"


class PageType(str, Enum):
    """Type of book page."""
    COVER = "cover"
    STORY = "story"
    BACK_COVER = "back_cover"


class GenerationStatus(str, Enum):
    """Status of book generation."""
    STARTING = "starting"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class WorkflowStep(str, Enum):
    """Steps in the book generation workflow."""
    INITIALIZE = "initialize"
    PROCESS_CHARACTERS = "process_characters"
    CREATE_PLAN = "create_plan"
    GENERATE_IMAGES = "generate_images"
    GENERATE_TEXT = "generate_text"
    CREATE_PDF = "create_pdf"
    COMPLETE = "complete"


# Character Models
class ExactColors(BaseModel):
    """Exact color specifications for character consistency."""
    primary: str = Field(..., description="Primary color (e.g., 'bright tangerine orange')")
    secondary: str = Field(..., description="Secondary color (e.g., 'pure snow white')")
    accent: str = Field(..., description="Accent color for details")
    details: str = Field(..., description="Specific color placements")
    seasonal_variations: str = Field(default="", description="Color changes in different seasons")


class FacialStructure(BaseModel):
    """Detailed facial feature structure."""
    eyes: str = Field(..., description="Eye shape, color, size, expression")
    nose: str = Field(..., description="Nose shape, color, size, characteristics")
    mouth: str = Field(..., description="Mouth shape, size, lip color, expression")
    cheeks: str = Field(..., description="Cheek shape, color, dimples, texture")
    chin: str = Field(..., description="Chin shape, prominence, cleft or dimple")
    forehead: str = Field(..., description="Forehead height, shape, markings")


class HairFurCovering(BaseModel):
    """Hair or fur covering details."""
    type: str = Field(..., description="Type: hair, fur, feathers, scales")
    color: str = Field(..., description="Specific colors and patterns")
    texture: str = Field(..., description="Texture: soft, coarse, curly, straight")
    length: str = Field(..., description="Length with specific styling")
    style: str = Field(..., description="How it's arranged, natural vs styled")
    special_features: str = Field(default="", description="Cowlicks, tufts, mane, etc.")


class HeadFace(BaseModel):
    """Head and face structure."""
    head_shape: str = Field(..., description="Detailed head shape description")
    facial_structure: FacialStructure
    hair_fur_covering: HairFurCovering
    ears: str = Field(..., description="Ear shape, size, position, coverage")
    other_facial_features: str = Field(default="", description="Whiskers, markings, scars")


class BodyStructure(BaseModel):
    """Body structure details."""
    torso: str = Field(..., description="Chest, waist, back characteristics")
    arms_hands: str = Field(..., description="Arm/hand length, strength, characteristics")
    legs_feet: str = Field(..., description="Leg/foot length, strength, characteristics")
    tail: str = Field(default="none", description="Tail presence, length, shape")
    wings: str = Field(default="none", description="Wing presence, size, type")
    other_appendages: str = Field(default="none", description="Horns, antlers, tentacles")


class SkinSurface(BaseModel):
    """Skin and surface characteristics."""
    texture: str = Field(..., description="Surface texture")
    patterns: str = Field(..., description="Stripes, spots, patches, gradients")
    markings: str = Field(..., description="Birthmarks, scars, natural patterns")
    special_properties: str = Field(default="", description="Glowing, color-changing properties")


class MobilityPosture(BaseModel):
    """Movement and posture characteristics."""
    typical_posture: str = Field(..., description="How they usually stand/sit/move")
    gait: str = Field(..., description="How they walk/run/fly")
    gesture_patterns: str = Field(..., description="Common hand/body movements")
    flexibility: str = Field(..., description="Range of motion, agility level")


class PhysicalDescription(BaseModel):
    """Complete physical description of a character."""
    overall_impression: str = Field(..., description="First impression, general vibe")
    size: str = Field(..., description="Size with specific measurements")
    build_physique: str = Field(..., description="Body type, fitness level, posture")
    height_weight: str = Field(..., description="Relative proportions")
    exact_colors: ExactColors
    head_face: HeadFace
    body_structure: BodyStructure
    skin_surface: SkinSurface
    distinctive_features: List[str] = Field(default_factory=list, description="Unique features")
    fixed_elements: List[str] = Field(default_factory=list, description="Always present elements")
    proportions: str = Field(..., description="Detailed body proportion description")
    mobility_posture: MobilityPosture


class RegularOutfit(BaseModel):
    """Regular clothing outfit."""
    upper_body: str = Field(..., description="Shirts, sweaters, jackets with details")
    lower_body: str = Field(..., description="Pants, skirts, shorts with details")
    footwear: str = Field(..., description="Shoes, boots, sandals, or bare feet")
    undergarments: str = Field(default="", description="If relevant and appropriate")
    style: str = Field(..., description="Casual, formal, uniform, fantasy style")


class Accessories(BaseModel):
    """Character accessories."""
    jewelry: str = Field(default="", description="Necklaces, rings, earrings")
    functional_items: str = Field(default="", description="Glasses, watch, belt, bag")
    decorative_items: str = Field(default="", description="Ribbons, bows, pins, patches")
    special_items: str = Field(default="", description="Magical items, tools, weapons")


class ClothingAccessories(BaseModel):
    """Clothing and accessories description."""
    regular_outfit: RegularOutfit
    accessories: Accessories
    seasonal_alternate_outfits: str = Field(default="", description="Different clothing for situations")
    clothing_preferences: str = Field(..., description="Favorite colors, styles, priorities")


class EmotionalCharacteristics(BaseModel):
    """Emotional characteristics."""
    dominant_emotions: List[str] = Field(default_factory=list, description="Primary emotional states")
    emotional_range: str = Field(..., description="From calm to excited states")
    emotional_triggers: str = Field(..., description="What evokes strong feelings")
    emotional_expression: str = Field(..., description="How they show feelings")


class SocialBehavior(BaseModel):
    """Social behavior patterns."""
    interaction_style: str = Field(..., description="Shy, outgoing, leadership style")
    communication_pattern: str = Field(..., description="Loud, quiet, eloquent, simple")
    relationship_approach: str = Field(..., description="Trusting, cautious, loyal")
    conflict_resolution: str = Field(..., description="How they handle disagreements")


class CognitiveTraits(BaseModel):
    """Cognitive traits and abilities."""
    intelligence_type: str = Field(..., description="Analytical, creative, emotional, practical")
    learning_style: str = Field(..., description="Visual, auditory, kinesthetic")
    problem_solving: str = Field(..., description="Methodical, intuitive, collaborative")
    attention_span: str = Field(..., description="Focused, easily distracted, hyperfocused")


class MotivationsValues(BaseModel):
    """Motivations and values."""
    primary_motivations: str = Field(..., description="What drives them forward")
    core_values: str = Field(..., description="What they believe in strongly")
    fears_concerns: str = Field(..., description="What they worry about")
    aspirations: str = Field(..., description="What they hope to achieve")


class PersonalityPsychology(BaseModel):
    """Personality and psychological traits."""
    core_personality_traits: List[str] = Field(default_factory=list, description="Main personality traits")
    emotional_characteristics: EmotionalCharacteristics
    social_behavior: SocialBehavior
    cognitive_traits: CognitiveTraits
    motivations_values: MotivationsValues


class BackgroundContext(BaseModel):
    """Character background and context."""
    origin_story: str = Field(..., description="Where they come from")
    current_living_situation: str = Field(..., description="Home environment")
    social_economic_status: str = Field(default="", description="If relevant to story")
    cultural_background: str = Field(..., description="Traditions, customs, beliefs")
    education_experience: str = Field(..., description="Schooling, training, lessons")
    significant_relationships: str = Field(..., description="Family, friends, mentors")
    life_experiences: str = Field(..., description="Formative events, adventures")


class BehavioralPatterns(BaseModel):
    """Behavioral patterns and habits."""
    daily_routines: str = Field(..., description="Typical day structure, habits")
    hobbies_interests: str = Field(..., description="What they do for fun")
    skills_talents: str = Field(..., description="What they're good at")
    quirks_habits: str = Field(..., description="Unique behaviors, nervous habits")
    reaction_patterns: str = Field(..., description="How they respond to situations")
    comfort_items: str = Field(default="", description="Favorite possessions")


class VoiceCommunication(BaseModel):
    """Voice and communication style."""
    speaking_voice: str = Field(..., description="Pitch, tone, accent, volume, speed")
    vocabulary_style: str = Field(..., description="Simple, complex, formal, casual")
    catchphrases: str = Field(default="", description="Repeated expressions")
    non_verbal_communication: str = Field(..., description="Gestures, facial expressions")
    laugh_type: str = Field(..., description="Giggle, hearty laugh, snort")
    crying_expression: str = Field(..., description="How they show sadness")


class StoryRoleDynamics(BaseModel):
    """Character's role in the story."""
    narrative_function: str = Field(..., description="Protagonist, antagonist, comic relief")
    character_arc_potential: str = Field(..., description="How they might grow")
    relationship_dynamics: str = Field(..., description="How they interact with others")
    conflict_sources: str = Field(..., description="Internal and external challenges")
    symbolic_meaning: str = Field(default="", description="What they represent")


class Character(BaseModel):
    """Complete character description model."""
    character_name: str = Field(..., description="Character name")
    character_type: CharacterType = Field(default=CharacterType.MAIN, description="Character role type")
    species: str = Field(..., description="Species or type (human, cat, dragon, etc.)")
    age_category: AgeCategory = Field(default=AgeCategory.CHILD, description="Age category")
    gender_presentation: str = Field(..., description="Gender expression")
    
    ideogram_character_seed: str = Field(..., description="Immutable character description for consistency")
    
    physical_description: PhysicalDescription
    clothing_accessories: ClothingAccessories
    personality_psychology: PersonalityPsychology
    background_context: BackgroundContext
    behavioral_patterns: BehavioralPatterns
    voice_communication: VoiceCommunication
    story_role_dynamics: StoryRoleDynamics
    
    consistency_formula: str = Field(..., description="Comprehensive formula for image generation")
    style_anchors: List[str] = Field(default_factory=list, description="Art style keywords")
    visual_style_notes: str = Field(default="", description="Art style preferences")
    
    # Metadata
    ai_expanded: bool = Field(default=True, description="Whether AI expanded the description")
    behavior_source: str = Field(default="ai_generated", description="Source of behavior data")
    original_user_description: Optional[str] = Field(None, description="Original user input")
    
    class Config:
        use_enum_values = True


class CharacterInput(BaseModel):
    """Input data for character processing."""
    type: InputType = Field(..., description="Type of input: text or image")
    content: Union[str, List[str]] = Field(..., description="Text description or image paths")
    name: str = Field(default="", description="Character name")
    character_type: CharacterType = Field(default=CharacterType.MAIN, description="Character role")
    additional_description: str = Field(default="", description="Additional text description")
    
    class Config:
        use_enum_values = True


# Book Models
class StoryArc(BaseModel):
    """Story arc structure."""
    opening: str = Field(..., description="Story opening")
    rising_action: str = Field(..., description="Rising action")
    climax: str = Field(..., description="Story climax")
    falling_action: str = Field(..., description="Falling action")
    resolution: str = Field(..., description="Story resolution")


class PageData(BaseModel):
    """Individual page data."""
    page_number: int = Field(..., description="Page number")
    page_type: PageType = Field(default=PageType.STORY, description="Type of page")
    scene_description: str = Field(..., description="What happens on this page")
    characters_present: List[str] = Field(default_factory=list, description="Characters on page")
    mood_tone: str = Field(default="happy and engaging", description="Mood and tone")
    visual_elements: List[str] = Field(default_factory=list, description="Visual elements")
    text_content_brief: str = Field(default="", description="Brief text content description")
    
    # Enhanced metadata
    page_id: str = Field(default="", description="Unique page identifier")
    estimated_word_count: int = Field(default=0, description="Estimated word count")
    character_details: List[Character] = Field(default_factory=list, description="Detailed character info")
    
    class Config:
        use_enum_values = True


class BookMetadata(BaseModel):
    """Book metadata."""
    original_story_idea: str = Field(..., description="Original story concept")
    num_characters: int = Field(..., description="Number of characters")
    requested_pages: int = Field(..., description="Requested page count")
    target_age_group: str = Field(..., description="Target age group")
    language: str = Field(..., description="Book language")


class BookStatistics(BaseModel):
    """Book statistics."""
    total_pages: int = Field(..., description="Total number of pages")
    story_pages: int = Field(..., description="Number of story pages")
    total_characters: int = Field(..., description="Total character count")
    main_characters: int = Field(..., description="Main character count")
    estimated_total_words: int = Field(..., description="Estimated total word count")


class BookPlan(BaseModel):
    """Complete book plan model."""
    book_title: str = Field(..., description="Book title")
    book_summary: str = Field(..., description="Book summary")
    target_age: str = Field(..., description="Target age group")
    themes: List[str] = Field(default_factory=list, description="Book themes")
    pages: List[PageData] = Field(..., description="All pages in the book")
    story_arc: Optional[StoryArc] = Field(None, description="Overall story arc")
    
    # Metadata
    metadata: Optional[BookMetadata] = Field(None, description="Book metadata")
    statistics: Optional[BookStatistics] = Field(None, description="Book statistics")


# Generation Models
class GenerationRequest(BaseModel):
    """Request for book generation."""
    book_title: str = Field(..., min_length=1, description="Title of the book")
    story_idea: str = Field(..., min_length=1, description="Main story concept")
    num_pages: int = Field(default=10, ge=4, le=50, description="Number of pages")
    age_group: str = Field(default="4-7", description="Target age group")
    language: str = Field(default="English", description="Book language")
    art_style: str = Field(default="children's book illustration", description="Art style")
    characters: List[CharacterInput] = Field(..., min_items=1, description="Character inputs")
    themes: List[str] = Field(default_factory=list, description="Story themes")
    cover_image_path: Optional[str] = Field(None, description="Path to uploaded cover image")


class WorkflowStatus(BaseModel):
    """Status of workflow execution."""
    current_step: WorkflowStep
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")
    message: str = Field(..., description="Status message")
    start_time: datetime
    updated_time: datetime
    error_message: Optional[str] = Field(None, description="Error message if failed")


class GenerationResult(BaseModel):
    """Result of book generation."""
    generation_id: str = Field(..., description="Unique generation identifier")
    status: GenerationStatus
    workflow_status: WorkflowStatus
    pdf_path: Optional[str] = Field(None, description="Path to generated PDF")
    book_plan: Optional[BookPlan] = Field(None, description="Generated book plan")
    characters: List[Character] = Field(default_factory=list, description="Processed characters")
    page_images: Dict[int, str] = Field(default_factory=dict, description="Generated images")
    page_texts: Dict[int, Dict[str, Any]] = Field(default_factory=dict, description="Generated texts")


# Image and Text Models
class ImagePromptData(BaseModel):
    """Data structure for image generation prompts."""
    detailed_prompt: str = Field(..., description="Detailed image generation prompt")
    style_keywords: List[str] = Field(default_factory=list, description="Style keywords")
    character_consistency_notes: str = Field(default="", description="Character consistency notes")
    mood_atmosphere: str = Field(..., description="Mood and atmosphere")
    composition_notes: str = Field(default="", description="Composition guidelines")
    technical_requirements: str = Field(default="", description="Technical requirements")
    
    # Metadata
    page_metadata: Dict[str, Any] = Field(default_factory=dict, description="Page metadata")


class TextData(BaseModel):
    """Generated text data for a page."""
    page_text: str = Field(..., description="Main page text")
    word_count: int = Field(..., description="Word count")
    reading_level: str = Field(default="", description="Reading level assessment")
    emotional_tone: str = Field(default="", description="Emotional tone")
    narrative_function: str = Field(default="", description="Narrative function")
    
    # Metadata
    page_metadata: Dict[str, Any] = Field(default_factory=dict, description="Page metadata")
    generation_notes: str = Field(default="", description="Generation notes")