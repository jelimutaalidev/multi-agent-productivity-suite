from dateutil import parser
from datetime import datetime
import logging
from langchain_core.messages import AIMessage, ToolMessage
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

logger = logging.getLogger(__name__)

def format_dt(dt_str: str) -> str:
    """
    Parses a datetime string and ensures it is in RFC3339 format with a timezone.
    If naive, assumes local system time.
    
    Args:
        dt_str: The datetime string to parse.
        
    Returns:
        str: The ISO 8601 formatted datetime string.
        
    Raises:
        ValueError: If the datetime string is invalid.
    """
    try:
        dt = parser.parse(dt_str)
        if dt.tzinfo is None:
            # If naive, assume local time
            dt = dt.astimezone()
        return dt.isoformat()
    except Exception as e:
        logger.error(f"Error parsing datetime string '{dt_str}': {e}")
        raise ValueError(f"Invalid datetime format: {dt_str}. Error: {e}")

console = Console()

def print_agent_step(message):
    """
    Prints the agent step details in a formatted way using rich.
    """
    if isinstance(message, AIMessage):
        if message.tool_calls:
            for tool_call in message.tool_calls:
                # Create a formatted string for arguments
                args_str = "\n".join([f"{k}: {v}" for k, v in tool_call['args'].items()])
                
                content = Text()
                content.append(f"Tool Call: {tool_call['name']}\n", style="bold cyan")
                content.append(f"ID: {tool_call['id']}\n", style="dim")
                content.append("\nArguments:\n", style="bold yellow")
                content.append(args_str)
                
                console.print(Panel(content, title="[bold blue]🤖 Assistant Tool Request[/]", border_style="blue"))
        
        if message.content:
            console.print(Panel(message.content, title="[bold blue]🤖 Assistant Message[/]", border_style="blue"))
            
    elif isinstance(message, ToolMessage):
        content = Text(f"{message.content}", style="green")
        console.print(Panel(content, title=f"[bold green]🔧 Tool Output: {message.name}[/]", border_style="green"))
