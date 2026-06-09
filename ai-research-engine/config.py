"""
Configuration module for loading API keys from .env file
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Validate that all API keys are set
def validate_api_keys():
    """Check if all required API keys are configured"""
    required_keys = {
        "GOOGLE_API_KEY": GOOGLE_API_KEY,
        "GROQ_API_KEY": GROQ_API_KEY,
        "OPENROUTER_API_KEY": OPENROUTER_API_KEY,
    }
    
    missing_keys = [key for key, value in required_keys.items() if not value]
    
    if missing_keys:
        print(f"⚠️  Missing API keys: {', '.join(missing_keys)}")
        print("Please fill in the .env file with your API keys.")
        return False
    
    print("✅ All API keys are configured!")
    print("✅ DuckDuckGo web search ready (no API key needed)")
    return True
