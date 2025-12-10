import sys
import os
from unittest.mock import MagicMock
from langgraph.types import Command

# Add project root to path
sys.path.append(os.getcwd())

from app.agents.email import EmailAgent
from app.core.context import AgentContext

def test_email_hitl():
    print("Initializing EmailAgent...", flush=True)
    
    # Mock Gmail service
    import app.tools.email
    mock_gmail = MagicMock()
    mock_gmail.users().messages().send().execute.return_value = {"id": "mock_msg_id"}
    app.tools.email.get_gmail_service = MagicMock(return_value=mock_gmail)
    
    # Mock print_agent_step
    import app.core.utils
    app.core.utils.print_agent_step = MagicMock()
    
    agent = EmailAgent()
    print("EmailAgent initialized.", flush=True)
    
    # 1. Send Request
    request = "Send an email to test@example.com with subject 'Test' and body 'Hello'"
    print(f"\n--- Step 1: Sending Request: {request} ---", flush=True)
    
    try:
        # We need to pass a thread_id for persistence
        # BaseAgent.invoke uses "default" thread_id.
        result = agent.invoke(request)
        print(f"Result type: {type(result)}", flush=True)
        print(f"Result: {result}", flush=True)
        
        if isinstance(result, dict) and "__interrupt__" in result: # BaseAgent.invoke returns step["__interrupt__"] if found
             print("SUCCESS: Interrupt received.", flush=True)
             interrupt_value = result["value"] # Access the interrupt value
             print(f"Interrupt value: {interrupt_value}", flush=True)
        else:
             print("FAILURE: No interrupt received. Result was:", result, flush=True)
             return

    except Exception as e:
        print(f"Error in Step 1: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return

    # 2. Resume with Approve
    print("\n--- Step 2: Resuming with Approve ---", flush=True)
    command = Command(resume={"decisions": [{"type": "approve"}]})
    
    try:
        # BaseAgent.resume uses "default" thread_id, so it should match.
        result = agent.resume(command)
        print(f"Result type: {type(result)}", flush=True)
        print(f"Result: {result}", flush=True)
        
        if "sent" in str(result).lower():
            print("SUCCESS: Email sent.", flush=True)
        else:
            print("FAILURE: Email not confirmed sent.", flush=True)
            
    except Exception as e:
        print(f"Error in Step 2: {e}", flush=True)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_email_hitl()
