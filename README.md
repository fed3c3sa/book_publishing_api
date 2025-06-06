# Children's Book Generator 🎨📚

An AI-powered tool for creating beautiful, personalized children's books with custom characters, engaging stories, and professional illustrations.

## Features ✨

- **Character Creation**: Extract detailed character descriptions from text or images using GPT-4o
- **Story Planning**: Generate age-appropriate story structures with page-by-page breakdowns
- **Image Generation**: Create consistent, beautiful illustrations using Ideogram AI
- **Text Generation**: Craft engaging, age-appropriate text content for each page
- **PDF Assembly**: Combine images and text into professional PDF books with full-page backgrounds
- **HTML Output**: Generate interactive HTML versions of your books
- **Modular Architecture**: Well-organized, maintainable code structure

## Quick Start 🚀

### 1. Setup

```bash
# Clone or download the project
cd children_book_generator

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp secrets.env.template secrets.env
# Edit secrets.env with your actual API keys
```

### 2. Configure Your Book

Edit the configuration section in `main.py`:

```python
# Book Configuration
BOOK_TITLE = "Your Book Title"
STORY_IDEA = "Your story concept..."
NUM_PAGES = 8
AGE_GROUP = "3-6"
LANGUAGE = "English"

# Character Configuration
CHARACTERS = [
    {
        "type": "text",  # or "image"
        "name": "Character Name",
        "character_type": "main",  # "main", "secondary", "background"
        "content": "Character description...",
    }
]
```

### 3. Generate Your Book

```bash
python main.py
```

The script will:
1. Process your character descriptions
2. Create a detailed story plan
3. Generate illustrations for each page
4. Create text content for each page
5. Assemble everything into PDF and HTML formats

## Requirements 📋

### API Keys Required

- **OpenAI API Key**: For GPT-4o text generation and character analysis
- **Ideogram API Key**: For image generation

### Python Dependencies

- `openai>=1.0.0` - OpenAI API client
- `requests>=2.31.0` - HTTP requests for Ideogram API
- `reportlab>=4.0.0` - PDF generation
- `Pillow>=10.0.0` - Image processing
- `python-dotenv>=1.0.0` - Environment variable management
- `pydantic>=2.0.0` - Data validation

## Project Structure 📁

```
children_book_generator/
├── main.py                 # Main script - configure and run here
├── requirements.txt        # Python dependencies
├── secrets.env.template    # API keys template
├── src/                    # Source code modules
│   ├── ai_clients/         # OpenAI and Ideogram API clients
│   ├── character_processing/ # Character description extraction
│   ├── book_planning/      # Story structure and planning
│   ├── content_generation/ # Image and text generation
│   ├── pdf_generation/     # PDF and HTML assembly
│   └── utils/              # Configuration and utilities
├── prompts/                # AI prompt templates
├── output/                 # Generated content (created automatically)
│   ├── characters/         # Character description files
│   ├── plans/              # Book plan files
│   ├── images/             # Generated illustrations
│   ├── texts/              # Generated text content
│   └── books/              # Final PDF and HTML books
├── examples/               # Example configurations
└── docs/                   # Additional documentation
```

## Configuration Guide 🔧

### Character Types

- **Main**: Primary characters that appear throughout the story
- **Secondary**: Important supporting characters
- **Background**: Minor characters or crowd elements

### Age Groups

- **3-5**: Very simple language, basic concepts
- **3-6**: Simple sentences, repetitive patterns
- **6-8**: Slightly more complex vocabulary
- **6-9**: Longer sentences, more descriptive
- **9-12**: Rich vocabulary, character development

### Art Styles

Examples of art style descriptions:
- `"children's book illustration, watercolor style, bright and colorful"`
- `"cartoon style, friendly characters, vibrant colors"`
- `"digital art, soft pastels, dreamy atmosphere"`
- `"hand-drawn style, pencil and crayon, playful"`

## Advanced Usage 💡

### Using Image-Based Characters

```python
CHARACTERS = [
    {
        "type": "image",
        "name": "Luna",
        "character_type": "main",
        "content": ["/path/to/character_image1.jpg", "/path/to/character_image2.png"],
        "additional_description": "Luna is brave and curious"
    }
]
```

### Custom Themes

```python
THEMES = ["friendship", "courage", "environmental awareness", "problem-solving"]
```

### Multiple Languages

The system supports multiple languages. Simply change:

```python
LANGUAGE = "Spanish"  # or "French", "German", etc.
```

## Output Files 📄

### Generated Files

- **PDF Book**: Professional book with full-page background images and text overlays
- **HTML Book**: Interactive web version with responsive design
- **Character Files**: JSON files with detailed character descriptions
- **Story Plan**: Complete page-by-page story structure
- **Individual Images**: High-quality illustrations for each page
- **Text Files**: Generated text content for each page

### File Organization

All outputs are organized in the `output/` directory by book title and content type for easy management and reuse.

## Troubleshooting 🔧

### Common Issues

1. **API Key Errors**
   - Ensure your API keys are correctly set in `secrets.env`
   - Check that your OpenAI account has GPT-4o access
   - Verify your Ideogram API key is active

2. **Image Generation Fails**
   - Check your internet connection
   - Ensure Ideogram API has sufficient credits
   - Try simplifying character descriptions

3. **PDF Generation Issues**
   - Ensure all required fonts are available
   - Check that image files exist and are accessible
   - Verify sufficient disk space

### Getting Help

- Check the `docs/` directory for detailed documentation
- Review example configurations in `examples/`
- Ensure all dependencies are properly installed

## License 📜

This project is provided as-is for educational and creative purposes. Please ensure you comply with the terms of service for OpenAI and Ideogram APIs.

## Contributing 🤝

This is a modular system designed for easy extension. You can:
- Add new AI service integrations
- Create custom prompt templates
- Implement additional output formats
- Enhance the PDF layout system

---

**Happy Book Creating! 🎉📚**

