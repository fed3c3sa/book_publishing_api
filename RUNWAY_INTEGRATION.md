# Runway Integration for Children's Book Generator

This document describes how to use the new Runway AI integration for image generation with advanced character consistency features.

## Overview

The Children's Book Generator now supports both Ideogram and Runway for image generation. When using Runway, the system automatically generates individual character reference images after character processing to maintain visual consistency throughout the book.

## Setup

### 1. Get Runway API Key

1. Sign up for a Runway account at [runwayml.com](https://runwayml.com)
2. Navigate to your API settings and generate an API key
3. Add your API key to your `secrets.env` file:

```
RUNWAY_API_KEY=your_runway_api_key_here
```

### 2. Configuration

The system automatically detects available API keys:
- If both `IDEOGRAM_API_KEY` and `RUNWAY_API_KEY` are present, Runway will be used for image generation
- If only `IDEOGRAM_API_KEY` is present, Ideogram will be used (default behavior)
- At least one image generation API key is required

## How It Works

### Character Consistency Workflow

When using Runway, the book generation process follows these steps:

1. **Character Processing**: Extract and enhance character descriptions using Gemini
2. **Character Image Generation**: Generate individual reference images for each character using Runway
3. **Book Planning**: Create the story structure and page-by-page content
4. **Page Image Generation**: Generate page illustrations using character reference images for consistency
5. **Cover Generation**: Generate book cover using character reference images

### Character Reference Images

- Each character gets a dedicated reference image generated using their detailed description
- Reference images are saved in `output/images/{book_title}_characters/`
- Character images use vertical (720x1280) aspect ratio for cost-effective reference use
- Character reference images are automatically tagged and referenced in subsequent generations

### Page Image Generation

- Page images reference character images using Runway's @mention syntax
- For example, if a character named "Luna" has a reference image, the prompt will include `@luna`
- Character consistency is maintained across all pages of the book
- Pages use 720x1280 (vertical portrait) aspect ratio optimized for children's book layouts

### Cover Generation

- Book covers use 720x1280 (vertical portrait) aspect ratio
- Main characters are referenced using their generated character images
- Cover includes book title space and professional children's book styling

## Technical Details

### API Integration

The Runway client (`src/ai_clients/runway_client.py`) provides:

- `generate_image()`: Core image generation with reference image support
- `generate_character_reference_image()`: Specialized character image generation
- `generate_book_page_image()`: Page illustration with character consistency
- `generate_book_cover()`: Professional book cover generation

### Reference Image Handling

- Local image files are automatically converted to base64 data URIs
- Remote URLs are passed directly to the API
- Image files support: PNG, JPEG, WebP
- Maximum file size: 10MB per reference image

### Error Handling

- Graceful fallback if character image generation fails
- Continues book generation even if some character images can't be created
- Detailed error logging for troubleshooting

## Comparison: Runway vs Ideogram

| Feature | Runway | Ideogram |
|---------|--------|----------|
| Character Consistency | ✅ Reference images + @mentions | ✅ Style reference + formulas |
| Image Quality | High (Gen-4 model) | High |
| Character Reference Generation | ✅ Automatic | ❌ Manual |
| Cross-page Consistency | ✅ Excellent | ✅ Good |
| Setup Complexity | Medium | Low |
| API Cost | Variable | Variable |

## Usage Examples

### Basic Usage

Simply add your Runway API key to `secrets.env` and the system will automatically use Runway for all image generation.

### Mixed Usage

If you have both API keys configured, you can modify the `use_runway` parameter in the ImageGenerator initialization to choose which service to use.

### Troubleshooting

#### Common Issues

1. **"Runway API key not found"**
   - Ensure `RUNWAY_API_KEY` is set in your environment or `secrets.env` file

2. **"Task timed out"**
   - Runway image generation can take longer than Ideogram
   - Check your API quota and rate limits

3. **"Reference image not found"**
   - Character image generation may have failed
   - Check logs for character generation errors

4. **Character consistency issues**
   - Ensure character descriptions are detailed and specific
   - Verify character reference images were generated successfully

#### Debug Mode

Set detailed logging to see the full character generation process:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- Support for additional Runway models (Gen-3, Gen-2)
- Video generation for animated book previews
- Advanced camera controls for page compositions
- Custom style transfer using uploaded reference images

## API Reference

For detailed API documentation, see:
- [Runway API Documentation](https://docs.dev.runwayml.com/)
- Source: `src/ai_clients/runway_client.py`
- Tests: Run the test implementation to verify your setup