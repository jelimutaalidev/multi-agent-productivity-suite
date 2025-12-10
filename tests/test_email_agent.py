import pytest
from unittest.mock import MagicMock
from app.agents.email import EmailAgent
from app.tools.email import send_email
from app.core.context import AgentContext

class TestEmailAgent:
    def test_initialization(self, mock_llm, mock_prompt_loader):
        """Test that the agent initializes correctly."""
        agent = EmailAgent()
        assert agent.llm is not None
        assert agent.agent_executor is not None

    def test_send_email_tool(self, mock_gmail_service):
        """Test the send_email tool."""
        # Setup mock response
        mock_gmail_service.users.return_value.messages.return_value.send.return_value.execute.return_value = {"id": "msg123"}

        # Run tool
        result = send_email.invoke({
            "to": "recipient@example.com",
            "subject": "Test Subject",
            "body": "Test Body"
        })

        # Verify
        assert "Email sent" in result
        assert "msg123" in result
        mock_gmail_service.users.return_value.messages.return_value.send.assert_called_once()
