from app.agents.supervisor import SupervisorAgent
from app.agents.calendar import CalendarAgent
from app.agents.email import EmailAgent
import sys
import logging
from rich.logging import RichHandler

# Force UTF-8 encoding for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)]
)

from app.core.utils import console
from rich.panel import Panel

def main():
    console.print(Panel.fit("[bold white]Multi-Agent Productivity Suite[/]", style="bold blue", title="Welcome"))
    
    try:
        # Initialize agents with dependency injection
        calendar_agent = CalendarAgent()
        email_agent = EmailAgent()
        
        agent = SupervisorAgent(calendar_agent=calendar_agent, email_agent=email_agent)
        agent.run_interactive()
    except Exception as e:
        print(f"Failed to start the agent: {e}")

if __name__ == "__main__":
    main()
