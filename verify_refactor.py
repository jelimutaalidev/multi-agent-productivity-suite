import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

try:
    from app.core.prompt_loader import PromptLoader
    from app.agents.calendar import CalendarAgent
    from app.agents.email import EmailAgent
    from app.agents.supervisor import SupervisorAgent
    
    print("Imports successful.")
    
    # Test Prompt Loading
    print("Testing PromptLoader...")
    calendar_prompt = PromptLoader.get_prompt("calendar", today="2024-01-01")
    assert "2024-01-01" in calendar_prompt
    print("Calendar prompt loaded successfully.")
    
    # Test Agent Instantiation
    print("Testing Agent Instantiation...")
    cal_agent = CalendarAgent()
    email_agent = EmailAgent()
    supervisor = SupervisorAgent(calendar_agent=cal_agent, email_agent=email_agent)
    
    print("Agents instantiated successfully.")
    
    # Verify Supervisor has access to sub-agents
    assert supervisor.calendar_agent is cal_agent
    assert supervisor.email_agent is email_agent
    print("Dependency injection verified.")
    
    print("VERIFICATION PASSED")

except Exception as e:
    print(f"VERIFICATION FAILED: {e}")
    sys.exit(1)
