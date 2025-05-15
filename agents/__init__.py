# agents/__init__.py
# This file makes the 'agents' directory a Python package.

# Import agent classes to make them easily accessible from the package level
# e.g., from agents import IdeatorAgent, StoryWriterAgent

from .base_agent import BaseBookAgent
from .ideator_agent import IdeatorAgent
from .story_writer_agent import StoryWriterAgent
from .image_creator_agent import ImageCreatorAgent
from .impaginator_agent import ImpaginatorAgent
from .trend_finder_agent import TrendFinderAgent
from .style_imitator_agent import StyleImitatorAgent
from .translator_agent import TranslatorAgent

__all__ = [
    "BaseBookAgent",
    "IdeatorAgent",
    "StoryWriterAgent",
    "ImageCreatorAgent",
    "ImpaginatorAgent",
    "TrendFinderAgent",
    "StyleImitatorAgent",
    "TranslatorAgent"
]

