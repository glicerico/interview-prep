"""
Test script for the interview preparation pipeline using a mock Qwello API
and the real OpenAI API for LLM processing.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from qwello_mock import MockQwelloAPI
from prepare_guest_prompt import prepare_guest_prompt

# Path for interview contexts - same as used by manage_interview_context.py
CONTEXTS_DIR = Path("interview_contexts")


def test_with_mock_qwello(guest_name: str, focus_areas: str, output_filename: str) -> str:
    """
    Test the interview preparation pipeline with mock Qwello data and real OpenAI.
    
    Args:
        guest_name: Name of the guest
        focus_areas: Comma-separated areas of focus
        output_filename: Name of the output file
        
    Returns:
        Path to the generated output file
    """
    # Ensure contexts directory exists
    CONTEXTS_DIR.mkdir(exist_ok=True)
    output_path = CONTEXTS_DIR / output_filename
    
    # Create mock Qwello for testing
    mock_qwello = MockQwelloAPI()
    
    # Monkey patch the requests.post function in prepare_guest_prompt
    # This is done to intercept calls to the real Qwello API
    import requests
    original_post = requests.post
    
    def mock_post(url, headers=None, json=None, timeout=None, **kwargs):
        """Mock implementation of requests.post that uses our MockQwelloAPI"""
        if "qwello" in url.lower():
            # If calling Qwello API, use our mock
            mock_response = mock_qwello.make_request(url, json, headers)
            
            # Create a mock response object that mimics requests.Response
            class MockResponse:
                def __init__(self, data):
                    self.status_code = data["status_code"]
                    self._headers = data["headers"]
                    self._json = data["json"]
                    self._text = data["text"]
                
                def json(self):
                    return self._json
                
                @property
                def text(self):
                    return self._text
                
                @property
                def headers(self):
                    return self._headers
                
                def raise_for_status(self):
                    if self.status_code >= 400:
                        raise requests.exceptions.HTTPError(f"Mock HTTP Error: {self.status_code}")
            
            return MockResponse(mock_response)
        else:
            # For all other URLs, use the real requests.post
            return original_post(url, headers=headers, json=json, timeout=timeout, **kwargs)
    
    # Apply the monkey patch
    requests.post = mock_post
    
    try:
        # Call the actual function that prepares the interview prompt
        prepare_guest_prompt(guest_name, focus_areas, str(output_path))
        print(f"✅ Successfully created interview brief for {guest_name} at {output_path}")
        return str(output_path)
    except Exception as e:
        print(f"❌ Error in test: {e}")
        raise
    finally:
        # Restore the original function
        requests.post = original_post


def main():
    """Run tests with several example guests"""
    # Load environment variables (.env file)
    load_dotenv()
    
    # Verify we have OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is not set.")
        print("Please create a .env file with your OpenAI API key to run this test.")
        return 1
    
    print("🚀 Testing interview preparation pipeline with mock Qwello data")
    print("Using real OpenAI API for LLM processing\n")
    print(f"Saving interview contexts to: {CONTEXTS_DIR}\n")
    
    # Test with pre-defined guests
    test_with_mock_qwello(
        "Bernie Sanders", 
        "Healthcare reform, Income inequality, Climate policy", 
        "bernie_sanders.txt"
    )
    
    test_with_mock_qwello(
        "Jane Goodall", 
        "Wildlife conservation, Chimpanzee behavior, Environmental education", 
        "jane_goodall.txt"
    )
    
    test_with_mock_qwello(
        "Rosa Luxemburg", 
        "Revolutionary theory, Democratic socialism, Anti-imperialism", 
        "rosa_luxemburg.txt"
    )
    
    # Test with an unknown guest (will generate generic data)
    test_with_mock_qwello(
        "Dr. Alex Johnson", 
        "Quantum computing, Machine learning ethics", 
        "alex_johnson.txt"
    )
    
    print("\n✨ All tests completed. Check the interview_contexts directory for results.")
    print("You can now use manage_interview_context.py to load these contexts for interviews.")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 