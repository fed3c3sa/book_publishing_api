# main.py
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import uuid

from config.config_manager import ConfigManager
from workflows.book_creation_workflow import BookCreationWorkflow
from data_models.character import Character

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BookCreationOrchestrator:
    """Main orchestrator for the book creation process."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the orchestrator with configuration."""
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.load_config()
        self.workflow = None
        
    def create_project_directory(self) -> str:
        """Create and return a unique project directory for this book creation run."""
        project_base_output_dir = self.config.get("output_directory", "outputs")
        project_id = f"book_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        project_output_dir = os.path.join(project_base_output_dir, project_id)
        
        os.makedirs(project_output_dir, exist_ok=True)
        logger.info(f"Created project directory: {project_output_dir}")
        return project_output_dir
        
    def setup_workflow(self, project_output_dir: str) -> BookCreationWorkflow:
        """Setup and return the book creation workflow."""
        try:
            workflow = BookCreationWorkflow(
                config=self.config,
                project_output_dir=project_output_dir
            )
            logger.info("Book creation workflow initialized successfully")
            return workflow
        except Exception as e:
            logger.error(f"Failed to initialize workflow: {e}")
            raise
            
    def run_book_creation(self, user_book_idea: str, characters: Optional[List[Character]] = None) -> Tuple[str, Optional[str]]:
        """
        Run the complete book creation process.
        
        Args:
            user_book_idea: The user's book concept
            characters: Optional list of pre-defined characters
            
        Returns:
            Tuple of (project_directory, pdf_path)
        """
        try:
            logger.info("Starting book creation process")
            
            # Create project directory
            project_output_dir = self.create_project_directory()
            
            # Setup workflow
            self.workflow = self.setup_workflow(project_output_dir)
            
            # Run the workflow
            pdf_path = self.workflow.execute(user_book_idea, characters)
            
            logger.info(f"Book creation completed successfully. PDF: {pdf_path}")
            return project_output_dir, pdf_path
            
        except Exception as e:
            logger.error(f"Book creation failed: {e}")
            return project_output_dir if 'project_output_dir' in locals() else None, None


def main():
    import dotenv
    dotenv.load_dotenv("secrets.env")
    """Main entry point for the book creation application."""
    try:
        # Initialize orchestrator
        orchestrator = BookCreationOrchestrator()
        
        # Get default book idea from config
        default_idea = orchestrator.config.get(
            "default_user_book_idea", 
            "A children's book about a curious squirrel who explores a magical garden."
        )
        
        # Create the book
        project_dir, pdf_path = orchestrator.run_book_creation(default_idea)
        
        if pdf_path:
            print(f"\n✅ Book creation completed successfully!")
            print(f"📁 Project directory: {project_dir}")
            print(f"📖 Final PDF: {pdf_path}")
        else:
            print("\n❌ Book creation failed. Check logs for details.")
            
    except Exception as e:
        logger.error(f"Application failed: {e}")
        print(f"\n❌ Application failed: {e}")


if __name__ == "__main__":
    main()