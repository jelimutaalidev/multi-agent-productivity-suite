import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
# from langchain.agents import AgentExecutor # Removed to fix ImportError

from app.core.config import config
from app.core.utils import print_agent_step, console
from app.core.context import AgentContext

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Base class for all agents in the system.
    """
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=config.MODEL_NAME,
            temperature=config.TEMPERATURE
        )
        self.checkpointer = InMemorySaver()
        self.agent_executor = self._create_agent_executor()

    @abstractmethod
    def _create_agent_executor(self):
        """
        Create and return the agent executor.
        Must be implemented by subclasses.
        """
        pass

    def chat(self, user_input: str, context: Optional[AgentContext] = None) -> Any:
        """
        Process a user message and return the agent's response.
        """
        thread_config = {"configurable": {"thread_id": "default"}}
        
        # Default context if none provided
        if context is None:
            context = AgentContext(user_name="User")

        response_messages = []
        try:
            # Stream the response
            with console.status("[bold green]Thinking...[/]", spinner="dots"):
                for step in self.agent_executor.stream(
                    {"messages": [HumanMessage(content=user_input)]},
                    config=thread_config,
                    context=context
                ):
                    # Check for interrupts
                    if "__interrupt__" in step:
                        return step["__interrupt__"]

                    for update in step.values():
                        if update and "messages" in update:
                            for message in update["messages"]:
                                response_messages.append(message)
                                print_agent_step(message)
            
            # Return the content of the last AI message
            last_ai_message = next((m for m in reversed(response_messages) if m.type == "ai"), None)
            return last_ai_message.content if last_ai_message else "I'm not sure how to respond to that."
            
        except Exception as e:
            logger.error(f"Error during chat: {e}")
            return f"An error occurred: {e}"

    def invoke(self, user_input: str, context: Optional[AgentContext] = None) -> Any:
        """
        Programmatically invoke the agent and return the final response.
        """
        return self.chat(user_input, context=context)

    def resume(self, command: Any, context: Optional[AgentContext] = None) -> Any:
        """
        Resume the agent execution with a command (for HITL).
        """
        thread_config = {"configurable": {"thread_id": "default"}}
        if context is None:
            context = AgentContext(user_name="User")

        response_messages = []
        try:
            iterator = self.agent_executor.stream(
                command,
                config=thread_config,
                context=context
            )
            
            for step in iterator:
                if "__interrupt__" in step:
                    return step["__interrupt__"]
                
                for update in step.values():
                    if update and "messages" in update:
                        for message in update["messages"]:
                            response_messages.append(message)
                            print_agent_step(message)
            
            last_ai_message = next((m for m in reversed(response_messages) if m.type == "ai"), None)
            return last_ai_message.content if last_ai_message else "Resumed successfully."
        except Exception as e:
            logger.error(f"Error during resume: {e}")
            return f"An error occurred during resume: {e}"

    def run_interactive(self, context: Optional[AgentContext] = None):
        """
        Run the agent in an interactive CLI loop.
        """
        console.print(f"[bold blue]{self.__class__.__name__} initialized.[/] Type 'quit' to exit.")
        
        if context is None:
             # Simple prompt for name if not provided (mostly for testing individual agents)
            try:
                user_name = console.input("[bold yellow]Enter your name (default: User): [/]") or "User"
            except EOFError:
                user_name = "User"
            context = AgentContext(user_name=user_name)

        while True:
            try:
                user_input = console.input("\n[bold green]You: [/]")
                if user_input.lower() in ["quit", "exit"]:
                    console.print("[bold red]Goodbye![/]")
                    break
                
                response = self.chat(user_input, context=context)
                # console.print(f"\n[bold purple]Agent:[/]\n{response}") # Removed to avoid double printing
            except KeyboardInterrupt:
                console.print("\n[bold red]Exiting...[/]")
                break
            except EOFError:
                break
