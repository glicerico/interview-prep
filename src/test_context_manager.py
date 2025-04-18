#!/usr/bin/env python3
"""
Test script for the interview context management system.

This script tests:
1. Creating new interview contexts using mock Qwello data
2. Listing available contexts
3. Loading contexts into Redis
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path
from unittest import mock
from dotenv import load_dotenv

# Import the modules we want to test
from qwello_mock import MockQwelloAPI
from prepare_guest_prompt import prepare_guest_prompt
from manage_interview_context import (
    ensure_contexts_dir, 
    list_available_contexts,
    load_context_to_redis,
    create_new_context,
    CONTEXTS_DIR
)
from redis_client import RedisClient


class TestContextManager:
    """Test class for the interview context management system"""
    
    def __init__(self):
        self.original_contexts_dir = CONTEXTS_DIR
        self.temp_dir = None
        self.mock_qwello = MockQwelloAPI()
        self.redis_client = RedisClient()
        
    def setup(self):
        """Set up the test environment"""
        # Create a temporary directory for test contexts
        self.temp_dir = Path(tempfile.mkdtemp())
        # Monkey patch the CONTEXTS_DIR in manage_interview_context
        global CONTEXTS_DIR
        CONTEXTS_DIR = self.temp_dir
        
        # Set up mock for requests.post to intercept Qwello API calls
        self.setup_request_mock()
        
        print("🔧 Test setup complete")
        print(f"Using temporary directory: {self.temp_dir}")
        
    def teardown(self):
        """Clean up after tests"""
        # Remove the temporary directory
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            
        # Restore the original CONTEXTS_DIR
        global CONTEXTS_DIR
        CONTEXTS_DIR = self.original_contexts_dir
        
        # Remove test data from Redis
        self.redis_client.client.delete('interview_context')
        
        # Restore the original requests.post
        if hasattr(self, 'original_post'):
            import requests
            requests.post = self.original_post
            
        print("🧹 Test cleanup complete")
        
    def setup_request_mock(self):
        """Set up mock for requests.post to use MockQwelloAPI"""
        import requests
        self.original_post = requests.post
        
        def mock_post(url, headers=None, json=None, timeout=None, **kwargs):
            """Mock implementation of requests.post that uses our MockQwelloAPI"""
            if "qwello" in url.lower():
                # If calling Qwello API, use our mock
                mock_response = self.mock_qwello.make_request(url, json, headers)
                
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
                return self.original_post(url, headers=headers, json=json, timeout=timeout, **kwargs)
        
        # Apply the monkey patch
        requests.post = mock_post
    
    def test_create_context(self):
        """Test creating a new interview context"""
        print("\n🧪 Testing context creation...")
        
        # Test guests
        test_guests = [
            ("Bernie Sanders", "Healthcare reform, Income inequality"),
            ("Jane Goodall", "Wildlife conservation, Chimpanzee behavior"),
            ("Elon Musk", "Space exploration, Electric vehicles")
        ]
        
        created_files = []
        
        for guest_name, focus_areas in test_guests:
            # Create a filename-safe version of the guest name
            safe_name = guest_name.lower().replace(' ', '_')
            output_file = self.temp_dir / f"{safe_name}.txt"
            
            print(f"Creating context for {guest_name}...")
            
            # Call prepare_guest_prompt directly (bypassing the input prompts)
            prepare_guest_prompt(
                guest_name=guest_name,
                focus_areas=focus_areas,
                output_file=str(output_file)
            )
            
            # Verify the file was created
            assert output_file.exists(), f"Context file for {guest_name} was not created"
            created_files.append(output_file)
            
            # Verify the file has content
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert len(content) > 100, f"Context file for {guest_name} has insufficient content"
                
            print(f"✅ Successfully created context for {guest_name}")
            
        return created_files
    
    def test_list_contexts(self):
        """Test listing available contexts"""
        print("\n🧪 Testing context listing...")
        
        # First, create some test contexts
        created_files = self.test_create_context()
        
        # Now test listing them
        contexts = list_available_contexts()
        
        # Verify we got the expected number of contexts
        assert len(contexts) == len(created_files), f"Expected {len(created_files)} contexts, got {len(contexts)}"
        
        # Verify each context is in the list
        for i, (_, guest_name, file_path) in enumerate(contexts, 1):
            print(f"{i}. {guest_name} - {file_path}")
            
        print(f"✅ Successfully listed {len(contexts)} contexts")
        return contexts
    
    def test_load_context(self):
        """Test loading a context into Redis"""
        print("\n🧪 Testing context loading...")
        
        # First, list available contexts
        contexts = self.test_list_contexts()
        
        # Choose the first context
        if not contexts:
            print("❌ No contexts available to load")
            return False
            
        _, guest_name, file_path = contexts[0]
        
        # Load it into Redis
        print(f"Loading context for {guest_name}...")
        load_context_to_redis(file_path)
        
        # Verify it was loaded into Redis
        redis_value = self.redis_client.client.get('interview_context')
        assert redis_value is not None, "Context was not loaded into Redis"
        
        # Verify the content matches the file
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read().strip()
            redis_content = redis_value.decode('utf-8')
            assert redis_content == file_content, "Redis content does not match file content"
            
        print(f"✅ Successfully loaded context for {guest_name} into Redis")
        return True
    
    def run_tests(self):
        """Run all tests"""
        try:
            self.setup()
            
            # Test the full workflow
            print("\n🚀 Starting tests for interview context management")
            
            # We'll test each function individually, but in a sequence that
            # builds on previous tests (create -> list -> load)
            self.test_load_context()
            
            print("\n✨ All tests passed!")
            return 0
            
        except AssertionError as e:
            print(f"\n❌ Test failed: {e}")
            return 1
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            return 1
        finally:
            self.teardown()


def main():
    """Main function to run the tests"""
    # Load environment variables
    load_dotenv()
    
    # Verify we have OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is not set.")
        print("Please create a .env file with your OpenAI API key to run this test.")
        return 1
    
    # Run the tests
    test_runner = TestContextManager()
    return test_runner.run_tests()


if __name__ == "__main__":
    sys.exit(main()) 