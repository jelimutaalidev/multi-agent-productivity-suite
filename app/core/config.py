import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the application."""
    
    # Google API Scopes
    SCOPES = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/gmail.send"
    ]
    
    # Credentials File Paths
    CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", "credentials.json")
    TOKEN_FILE = os.getenv("TOKEN_FILE", "token.json")
    
    # Model Configuration
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash-preview-09-2025")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))
    
    # Application Settings
    CALENDAR_ID = "primary"
    
config = Config()
