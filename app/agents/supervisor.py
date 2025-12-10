import logging
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langgraph.types import Command

from app.agents.base import BaseAgent
from app.agents.calendar import CalendarAgent
from app.agents.email import EmailAgent
from app.core.context import AgentContext
from app.core.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)

# Initialize sub-agents - REMOVED GLOBAL STATE
# calendar_agent = CalendarAgent()
# email_agent = EmailAgent()

class SupervisorAgent(BaseAgent):
    def __init__(self, calendar_agent: BaseAgent, email_agent: BaseAgent):
        self.calendar_agent = calendar_agent
        self.email_agent = email_agent
        super().__init__()

    def _create_agent_executor(self):
        system_prompt = PromptLoader.get_prompt("supervisor")

        # Define tools dynamically to use instance attributes
        @tool
        def schedule_event(request: str) -> str:
            """
            Schedule calendar events using natural language.
            Use this when the user wants to create, modify, or check calendar appointments.
            Handles date/time parsing, availability checking, and event creation.
            
            Input: Natural language scheduling request (e.g., 'meeting with design team next Tuesday at 2pm')
            """
            return self.calendar_agent.invoke(request)

        @tool
        def manage_email(request: str, runtime: ToolRuntime[AgentContext]) -> str:
            """
            Send emails using natural language.
            Use this when the user wants to send notifications, reminders, or any email communication.
            Handles recipient extraction, subject generation, and email composition.
            
            Input: Natural language email request (e.g., 'send them a reminder about the meeting')
            OR approval commands: 'Approve', 'Reject', 'Edit: [changes]'
            """
            # Extract context from runtime
            context = runtime.context
            
            # Simple heuristic to detect approval/rejection
            # In a real app, we might check the agent state or use a separate tool.
            lower_request = request.lower()
            
            if lower_request.startswith("approve"):
                command = Command(resume={"decisions": [{"type": "approve"}]})
                return self.email_agent.resume(command, context=context)
                
            elif lower_request.startswith("reject"):
                reason = request[6:].strip() or "Rejected by user"
                command = Command(resume={"decisions": [{"type": "reject", "message": reason}]})
                return self.email_agent.resume(command, context=context)
                
            elif lower_request.startswith("edit"):
                # Treat "Edit" as a "Reject" with feedback.
                # This prompts the EmailAgent to regenerate the draft with the new instructions.
                instructions = request[5:].strip()
                if not instructions:
                     return "Please provide instructions on what to edit (e.g., 'Edit: Change subject to...')"
                
                feedback = f"User requested changes: {instructions}. Please update the email draft and try again."
                command = Command(resume={"decisions": [{"type": "reject", "message": feedback}]})
                return self.email_agent.resume(command, context=context)
            
            try:
                # Normal invocation
                result = self.email_agent.invoke(request, context=context)
                
                # Check for interrupt
                # Result might be a list/tuple of Interrupt objects
                interrupt_value = None
                if isinstance(result, (list, tuple)) and len(result) > 0:
                    first_item = result[0]
                    if hasattr(first_item, "value"):
                        interrupt_value = first_item.value
                elif hasattr(result, "value"):
                     interrupt_value = result.value
                
                if interrupt_value:
                    # Format interrupt for the LLM
                    # The interrupt value contains 'action_requests'
                    if "action_requests" in interrupt_value and len(interrupt_value["action_requests"]) > 0:
                        action = interrupt_value["action_requests"][0]
                        tool_name = action.get("name")
                        args = action.get("args")
                        return f"Action required: The Email Agent wants to call '{tool_name}' with args: {args}. Please ask the user to 'Approve', 'Reject', or 'Edit'."
                
                return str(result)
            except Exception as e:
                logger.error(f"Error in manage_email: {e}")
                return f"Error in manage_email: {e}"

        tools = [schedule_event, manage_email]

        agent = create_agent(
            self.llm,
            tools=tools,
            system_prompt=system_prompt,
            checkpointer=self.checkpointer,
            context_schema=AgentContext,
        )
        
        return agent
