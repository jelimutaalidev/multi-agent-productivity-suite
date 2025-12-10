import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from app.core.config import config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def authenticate_google_services():
    """
    Authenticates the user with Google APIs (Calendar, Gmail, etc.).
    
    Returns:
        creds: The authenticated Google OAuth2 credentials.
    """
    creds = None
    
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists(config.TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.SCOPES)
        except Exception as e:
            logger.error(f"Error loading credentials from {config.TOKEN_FILE}: {e}")
            # If loading fails, we might want to re-authenticate or just let creds be None
            creds = None

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                logger.info("Refreshing expired credentials...")
                creds.refresh(Request())
            except Exception as e:
                logger.error(f"Error refreshing credentials: {e}")
                creds = None
        
        if not creds:
            try:
                logger.info("Initiating new authentication flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.CREDENTIALS_FILE, config.SCOPES
                )
                creds = flow.run_local_server(port=0)
            except Exception as e:
                logger.error(f"Error during authentication flow: {e}")
                raise RuntimeError(f"Failed to authenticate: {e}")

        # Save the credentials for the next run
        try:
            with open(config.TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
            logger.info(f"Credentials saved to {config.TOKEN_FILE}")
        except Exception as e:
            logger.error(f"Error saving credentials to {config.TOKEN_FILE}: {e}")

    return creds
