"""
Domain models for the Children's Book Generator.

This module contains Pydantic models that define the core data structures
used throughout the application, providing type safety and validation.
"""

from .models import (
    # Character models
    Character,
    CharacterInput,
    PhysicalDescription,
    ExactColors,
    HeadFace,
    FacialStructure,
    HairFurCovering,
    BodyStructure,
    SkinSurface,
    MobilityPosture,
    ClothingAccessories,
    RegularOutfit,
    Accessories,
    PersonalityPsychology,
    EmotionalCharacteristics,
    SocialBehavior,
    CognitiveTraits,
    MotivationsValues,
    BackgroundContext,
    BehavioralPatterns,
    VoiceCommunication,
    StoryRoleDynamics,
    
    # Book models
    BookPlan,
    PageData,
    BookMetadata,
    BookStatistics,
    StoryArc,
    
    # Generation models
    GenerationRequest,
    GenerationStatus,
    ImagePromptData,
    TextData,
    
    # Workflow models
    WorkflowStep,
    WorkflowStatus,
)

__all__ = [
    # Character models
    "Character",
    "CharacterInput", 
    "PhysicalDescription",
    "ExactColors",
    "HeadFace",
    "FacialStructure",
    "HairFurCovering",
    "BodyStructure",
    "SkinSurface",
    "MobilityPosture",
    "ClothingAccessories",
    "RegularOutfit",
    "Accessories",
    "PersonalityPsychology",
    "EmotionalCharacteristics",
    "SocialBehavior",
    "CognitiveTraits",
    "MotivationsValues",
    "BackgroundContext",
    "BehavioralPatterns",
    "VoiceCommunication",
    "StoryRoleDynamics",
    
    # Book models
    "BookPlan",
    "PageData",
    "BookMetadata",
    "BookStatistics",
    "StoryArc",
    
    # Generation models
    "GenerationRequest",
    "GenerationStatus",
    "ImagePromptData",
    "TextData",
    
    # Workflow models
    "WorkflowStep",
    "WorkflowStatus",
]