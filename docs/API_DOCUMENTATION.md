# API Documentation

This document provides detailed information about the Children's Book Generator API and modules.

## Core Modules

### CharacterProcessor

Handles character description extraction from text or images.

```python
from src.character_processing import CharacterProcessor

processor = CharacterProcessor()

# Extract from text
character = processor.extract_character_from_text(
    character_description="A brave little mouse with a red cape",
    character_name="Hero Mouse",
    character_type="main"
)

# Extract from images
character = processor.extract_character_from_image(
    image_paths=["character1.jpg", "character2.png"],
    character_name="Hero Mouse",
    character_type="main"
)

# Process multiple characters
characters = processor.process_multiple_characters([
    {
        "type": "text",
        "name": "Hero",
        "character_type": "main",
        "content": "Description..."
    }
])
```

### BookPlanner

Creates detailed story structures and page-by-page plans.

```python
from src.book_planning import BookPlanner

planner = BookPlanner()

book_plan = planner.create_book_plan(
    story_idea="A mouse goes on an adventure",
    characters=character_list,
    num_pages=8,
    age_group="3-6",
    language="English"
)

# Save and load plans
plan_path = planner.save_book_plan(book_plan)
loaded_plan = planner.load_book_plan("book_plan.json")
```

### ImageGenerator

Generates illustrations using Ideogram AI.

```python
from src.content_generation import ImageGenerator

generator = ImageGenerator()

# Generate single page image
image_path = generator.generate_page_image(
    page_data=page_info,
    characters=character_list,
    book_title="My Book",
    art_style="watercolor, bright colors"
)

# Generate all page images
page_images = generator.generate_all_page_images(
    book_plan=book_plan,
    characters=character_list,
    art_style="children's illustration"
)

# Generate cover
cover_path = generator.generate_book_cover(
    book_plan=book_plan,
    characters=character_list
)
```

### TextGenerator

Creates age-appropriate text content for pages.

```python
from src.content_generation import TextGenerator

generator = TextGenerator()

# Generate single page text
text_data = generator.generate_page_text(
    page_data=page_info,
    book_plan=book_plan,
    previous_page_text="Previous text for context",
    language="English"
)

# Generate all page texts
page_texts = generator.generate_all_page_texts(
    book_plan=book_plan,
    language="English"
)
```

### PDFGenerator

Assembles final PDF and HTML books.

```python
from src.pdf_generation import PDFGenerator

generator = PDFGenerator()

# Create PDF book
pdf_path = generator.create_book_pdf(
    book_plan=book_plan,
    page_images=image_dict,
    page_texts=text_dict
)

# Create HTML version
html_path = generator.create_html_version(
    book_plan=book_plan,
    page_images=image_dict,
    page_texts=text_dict
)
```

## Data Structures

### Character Description Format

```json
{
    "character_name": "Luna",
    "character_type": "main",
    "species": "cat",
    "physical_description": {
        "size": "small",
        "colors": ["orange", "white", "cream"],
        "distinctive_features": ["green eyes", "white paws", "striped pattern"],
        "clothing_accessories": ["blue collar", "silver bell"],
        "facial_features": "curious expression, pink nose",
        "body_type": "fluffy, small build"
    },
    "personality_traits": ["curious", "brave", "adventurous"],
    "visual_style_notes": "friendly children's book style",
    "consistency_keywords": ["orange tabby", "green eyes", "blue collar"]
}
```

### Book Plan Format

```json
{
    "book_title": "Luna's Adventure",
    "book_summary": "A curious cat discovers a magical garden",
    "target_age": "3-6",
    "themes": ["friendship", "courage", "nature"],
    "pages": [
        {
            "page_number": 1,
            "page_type": "story",
            "scene_description": "Luna discovers the garden gate",
            "visual_elements": ["garden gate", "curious cat", "flowers"],
            "characters_present": ["Luna"],
            "mood_tone": "curious and excited",
            "text_content_brief": "Luna finds something interesting"
        }
    ],
    "story_arc": {
        "beginning": "pages 1-2",
        "middle": "pages 3-6", 
        "end": "pages 7-8"
    }
}
```

### Page Text Format

```json
{
    "page_text": "Luna pushed through the garden gate...",
    "text_style": "narrative",
    "reading_level": "early reader",
    "word_count": 25,
    "text_placement_suggestion": "bottom",
    "emphasis_words": ["garden", "magical"]
}
```

## Configuration Options

### Age Groups

- **3-5**: 5-15 words per page, very simple concepts
- **3-6**: 10-20 words per page, basic vocabulary
- **6-8**: 20-35 words per page, simple sentences
- **6-9**: 25-40 words per page, descriptive language
- **9-12**: 40-60 words per page, complex concepts

### Art Styles

Effective art style descriptions:
- `"children's book illustration, watercolor, soft colors"`
- `"cartoon style, bright and cheerful, simple shapes"`
- `"digital art, fantasy style, magical atmosphere"`
- `"hand-drawn, crayon texture, playful and fun"`

### Character Types

- **main**: Primary protagonists, appear in most pages
- **secondary**: Important supporting characters
- **background**: Minor characters, crowd elements

## Error Handling

All modules include comprehensive error handling:

```python
try:
    character = processor.extract_character_from_text(description)
except Exception as e:
    print(f"Character processing failed: {e}")
    # Handle error appropriately
```

Common error scenarios:
- Invalid API keys
- Network connectivity issues
- Malformed input data
- File system permissions
- API rate limits

## Performance Considerations

### API Rate Limits

- OpenAI: Respect rate limits for GPT-4o
- Ideogram: Monitor credit usage and generation limits

### File Management

- Images are saved locally for reuse
- JSON files track all generated content
- Automatic directory organization by book title

### Memory Usage

- Large images are processed efficiently
- Text content is kept in memory during generation
- Temporary files are cleaned up automatically

## Extending the System

### Adding New AI Services

1. Create new client in `src/ai_clients/`
2. Implement standard interface methods
3. Add configuration options
4. Update main workflow

### Custom Prompt Templates

1. Add new template to `prompts/` directory
2. Use `{variable}` syntax for replacements
3. Test with various inputs
4. Document expected outputs

### New Output Formats

1. Create new generator in appropriate module
2. Implement standard interface
3. Add configuration options
4. Test with existing content

## Best Practices

### Character Descriptions

- Be specific about visual details
- Include personality traits that affect appearance
- Use consistent terminology
- Consider the target age group

### Story Ideas

- Keep concepts age-appropriate
- Include clear beginning, middle, end
- Focus on relatable themes
- Allow for visual storytelling

### Art Style Specifications

- Be specific about style and mood
- Include color preferences
- Specify technical requirements
- Consider the target audience

### Text Content

- Match vocabulary to age group
- Use active voice
- Include sensory details
- Make it read-aloud friendly

