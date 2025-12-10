import logging
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import dynamic_prompt, ModelRequest

from app.agents.base import BaseAgent
from app.tools.email import send_email
from app.core.context import AgentContext
from app.core.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)

@dynamic_prompt
def email_agent_prompt(request: ModelRequest) -> str:
    """Generate system prompt with user context."""
    user_name = request.runtime.context.user_name
    
    return PromptLoader.get_prompt("email", user_name=user_name)

class EmailAgent(BaseAgent):
    def _create_agent_executor(self):
        tools = [send_email]

        agent = create_agent(
            self.llm,
            tools=tools,
            middleware=[
                email_agent_prompt,
                HumanInTheLoopMiddleware(
                    interrupt_on={
                        "send_email": {
                            "allowed_decisions": ["approve", "edit", "reject"],
                        }
                    },
                    description_prefix="Email sending pending approval",
                ),
            ],
            context_schema=AgentContext,
            checkpointer=InMemorySaver(), # Use InMemorySaver for now, or self.checkpointer if it's compatible
        )
        
        return agent
