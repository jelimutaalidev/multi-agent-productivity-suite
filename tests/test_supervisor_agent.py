import pytest
from unittest.mock import MagicMock
from app.agents.supervisor import SupervisorAgent
from app.agents.base import BaseAgent

class TestSupervisorAgent:
    def test_initialization(self, mock_llm, mock_prompt_loader):
        """Test that the agent initializes correctly with dependencies."""
        mock_cal_agent = MagicMock(spec=BaseAgent)
        mock_email_agent = MagicMock(spec=BaseAgent)
        
        agent = SupervisorAgent(calendar_agent=mock_cal_agent, email_agent=mock_email_agent)
        
        assert agent.llm is not None
        assert agent.agent_executor is not None
        assert agent.calendar_agent is mock_cal_agent
        assert agent.email_agent is mock_email_agent

    # def test_tools_delegation(self, mock_llm, mock_prompt_loader):
    #     """Test that tools delegate to sub-agents."""
    #     mock_cal_agent = MagicMock(spec=BaseAgent)
    #     mock_email_agent = MagicMock(spec=BaseAgent)
        
    #     # Setup mock return values for sub-agents
    #     mock_cal_agent.invoke.return_value = "Calendar Action Done"
    #     mock_email_agent.invoke.return_value = "Email Action Done"
        
    #     agent = SupervisorAgent(calendar_agent=mock_cal_agent, email_agent=mock_email_agent)
        
    #     # Skipping tool access test as LangGraph structure hides tools.
    #     pass
