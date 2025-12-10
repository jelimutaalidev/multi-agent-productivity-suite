import sys
import os
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.getcwd())

from app.agents.supervisor import SupervisorAgent
from app.agents.calendar import CalendarAgent
from app.agents.email import EmailAgent
from app.core.context import AgentContext

def test_hitl_flow():
    print("Initializing agents...")
    # We need to mock the services to avoid real API calls, 
    # but we want the agent logic to run.
    # So we will mock the tools inside the agents or just let them fail/mock at service level?
    # Since we modified the code to use real classes, we should probably mock the service calls 
    # like we did in unit tests, but here we want to run the full flow.
    # For simplicity, let's assume the user has credentials OR we mock the service getters globally.
    
    # Mocking service getters
    import app.tools.email
    import app.tools.calendar
    
    mock_gmail = MagicMock()
    mock_gmail.users().messages().send().execute.return_value = {"id": "mock_msg_id"}
    app.tools.email.get_gmail_service = MagicMock(return_value=mock_gmail)
    
    # Mock print_agent_step to avoid clutter
    import app.core.utils
    app.core.utils.print_agent_step = MagicMock()
    
    # Initialize agents
    cal_agent = CalendarAgent()
    email_agent = EmailAgent()
    supervisor = SupervisorAgent(calendar_agent=cal_agent, email_agent=email_agent)
    
    print("Agents initialized.")
    
    # 1. Send Email Request
    print("\n--- Step 1: Requesting Email ---")
    request = "Send an email to jeyk1ll3r05@gmail.com saying I'm done"
    print(f"User: {request}")
    
    # We use invoke. Since we are mocking LLM in unit tests usually, here we are running REAL LLM?
    # If we run real LLM, we need credentials. The user environment seems to have them (credentials.json).
    # But to be safe and deterministic, maybe we should mock the LLM responses too?
    # Mocking LLM responses for a complex multi-step flow is hard.
    # Let's try to run with REAL LLM if possible, assuming the user has set it up.
    # If not, we will fail. But the user asked to "Verify HITL flow with manual test".
    # I will create this script for the user to run, or run it myself if I can.
    
    try:
        response = supervisor.invoke(request)
        print(f"Agent Response Step 1: {response}")
        
        # Check if response asks for approval
        if "Approve" in str(response) or "approval" in str(response) or "Action required" in str(response):
            print("SUCCESS: Agent asked for approval.")
        else:
            print("WARNING: Agent did not explicitly ask for approval. Check logs.")
            
    except Exception as e:
        print(f"Error in Step 1: {e}")
        return

    # 2. Approve
    print("\n--- Step 2: Approving ---")
    approval = "Approve"
    print(f"User: {approval}")
    
    try:
        response = supervisor.invoke(approval)
        print(f"Agent Response Step 2: {response}")
        
        if "sent" in str(response).lower():
            print("SUCCESS: Email sent after approval.")
        else:
            print("WARNING: Agent did not confirm email sent.")
            
    except Exception as e:
        print(f"Error in Step 2: {e}")

if __name__ == "__main__":
    test_hitl_flow()
