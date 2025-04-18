import os
import requests
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

def prepare_guest_prompt(guest_name: str, focus_areas: str, output_file: str = "interview_briefing.txt"):
    """
    Creates a text-based briefing prompt for the robot based on Qwello data,
    processed through an LLM to create a more structured interview guide.
    
    :param guest_name: The name of the guest being interviewed.
    :param focus_areas: Comma-separated or descriptive string of the guest's primary topics.
    :param output_file: The file to which the resulting briefing prompt should be written.
    """
    # 1) Load environment variables for Qwello and LLM
    load_dotenv()
    qwello_api_key = os.getenv('QWELLO_API_KEY', 'YOUR_QWELLO_API_KEY')
    openai_api_key = os.getenv('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY')
    qwello_url = "https://api.qwello.com/v1/query"  # Example endpoint

    # 2) Build the request payload for Qwello
    payload = {
        "guest_name": guest_name,
        "focus_areas": focus_areas
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
        raise SystemExit(f"Error connecting to Qwello API: {e}")

    # 4) Initialize the LLM and prepare prompt
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


if __name__ == "__main__":
    """
    Example usage: 
    python prepare_guest_prompt.py "John Doe" "AI, NLP"
    """
    import sys
    if len(sys.argv) < 3:
        print("Usage: python prepare_guest_prompt.py <guest_name> <focus_areas>")
        sys.exit(1)

    guest = sys.argv[1]
    focus = sys.argv[2]
    prepare_guest_prompt(guest, focus) 