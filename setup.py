#!/usr/bin/env python3
"""
Setup script for Children's Book Generator

This script helps you set up the project and test that everything is working correctly.
"""

import os
import sys
from pathlib import Path
import subprocess

def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {text}")
    print(f"{'='*60}")

def print_step(text):
    """Print a step description."""
    print(f"\n→ {text}")

def check_python_version():
    """Check if Python version is compatible."""
    print_step("Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install required Python packages."""
    print_step("Installing dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("   Please run: pip install -r requirements.txt")
        return False

def setup_config():
    """Set up configuration files."""
    print_step("Setting up configuration...")
    
    secrets_template = Path("secrets.env.template")
    secrets_file = Path("secrets.env")
    
    if not secrets_template.exists():
        print("❌ secrets.env.template not found")
        return False
    
    if not secrets_file.exists():
        # Copy template to secrets.env
        with open(secrets_template, 'r') as src:
            content = src.read()
        
        with open(secrets_file, 'w') as dst:
            dst.write(content)
        
        print("✅ Created secrets.env from template")
        print("   Please edit secrets.env with your actual API keys")
    else:
        print("✅ secrets.env already exists")
    
    return True

def check_api_keys():
    """Check if API keys are configured."""
    print_step("Checking API key configuration...")
    
    secrets_file = Path("secrets.env")
    if not secrets_file.exists():
        print("❌ secrets.env not found")
        return False
    
    with open(secrets_file, 'r') as f:
        content = f.read()
    
    has_gemini = "your_gemini_api_key_here" not in content and "GEMINI_API_KEY=" in content
    has_ideogram = "your_ideogram_api_key_here" not in content and "IDEOGRAM_API_KEY=" in content
    
    if has_gemini and has_ideogram:
        print("✅ API keys appear to be configured")
        return True
    else:
        print("⚠️  API keys need to be configured in secrets.env")
        if not has_gemini:
            print("   - Missing Gemini API key")
        if not has_ideogram:
            print("   - Missing Ideogram API key")
        return False

def test_imports():
    """Test that all modules can be imported."""
    print_step("Testing module imports...")
    
    try:
        sys.path.insert(0, str(Path("src")))
        
        from src.ai_clients import GeminiClient, IdeogramClient
        from src.character_processing import CharacterProcessor
        from src.book_planning import BookPlanner
        from src.content_generation import ImageGenerator, TextGenerator
        from src.pdf_generation import PDFGenerator
        
        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def create_directories():
    """Create necessary output directories."""
    print_step("Creating output directories...")
    
    directories = [
        "output",
        "output/characters",
        "output/plans", 
        "output/images",
        "output/texts",
        "output/books"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Output directories created")
    return True

def main():
    """Main setup function."""
    print_header("Children's Book Generator Setup")
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Install dependencies
    if success and not install_dependencies():
        success = False
    
    # Set up configuration
    if success and not setup_config():
        success = False
    
    # Create directories
    if success and not create_directories():
        success = False
    
    # Test imports
    if success and not test_imports():
        success = False
    
    # Check API keys
    api_keys_configured = check_api_keys()
    
    # Final summary
    print_header("Setup Summary")
    
    if success:
        print("✅ Setup completed successfully!")
        
        if api_keys_configured:
            print("\n🎉 You're ready to generate books!")
            print("   Run: python main.py")
        else:
            print("\n⚠️  Next steps:")
            print("   1. Edit secrets.env with your API keys")
            print("   2. Configure your book in main.py")
            print("   3. Run: python main.py")
        
        print("\n📚 Example configurations available in examples/")
        print("   - examples/space_adventure.py")
        print("   - examples/forest_friends.py")
        
    else:
        print("❌ Setup encountered errors")
        print("   Please resolve the issues above and run setup again")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

