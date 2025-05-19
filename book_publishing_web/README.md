# Book Publishing Web Interface - Updated Deployment Guide

## Overview

This document provides instructions for deploying and using the updated Book Publishing Web Interface, a single-page application that connects to the existing book publishing backend API. The interface features a dark theme with light blue accents, intuitive design, animated progress indicators, and an interactive book preview with page-turning animations.

## Features

- **Simple, Intuitive Interface**: Clean, dark-themed design with light blue accents
- **Enhanced Background Animations**: More visible particle effects for visual appeal
- **Direct Backend Integration**: Connects directly to the main.py backend like the Streamlit app
- **Animated Progress Tracking**: Visual feedback during the book generation process
- **Interactive Book Preview**: Realistic page-turning animations with physics effects
- **Access Control**: First 2 pages are freely viewable, with "purchase" required to see the rest
- **Expandable Sections**: View book plan, story summary, and image logs
- **Responsive Design**: Works well on both desktop and mobile devices

## Files Structure

```
book_publishing_web/
├── app.py                 # Flask backend for serving the web interface
├── index.html             # Main HTML file
├── static/
│   ├── css/
│   │   ├── styles.css     # Main stylesheet
│   │   └── book-preview.css # Book preview specific styles
│   ├── js/
│   │   ├── main.js        # Core JavaScript functionality
│   │   ├── api.js         # Backend API integration
│   │   └── book-preview.js # Enhanced book preview functionality
│   └── images/            # Directory for static images
```

## Deployment Instructions

### Option 1: Local Development Server

1. Ensure Python is installed with the required dependencies:
   ```
   pip install flask
   ```

2. Navigate to the `book_publishing_web` directory and run:
   ```
   python app.py
   ```

3. Access the application at `http://localhost:5000`

### Option 2: Production Deployment

For production deployment, you can use a WSGI server like Gunicorn:

1. Install Gunicorn:
   ```
   pip install gunicorn
   ```

2. Run the application:
   ```
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. For a more permanent setup, consider using a process manager like Supervisor and a reverse proxy like Nginx.

## Usage Guide

1. **Input Form**:
   - Enter your book idea in the text area
   - Optionally provide a title
   - Select a genre from the dropdown
   - Describe your preferred writing and image styles
   - Enable optional features if desired (Trend Finder, Style Imitator, Translator)
   - Click "Create My Book" to start the generation process

2. **Generation Process**:
   - The form will minimize and a progress indicator will appear
   - The progress bar and status messages will update as the book is generated
   - This process may take several minutes depending on the complexity of your book

3. **Book Results**:
   - Once generation is complete, you'll see a download button for the PDF
   - An interactive book preview will appear
   - Use the corner of pages or the navigation buttons to turn pages
   - You can view the first 2 pages for free
   - Click "Purchase Now" to unlock the full book (currently just simulated)
   - Expandable sections show additional information (Book Plan, Story Summary, Image Log)

## Technical Notes

- The web interface connects directly to the existing book publishing backend API
- The application uses the same parameter mapping as the Streamlit app
- The book preview uses turn.js for page-turning animations
- The application is designed to be responsive and work on various screen sizes
- No actual purchase logic is implemented; clicking "Purchase" simply unlocks all pages

## Customization

- To modify the color scheme, edit the CSS variables in `static/css/styles.css`
- To change the book preview appearance, edit `static/css/book-preview.css`
- To adjust the page access limit, modify the `pageAccessLimit` variable in `static/js/book-preview.js`

## Troubleshooting

- If the application fails to start, check that all dependencies are installed
- If book generation fails, verify that the backend API is properly configured
- For issues with the book preview, check browser console for JavaScript errors
- If the backend connection fails, ensure the path to main.py is correct in app.py

## Changes from Previous Version

- Updated color scheme from purple to light blue
- Enhanced background animations for greater visibility
- Fixed backend connection to properly integrate with main.py
- Added expandable sections for additional outputs
- Improved error handling and status updates
- Added support for all optional features from the Streamlit app
