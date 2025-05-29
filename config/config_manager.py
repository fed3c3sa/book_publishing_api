"""Configuration management for the book publishing API."""

import logging
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import dotenv

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration loading and validation for the book creation system."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the configuration manager."""
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        
        # Load environment variables
        self._load_environment()
        
    def _load_environment(self) -> None:
        """Load environment variables from secrets.env file."""
        env_file = Path("secrets.env")
        if env_file.exists():
            dotenv.load_dotenv(env_file)
            logger.info("Environment variables loaded from secrets.env")
        else:
            logger.warning("secrets.env file not found")
            
    def load_config(self) -> Dict[str, Any]:
        """
        Load and validate configuration from YAML file.
        
        Returns:
            Dict containing configuration data
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid YAML
        """
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
            
            # Validate and set defaults
            self._validate_and_set_defaults()
            
            logger.info(f"Configuration loaded successfully from {self.config_path}")
            return self.config
            
        except FileNotFoundError:
            logger.error(f"Configuration file {self.config_path} not found")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file {self.config_path}: {e}")
            raise
    
    def _validate_and_set_defaults(self) -> None:
        """Validate configuration and set default values."""
        # Set default output directory
        if "output_directory" not in self.config:
            self.config["output_directory"] = "outputs"
            
        # Ensure output directory exists
        output_dir = Path(self.config["output_directory"])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set default OpenAI model
        if "openai_llm_model" not in self.config:
            self.config["openai_llm_model"] = "gpt-4o"
            
        # Set default PDF settings
        if "pdf_layout" not in self.config:
            self.config["pdf_layout"] = self._get_default_pdf_layout()
            
        # Set default agent flags
        agent_flags = ["enable_trend_finder", "enable_style_imitator", "enable_translator"]
        for flag in agent_flags:
            if flag not in self.config:
                self.config[flag] = False
                
    def _get_default_pdf_layout(self) -> Dict[str, Any]:
        """Get default PDF layout configuration."""
        return {
            "margin_cm": 2.0,
            "font_name": "Helvetica",
            "font_size_title": 24,
            "font_size_h1": 18,
            "font_size_h2": 14,
            "font_size_normal": 12,
            "cover_image_width_inch": 5,
            "cover_image_height_inch": 7,
            "body_image_width_inch": 4.5
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self.config.get(key, default)
    
    def get_openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key from environment."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
        return api_key
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get LLM model configuration."""
        return {
            "api_key": self.get_openai_api_key(),
            "model_id": self.get("openai_llm_model", "gpt-4o")
        } 