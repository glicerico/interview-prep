#!/bin/bash
# Setup script for interview preparation tools

echo "Setting up interview preparation tools..."

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Make scripts executable
echo "Making scripts executable..."
chmod +x src/redis_client.py
chmod +x src/manage_interview_context.py
chmod +x src/find_redis_ip.py

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your Redis connection details"
fi

# Create interview_contexts directory if it doesn't exist
if [ ! -d interview_contexts ]; then
    echo "Creating interview_contexts directory..."
    mkdir interview_contexts
fi

echo "Setup complete! You can now run the tools directly:"
echo "  ./src/manage_interview_context.py"
echo "  ./src/redis_client.py"
echo ""
echo "Or activate the virtual environment manually with:"
echo "  source venv/bin/activate" 