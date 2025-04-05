"""
Test script for the interview preparation pipeline using a mock Qwello API
and the real OpenAI API for LLM processing.
"""

import os
import sys
from dotenv import load_dotenv
from qwello_mock import MockQwelloAPI
from prepare_guest_prompt import prepare_guest_prompt

# Path for test output
TEST_OUTPUT_DIR = "test_output"


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
    # Ensure output directory exists
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(TEST_OUTPUT_DIR, output_filename)
    
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
            # For all other requests (like OpenAI), use the real implementation
            return original_post(url, headers=headers, json=json, timeout=timeout, **kwargs)
    
    # Apply the monkey patch
    requests.post = mock_post
    
    try:
        # Call the actual function that prepares the interview prompt
        prepare_guest_prompt(guest_name, focus_areas, output_path)
        print(f"✅ Successfully created interview brief for {guest_name} at {output_path}")
        return output_path
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
    
    # Test with pre-defined guests
    test_with_mock_qwello(
        "Bernie Sanders", 
        "Healthcare reform, Income inequality, Climate policy", 
        "bernie_sanders_interview.txt"
    )
    
    test_with_mock_qwello(
        "Jane Goodall", 
        "Wildlife conservation, Chimpanzee behavior, Environmental education", 
        "jane_goodall_interview.txt"
    )
    
    test_with_mock_qwello(
        "Rosa Luxemburg", 
        "Revolutionary theory, Democratic socialism, Anti-imperialism", 
        "rosa_luxemburg_interview.txt"
    )
    
    # Test with an unknown guest (will generate generic data)
    test_with_mock_qwello(
        "Dr. Alex Johnson", 
        "Quantum computing, Machine learning ethics", 
        "alex_johnson_interview.txt"
    )
    
    print("\n✨ All tests completed. Check the test_output directory for results.")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 