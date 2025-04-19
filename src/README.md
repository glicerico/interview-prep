# hrsdk Interview Preparation Pipeline

This folder provides a Python-based pipeline that fetches background data from the Qwello API, processes it through an LLM using LangChain, and generates a structured interview prompt for an hrsdk character to use during interviews.

## Contents

1. **prepare_guest_prompt.py**  
   The main Python script that:
   - Creates structured interview briefs from Qwello data and LLM processing
   - Saves interview briefs as text files

2. **manage_interview_context.py**  
   Interactive tool to:
   - List available interview contexts stored as text files
   - Select a context to load into Redis for an upcoming interview
   - Create a new context if needed

3. **redis_client.py**  
   Utility for interacting with Redis:
   - Handles different Redis data types
   - Provides functions to get, set, and list variables

4. **interview_redis_utils.py**  
   Specialized utilities for managing interview data in Redis:
   - List all stored interview guests
   - Retrieve interview briefs
   - Delete interview data when no longer needed

5. **requirements.txt**  
   Dependencies for the pipeline.

6. **.env.example**  
   Shows how to store environment variables like API keys.

## Usage

1. **Install Dependencies**:
   ```bash
   cd interview_preparation
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Set Up Environment Variables**:  
   - Copy `.env.example` to `.env`.  
   - Fill in your Qwello API key and OpenAI API key in `.env`.

3. **Ensure Redis is Running**:
   - Install Redis if not already installed
   - Start the Redis server (typically `redis-server`)
   - The scripts default to connecting to Redis on localhost:6379

4. **Manage Interview Contexts**:

   Run the interactive context manager:
   ```bash
   python manage_interview_context.py
   ```

   This will present a menu with options to:
   - List available interview contexts
   - Load a context into Redis for the robot
   - Create a new context

   You can also use command-line arguments:
   ```bash
   # List available contexts
   python manage_interview_context.py --list
   
   # Load context #2 into Redis
   python manage_interview_context.py --load 2
   
   # Create a new context
   python manage_interview_context.py --new
   ```

5. **How It Works**:
   - Interview contexts are stored as text files in the `interview_contexts` directory
   - When you select a context, it's loaded into Redis under the key `interview_context`
   - The robot's template system reads this key to access the interview data
   - This approach keeps Redis clean and only stores what's needed for the current interview

## Interview Context Creation Process

1. The script prompts for guest information
2. It queries the Qwello API for background data on the guest
3. The data is processed through an LLM via LangChain
4. The LLM structures the information into sections like:
   - Guest background
   - Key topics
   - Talking points
   - Suggested questions
   - Potential follow-ups
   - Interview strategy
5. The structured output is saved as a text file in the `interview_contexts` directory
6. When selected, the context is loaded into Redis for the robot to access

## Notes

- This pipeline is intentionally minimal. Extend or modify as necessary.
- Ensure you have a valid Qwello API key and endpoint if running against the real service.
- Adjust request timeouts, logging, etc., based on your production needs.
- The system is designed to keep Redis clean by only storing the active interview context.

## Using Interview Data in Robot Templates

In your robot's Jinja2 templates, you can access the interview data like this:

```
{% set guest_key = "interview:guest:" + guest_name|lower|replace(" ", "_") %}

Hello, I'm a robot, and I'll be interviewing {{ guest_name }} today.

{% if redis_get(guest_key) %}
I've prepared some questions based on your background and expertise.
{% endif %}
```

## Notes

- This pipeline is intentionally minimal. Extend or modify as necessary.
- Ensure you have a valid Qwello API key and endpoint if running against the real service.
- Adjust request timeouts, logging, etc., based on your production needs.
- The Redis integration makes it easy for the robot to access the interview data.
- The system is designed to be efficient by reusing existing interview briefs when available.

## Docker Redis Connection

When connecting to Redis running in a Docker container:

1. The simplest approach is to use localhost:
   ```
   REDIS_HOST=127.0.0.1
   REDIS_PORT=6379
   ```

2. This works when:
   - The Redis container is using host networking
   - The Redis container has its ports mapped to the host
   - You're running your scripts on the same machine as Docker

3. Test your Redis connection:
   ```bash
   python -m src.redis_client --list
   ```

4. If you need to find the IP of a specific Redis container:
   ```bash
   python src/find_redis_ip.py --update-env
   ``` 
