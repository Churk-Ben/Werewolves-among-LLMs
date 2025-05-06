from openai import OpenAI
import sys
import os

# Add parent directory to path to import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import API_KEY, API_URL

def test_openai_client():
    print("Testing OpenAI client initialization...")
    try:
        client = OpenAI(
            api_key=API_KEY,
            base_url=API_URL,
        )
        
        print("Client initialized successfully!")
        print("Note: Not testing API calls as the API key is a placeholder.")
        print("Test passed!")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_openai_client()