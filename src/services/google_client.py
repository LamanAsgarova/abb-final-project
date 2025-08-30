import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def configure_google_client():
    """
    Configures the Google Generative AI client with the API key
    from the environment variables.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file")

    genai.configure(api_key=api_key)
    print("Google AI Client configured successfully.")