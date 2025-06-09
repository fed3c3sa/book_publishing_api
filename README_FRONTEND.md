# Children's Book Generator - Web Frontend

A beautiful, minimalistic web interface for generating AI-powered children's books with custom characters and stories.

## Features

✨ **Easy-to-use web interface** - Clean, responsive design that works on all devices  
📚 **Complete book configuration** - Set title, story, pages, age group, themes, and art style  
👥 **Multiple character support** - Add unlimited characters with text descriptions or image uploads  
🎨 **Real-time progress tracking** - Watch your book being generated with live progress updates  
📥 **Instant download** - Get your finished PDF book immediately after generation  

## Quick Start

### 1. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### 2. Configure API Keys

Make sure your `secrets.env` file contains your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
# Add other API keys as needed
```

### 3. Run the Application

```bash
# Start the Flask web server
python app.py
```

The application will start on `http://localhost:5000`

### 4. Access the Web Interface

Open your web browser and go to:
```
http://localhost:5000
```

## How to Use

### Book Configuration
1. **Book Title**: Enter a creative title for your story
2. **Story Idea**: Describe your story in detail - the more detail, the better!
3. **Number of Pages**: Choose between 6-20 pages
4. **Age Group**: Select the target age group (3-5, 4-7, 6-8, 6-9, or 9-12 years)
5. **Language**: Choose the language for your book
6. **Art Style**: Describe the visual style (e.g., "whimsical children's book illustration")
7. **Themes**: Select relevant themes like friendship, adventure, courage, etc.

### Adding Characters

#### Text Description Method:
1. Click "Add Character" 
2. Enter the character name
3. Choose character type (Main, Secondary, or Background)
4. Select "Text Description" 
5. Write a detailed description of the character's appearance, personality, and traits

#### Image Upload Method:
1. Click "Add Character"
2. Enter the character name  
3. Choose character type
4. Select "Upload Image"
5. Click the upload area and select an image file (PNG, JPG, JPEG, GIF up to 16MB)

### Generation Process

1. Click "Generate Book" 
2. Watch the real-time progress bar and status updates
3. The process includes:
   - Loading configuration and AI clients
   - Processing character descriptions  
   - Creating book plan and story structure
   - Generating AI illustrations
   - Creating text content
   - Assembling the final PDF
4. Download your completed book when ready!

## Technical Details

### Architecture
- **Backend**: Flask API with asynchronous book generation
- **Frontend**: Clean HTML/CSS/JavaScript with real-time updates
- **Character Processing**: Supports both text descriptions and image uploads
- **Progress Tracking**: WebSocket-style polling for live status updates
- **File Management**: Secure file uploads with validation

### API Endpoints
- `GET /` - Serve the web interface
- `POST /api/generate` - Start book generation
- `GET /api/status/<generation_id>` - Get generation status
- `GET /api/download/<generation_id>` - Download completed book
- `POST /api/upload_character_image` - Upload character images

### File Structure
```
├── app.py                 # Flask backend API
├── templates/
│   └── index.html        # Web frontend
├── temp_uploads/         # Temporary image uploads
├── output/               # Generated books and assets
└── src/                  # Core book generation modules
```

## Troubleshooting

### Common Issues

**"Generation failed" error**:
- Check that your API keys are correctly set in `secrets.env`
- Ensure you have a stable internet connection
- Verify all required dependencies are installed

**Image upload not working**:
- Make sure the image is under 16MB
- Use supported formats: PNG, JPG, JPEG, GIF
- Check that the `temp_uploads/` directory exists and is writable

**Slow generation**:
- Complex stories with many characters take longer to process
- Image generation is the most time-consuming step
- Consider reducing the number of pages for faster results

### Support

If you encounter issues:
1. Check the console/terminal for error messages
2. Ensure all requirements are installed: `pip install -r requirements.txt`
3. Verify your API keys are valid and have sufficient credits
4. Try with a simpler story/fewer characters first

## Advanced Usage

### Customizing Art Styles
Try these art style descriptions for different looks:
- `"watercolor children's illustration, soft pastel colors"`
- `"cartoon style, bright vibrant colors, Disney-like animation"`
- `"realistic digital art, detailed fantasy illustration"`
- `"minimalist flat design, geometric shapes, modern colors"`

### Character Description Tips
For best results, include:
- **Physical appearance**: size, colors, distinctive features
- **Personality traits**: friendly, brave, curious, etc.
- **Clothing/accessories**: what they wear or carry
- **Special abilities**: if they have any magical powers or skills

### Theme Combinations
Popular theme combinations:
- Friendship + Adventure
- Courage + Kindness  
- Acceptance + Family
- Adventure + Discovery

---

🎨 **Happy book creating!** Generate endless magical stories for children with the power of AI. 