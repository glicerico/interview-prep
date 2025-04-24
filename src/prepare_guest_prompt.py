import os
import requests
import sys
import argparse
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

def prepare_guest_prompt(guest_name: str, focus_areas: str, output_file: str = "interview_briefing.txt", store_in_redis: bool = False):
    """
    Creates a text-based briefing prompt for the robot based on Qwello data,
    processed through an LLM to create a more structured interview guide.
    
    :param guest_name: The name of the guest being interviewed.
    :param focus_areas: Comma-separated or descriptive string of the guest's primary topics.
    :param output_file: The file to which the resulting briefing prompt should be written.
    :param store_in_redis: Deprecated parameter, kept for backward compatibility.
    """
    print(f"[INFO] Preparing new interview brief for {guest_name}...")
    
    try:
        # 1) Load environment variables for Qwello and LLM
        load_dotenv()
        qwello_api_key = os.getenv('QWELLO_API_KEY', 'YOUR_QWELLO_API_KEY')
        openai_api_key = os.getenv('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY')
        qwello_url = "https://api.qwello.com/v1/query"  # Example endpoint

        # 2) Build the request payload for Qwello
        payload = {
            "prompt": f"""
I need to prepare for an interview where a humanoid robot will be interviewing {guest_name}, who is known for their work in {focus_areas}.
Please research this person and provide comprehensive background information including:
- Their professional background and major achievements
- Their expertise and contributions to {focus_areas}
- Recent work, publications, or notable projects
- Any controversies or challenges they've faced
- Their communication style and interview preferences (if known)
- Any information that would be particularly relevant for a robot interviewer to know

Format the information in a clear, detailed manner that would help prepare for an in-depth interview conducted by a robot.
""",
            # Additional query parameters as needed
        }
        headers = {
            "Authorization": f"Bearer {qwello_api_key}",
            "Content-Type": "application/json"
        }

        # 3) Make the request to Qwello
        try:
            response = requests.post(qwello_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            # For Qwello response with no specific JSON format, assume it returns text directly
            # If Qwello actually returns JSON, adjust this accordingly
            if response.headers.get('Content-Type', '').startswith('application/json'):
                qwello_data = response.json()
                if isinstance(qwello_data, dict):
                    qwello_text = qwello_data.get('text', '') or qwello_data.get('content', '')
                else:
                    qwello_text = str(qwello_data)
            else:
                qwello_text = response.text
                
        except requests.exceptions.RequestException as e:
            print(f"[WARNING] Error connecting to Qwello API: {e}")
            print("[INFO] Using fallback information for the guest...")
            
            # Create a fallback text with basic information about the guest
            qwello_text = f"""
Guest: {guest_name}
Focus Areas: {focus_areas}

This guest is known for their work in {focus_areas}. 
Please use your knowledge to provide relevant background information and insights about {guest_name}.
"""

        # 4) Initialize the LLM and prepare prompt
        try:
            llm = ChatOpenAI(model="gpt-4", temperature=0.2, api_key=openai_api_key)
            
            # Create template for LLM to structure the interview preparation
            prompt_template = PromptTemplate(
                input_variables=["guest_name", "focus_areas", "qwello_text"],
                template="""
You are an expert at interview briefing, who will help a humanoid robot
prepare to conduct an interview to a human guest.
The robot needs a well-structured prompt with context to
guide her interview with a guest.

The guest information is as follows:
Guest Name: {guest_name}
Focus Areas: {focus_areas}

Below is background information from the Qwello API:
{qwello_text}

Please create a structured interview prompt with the following sections:
1. GUEST BACKGROUND: A concise summary of who the guest is and their achievements.
2. KEY TOPICS: 3-5 specific topics that would be interesting to explore, based on the guest's expertise.
3. TALKING POINTS: Key facts, quotes, or insights for each topic that the interviewer should be aware of.
4. SUGGESTED QUESTIONS: 2-3 thoughtful, open-ended questions for each topic that would lead to engaging conversation.
5. POTENTIAL FOLLOW-UPS: Possible directions the conversation might go based on common responses.
6. INTERVIEW STRATEGY: Brief guidance on tone, pace, and approach for this specific guest.

Format the output in a clear, structured way that an interviewer can easily process during the interview.
"""
            )
            
            # Create and run the chain using the new pipe syntax
            chain = prompt_template | llm
            
            # Invoke the chain with our input variables
            result = chain.invoke({
                "guest_name": guest_name,
                "focus_areas": focus_areas,
                "qwello_text": qwello_text
            })
            
            # Extract the result (result is the direct output from the LLM)
            final_prompt = result.content

            # 5) Write the structured prompt to a file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(final_prompt.strip() + "\n")

            print(f"[INFO] Structured interview prompt created: {output_file}")
            return final_prompt
            
        except Exception as e:
            print(f"[ERROR] Error processing with LLM: {e}")
            print("[INFO] Creating a basic interview prompt without LLM...")
            
            # Create a basic interview prompt without LLM
            basic_prompt = f"""
GUEST BACKGROUND:
{guest_name} is known for their work in {focus_areas}.

KEY TOPICS:
1. {focus_areas.split(',')[0] if ',' in focus_areas else focus_areas}
2. Career and achievements
3. Future plans

SUGGESTED QUESTIONS:
1. Could you tell us about your background and how you got started in {focus_areas}?
2. What are some of the most important projects you've worked on?
3. What are you currently working on or planning for the future?

INTERVIEW STRATEGY:
Be respectful and listen actively. Ask follow-up questions based on the guest's responses.
            """
            
            # Write the basic prompt to a file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(basic_prompt.strip() + "\n")
                
            print(f"[INFO] Basic interview prompt created: {output_file}")
            return basic_prompt
            
    except Exception as e:
        print(f"[ERROR] Unexpected error preparing interview brief: {e}")
        print("[INFO] Interview brief could not be created.")
        return None


if __name__ == "__main__":
    """
    Example usage: 
    python prepare_guest_prompt.py "John Doe" "AI, NLP"
    """
    parser = argparse.ArgumentParser(description="Prepare an interview brief for a guest.")
    parser.add_argument("guest_name", help="Name of the guest")
    parser.add_argument("focus_areas", help="Comma-separated areas of focus")
    parser.add_argument("--output", "-o", default="interview_briefing.txt", 
                        help="Output file name (default: interview_briefing.txt)")
    
    args = parser.parse_args()
    
    prepare_guest_prompt(
        guest_name=args.guest_name,
        focus_areas=args.focus_areas,
        output_file=args.output,
        store_in_redis=False  # Never store in Redis directly
    ) 