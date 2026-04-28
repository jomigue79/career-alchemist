import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Configure the SDK
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

def test_connection():
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Simple prompt to verify connectivity
        response = model.generate_content("Say 'Hello World! System online.'")
        
        print("-" * 30)
        print("GEMINI API STATUS: SUCCESS")
        print(f"Response: {response.text}")
        print("-" * 30)
    except Exception as e:
        print("-" * 30)
        print("GEMINI API STATUS: FAILED")
        print(f"Error: {str(e)}")
        print("-" * 30)

if __name__ == "__main__":
    test_connection()