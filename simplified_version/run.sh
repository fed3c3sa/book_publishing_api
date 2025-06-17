#!/bin/bash

echo "🚀 Starting StoryMaker Simplified Version..."
echo "📧 Make sure to configure your email settings in secrets.env"
echo "🌐 The app will be available at http://localhost:5001"
echo ""

# Check if we're in the right directory
if [ ! -d "../src" ]; then
    echo "❌ Error: This script must be run from the simplified_version directory"
    echo "   and the parent directory must contain the 'src' folder"
    echo ""
    echo "   Current directory: $(pwd)"
    echo "   Expected structure:"
    echo "   book_publishing_api/"
    echo "   ├── src/"
    echo "   └── simplified_version/"
    echo ""
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the application
echo "Starting the application..."
python app.py 