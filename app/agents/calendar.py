import datetime
import logging
from langchain.agents import create_agent
# from langchain.agents import AgentExecutor

from app.agents.base import BaseAgent
from app.tools.calendar import list_events, create_event, get_available_time_slots
from app.core.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)

class CalendarAgent(BaseAgent):
    def _create_agent_executor(self):
        today = datetime.date.today().isoformat()
        
        system_prompt = PromptLoader.get_prompt("calendar", today=today)

        tools = [list_events, create_event, get_available_time_slots]

        agent = create_agent(
            self.llm,
            tools=tools,
            system_prompt=system_prompt,
            checkpointer=self.checkpointer,
        )
        
        return agent
