from pydantic import BaseModel, Field
import logging
import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from langchain.tools import tool
from app.core.auth import authenticate_google_services

logger = logging.getLogger(__name__)

def get_gmail_service():
    """Returns an authenticated Gmail service resource."""
    creds = authenticate_google_services()
    service = build("gmail", "v1", credentials=creds)
    return service

class SendEmailInput(BaseModel):
    to: str = Field(description="Email address of the recipient")
    subject: str = Field(description="Subject of the email")
    body: str = Field(description="Body content of the email")

@tool(args_schema=SendEmailInput)
def send_email(to: str, subject: str, body: str) -> str:
    """
    Send an email via Gmail.
    """
    logger.info(f"Sending email to {to} with subject '{subject}'")
    service = get_gmail_service()
    
    try:
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        body = {"raw": raw_message}
        
        sent_message = service.users().messages().send(userId="me", body=body).execute()
        return f"Email sent! Message ID: {sent_message['id']}"
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return f"Error sending email: {e}"
