import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.tools.email import send_email

@patch('app.tools.email.get_gmail_service')
def test_send_email(mock_get_service):
    print("Testing send_email...")
    
    # Mock the service and the send execution
    mock_service = MagicMock()
    mock_users = mock_service.users.return_value
    mock_messages = mock_users.messages.return_value
    mock_send = mock_messages.send.return_value
    mock_send.execute.return_value = {'id': '12345'}
    
    mock_get_service.return_value = mock_service
    
    try:
        result = send_email.invoke({
            "to": "test@example.com",
            "subject": "Test Subject",
            "body": "Test Body"
        })
        print(f"Result: {result}")
        assert "Email sent!" in result
        assert "Message ID: 12345" in result
    except Exception as e:
        pytest.fail(f"Error calling send_email: {e}")

if __name__ == "__main__":
    test_send_email()
