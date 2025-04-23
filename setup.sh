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

# Create wrapper scripts
echo "Creating wrapper scripts..."
mkdir -p bin

# Create manage_interview_context wrapper
cat > bin/manage_interview_context << 'EOF'
#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." &> /dev/null && pwd )"
cd "$PROJECT_ROOT"  # Change to project root to ensure imports work
"$PROJECT_ROOT/venv/bin/python" "$PROJECT_ROOT/src/manage_interview_context.py" "$@"
EOF

# Create redis_client wrapper
cat > bin/redis_client << 'EOF'
#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." &> /dev/null && pwd )"
cd "$PROJECT_ROOT"  # Change to project root to ensure imports work
"$PROJECT_ROOT/venv/bin/python" "$PROJECT_ROOT/src/redis_client.py" "$@"
EOF

# Create find_redis_ip wrapper
cat > bin/find_redis_ip << 'EOF'
#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." &> /dev/null && pwd )"
cd "$PROJECT_ROOT"  # Change to project root to ensure imports work
"$PROJECT_ROOT/venv/bin/python" "$PROJECT_ROOT/src/find_redis_ip.py" "$@"
EOF

# Make wrapper scripts executable
chmod +x bin/manage_interview_context
chmod +x bin/redis_client
chmod +x bin/find_redis_ip

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
echo "  ./bin/manage_interview_context"
echo "  ./bin/redis_client"
echo "  ./bin/find_redis_ip"
echo ""
echo "For convenience, you might want to add the bin directory to your PATH:"
echo "  export PATH=\"\$PATH:$(pwd)/bin\""
echo ""
echo "Or activate the virtual environment manually with:"
echo "  source venv/bin/activate" 