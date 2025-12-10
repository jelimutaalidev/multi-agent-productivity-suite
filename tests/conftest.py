import pytest
import unittest
from unittest.mock import MagicMock
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def mock_llm():
    """Mock the ChatGoogleGenerativeAI class."""
    with unittest.mock.patch('app.agents.base.ChatGoogleGenerativeAI') as MockLLM:
        mock_instance = MockLLM.return_value
        yield mock_instance

@pytest.fixture
def mock_calendar_service():
    """Mock the Google Calendar service."""
    with unittest.mock.patch('app.tools.calendar.get_calendar_service') as mock_get_service:
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        yield mock_service

@pytest.fixture
def mock_gmail_service():
    """Mock the Gmail service."""
    with unittest.mock.patch('app.tools.email.get_gmail_service') as mock_get_service:
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        yield mock_service

@pytest.fixture
def mock_prompt_loader():
    """Mock the PromptLoader to return dummy prompts."""
    with unittest.mock.patch('app.core.prompt_loader.PromptLoader') as MockLoader:
        # Mock get_prompt to return a simple string
        MockLoader.get_prompt.return_value = "Mock Prompt"
        yield MockLoader
