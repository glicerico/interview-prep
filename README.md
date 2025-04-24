# Interview Preparation Tools

Scripts to help prepare for robot interviews by managing interview contexts and Redis data.

## Overview

This toolkit provides:

1. **Interview Context Management** - Create, store, and load interview contexts for robot interviews
2. **Redis Integration** - Store and retrieve interview data in Redis with session management
3. **Docker Support** - Connect to Redis running in Docker containers

## Contents

1. **prepare_guest_prompt.py**  
   - Creates structured interview briefs from Qwello data and LLM processing
   - Saves interview briefs as text files

2. **manage_interview_context.py**  
   - Lists available interview contexts stored as text files
   - Selects contexts to load into Redis for upcoming interviews
   - Creates new contexts when needed

3. **redis_client.py**  
   - Handles different Redis data types
   - Provides functions to get, set, list, and delete variables

4. **interview_redis_utils.py**  
   - Lists all stored interview guests
   - Retrieves interview briefs
   - Deletes interview data when no longer needed

5. **find_redis_ip.py**
   - Locates Redis containers in Docker environments
   - Updates .env file with correct connection details

## Setup

### Quick Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/interview-prep.git
   cd interview-prep
   ```

2. **Run the setup script**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   This script will:
   - Create a Python virtual environment
   - Install all dependencies
   - Make the scripts executable
   - Create a template .env file
   - Create the interview_contexts directory

3. **Edit the .env file** with your Redis connection details


## Usage

After running the setup script, you can use the tools directly from the bin directory:

```bash
./bin/manage_interview_context
./bin/redis_client
./bin/find_redis_ip
```

For convenience, you can add the bin directory to your PATH:
```bash
export PATH="$PATH:$(pwd)/bin"
```

Then you can run the commands from anywhere:
```bash
manage_interview_context
redis_client
```

## How It Works

### Interview Context Creation

1. The script prompts for guest information (name and focus areas)
2. It queries the Qwello API for background data on the guest (when available)
3. The data is processed through an LLM via LangChain
4. The LLM structures the information into sections like:
   - Guest background
   - Key topics
   - Talking points
   - Suggested questions
   - Potential follow-ups
   - Interview strategy
5. The structured output is saved as a text file in the `interview_contexts` directory

### Session Management

The hrsdk system uses a session ID to organize Redis variables:
- Each session has a unique ID stored in `default.current_session`
- All variables for a session are prefixed with `default.{session_id}.`
- This keeps Redis organized and allows multiple interview sessions

### Using Interview Data in Robot Templates

In your robot's Jinja2 templates, you can access the interview data like this:
```jinja
{% if interview_context %}
{# Use the interview context data here #}
{% endif %}
```

## Notes

- Interview contexts are stored as text files in the `interview_contexts` directory
- When you select a context, it's loaded into Redis with the current session ID
- The system is designed to keep Redis clean by using session-based prefixes
- Ensure you have valid API keys in your `.env` file if using external services

### Working with Redis Directly

The `redis_client.py` utility allows direct interaction with Redis:

```bash
# List variables (excluding sentence embeddings)
./bin/redis_client --list

# List all variables including sentence embeddings
./bin/redis_client --list-all

# Get a specific variable
./bin/redis_client --get <key>

# Set a specific variable
./bin/redis_client --set <key> <value>

# Delete a specific variable
./bin/redis_client --delete <key>
```
