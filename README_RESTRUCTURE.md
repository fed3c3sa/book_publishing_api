# Children's Book Generator - Restructured Architecture

## Overview

The Children's Book Generator has been completely restructured for better maintainability, type safety, and modularity. This document outlines the new architecture and how to use it.

## New Architecture

### 🏗️ Core Structure

```
src/
├── domain/              # Domain models with Pydantic
│   └── models.py       # All data models and types
├── interfaces/         # Abstract interfaces  
│   ├── ai_client_interface.py
│   ├── character_service_interface.py
│   ├── book_planning_interface.py
│   ├── content_generation_interface.py
│   └── pdf_generation_interface.py
├── services/           # Service implementations
│   ├── character_service.py
│   ├── book_planning_service.py
│   ├── content_generation_service.py
│   ├── pdf_generation_service.py
│   ├── ai_gemini_client.py
│   └── dependency_container.py
├── workflow/           # Workflow orchestration
│   ├── book_generation_workflow.py
│   ├── workflow_manager.py
│   └── workflow_context.py
├── exceptions/         # Custom exceptions
│   ├── base_exceptions.py
│   ├── character_exceptions.py
│   ├── book_exceptions.py
│   ├── content_exceptions.py
│   └── ai_exceptions.py
├── prompts/           # Organized prompt management
│   ├── prompt_manager.py
│   ├── prompt_registry.py
│   └── character/     # Character prompts
└── api/               # REST API endpoints
    └── routes.py
```

### 🔧 Key Improvements

1. **Type Safety**: All data uses Pydantic models with full validation
2. **Dependency Injection**: Clean separation of concerns with DI container
3. **Interface-Based Design**: All services implement clear interfaces
4. **Workflow Orchestration**: Step-by-step book generation with progress tracking
5. **Structured Error Handling**: Custom exception hierarchy with detailed error info
6. **Organized Prompts**: Categorized prompts with validation and versioning
7. **Modular Services**: Small, focused services with single responsibilities

### 📊 Data Models

All data is now strongly typed using Pydantic models:

- `Character` - Complete character with all attributes
- `BookPlan` - Structured book plan with pages and metadata
- `GenerationRequest` - API request validation
- `WorkflowContext` - Workflow state management
- `TextData` - Generated text with metadata
- `ImagePromptData` - Image generation prompts

### 🔄 Workflow Process

The new workflow provides clear step-by-step execution:

1. **Initialize** - Setup and validation
2. **Process Characters** - Extract and validate character data
3. **Create Plan** - Generate book structure
4. **Generate Images** - Create all illustrations
5. **Generate Text** - Create all page content  
6. **Create PDF** - Assemble final book
7. **Complete** - Finalize and cleanup

### 🎯 API Endpoints

The API has been cleaned up with better error handling:

- `POST /api/generate` - Start book generation
- `GET /api/status/<id>` - Get generation progress
- `GET /api/download/<id>` - Download completed book
- `POST /api/upload_character_image` - Upload character images
- `POST /api/upload_cover_image` - Upload cover images
- `GET /api/health` - Health check

## Usage

### Running the New Application

```bash
# Use the new modular app
python app_new.py

# Or the old app (still works)
python app.py
```

### Example API Request

```json
{
  "bookTitle": "The Adventures of Luna",
  "storyIdea": "A brave little fox goes on a magical journey",
  "numPages": 10,
  "ageGroup": "4-7",
  "language": "English",
  "artStyle": "children's book illustration",
  "characters": [
    {
      "type": "text",
      "content": "Luna is a small orange fox with bright green eyes and a fluffy tail",
      "name": "Luna",
      "character_type": "main"
    }
  ],
  "themes": ["friendship", "courage", "adventure"]
}
```

### Progress Tracking

```json
{
  "success": true,
  "status": {
    "generation_id": "uuid-here",
    "status": "generate_images",
    "progress": 60,
    "message": "Generating illustrations...",
    "characters_count": 1,
    "pages_count": 10,
    "start_time": "2024-01-01T12:00:00Z"
  }
}
```

## Migration Guide

### From Old to New

The old `app.py` still works, but to use the new architecture:

1. **Import Changes**: 
   ```python
   # Old
   from src.character_processing import CharacterProcessor
   
   # New  
   from src.services.character_service import CharacterService
   ```

2. **Model Usage**:
   ```python
   # Old
   character_data = {...}  # Raw dict
   
   # New
   character = Character(**character_data)  # Validated model
   ```

3. **Error Handling**:
   ```python
   # Old
   try:
       result = process_character(data)
   except Exception as e:
       print(f"Error: {e}")
   
   # New
   try:
       result = character_service.process_character_input(input)
   except CharacterProcessingError as e:
       print(f"Character error: {e.message}")
       print(f"Details: {e.details}")
   ```

## Benefits

### ✅ Better Maintainability
- Small, focused modules
- Clear separation of concerns
- Easy to test and modify

### ✅ Type Safety
- Pydantic validation
- Better IDE support
- Fewer runtime errors

### ✅ Better Error Handling
- Structured error hierarchy
- Detailed error context
- Graceful failure recovery

### ✅ Improved Testing
- Interface-based design
- Dependency injection
- Mockable services

### ✅ Better Documentation
- Self-documenting code
- Clear data models
- Organized structure

## Configuration

The new system uses the same configuration as before:
- `secrets.env` for API keys
- `prompts/` directory for prompt templates
- `output/` directory for generated content

## Backward Compatibility

- The old `app.py` continues to work unchanged
- All existing functionality is preserved
- Old prompts are still supported
- Generated content format remains the same

This restructure provides a solid foundation for future enhancements while maintaining all existing functionality.