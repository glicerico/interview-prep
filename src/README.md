# Desi Interview Preparation Pipeline

This folder provides a Python-based pipeline that fetches background data from the Qwello API, processes it through an LLM using LangChain, and generates a structured interview prompt for the humanoid robot Desi to use during interviews.

## Contents

1. **prepare_guest_prompt.py**  
   The main Python script that:
   - Queries the Qwello API for guest information
   - Processes the response through an LLM (via LangChain)
   - Creates a structured interview prompt file

2. **requirements.txt**  
   Dependencies for the pipeline.

3. **.env.example**  
   Shows how to store environment variables like API keys.

## Usage

1. **Install Dependencies**:
   ```bash
   cd desi_pipeline
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Set Up Environment Variables**:  
   - Copy `.env.example` to `.env`.  
   - Fill in your Qwello API key and OpenAI API key in `.env`.

3. **Run the Script**:
   ```bash
   python prepare_guest_prompt.py "<GUEST_NAME>" "<FOCUS_AREAS>"
   ```
   Example:
   ```bash
   python prepare_guest_prompt.py "Dr. Jane Smith" "AI ethics, robotics"
   ```

4. **Check the Result**:
   - A file named `prompt_for_desi.txt` is created in the current directory.
   - This file contains a structured interview guide processed by an LLM.
   - Provide `prompt_for_desi.txt` to Desi's system prior to the interview.

## How It Works

1. The script sends the guest name and focus areas to the Qwello API
2. Qwello returns a 1-2 page text with context about the guest
3. The text is sent to an LLM (default: GPT-4) through LangChain
4. The LLM structures the information into sections like:
   - Guest background
   - Key topics
   - Talking points
   - Suggested questions
   - Potential follow-ups
   - Interview strategy
5. The structured output is saved as a text file for Desi to use

## Notes

- You can modify the LLM prompt template in the script to adjust the output format.
- The default model is set to GPT-4, but you can change it to other models.
- Ensure you have valid API keys for both Qwello and your chosen LLM provider.

## Notes

- This pipeline is intentionally minimal. Extend or modify as necessary.
- Ensure you have a valid Qwello API key and endpoint if running against the real service.
- Adjust request timeouts, logging, etc., based on your production needs. 