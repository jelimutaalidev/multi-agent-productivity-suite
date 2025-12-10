import sys
import os
from unittest.mock import MagicMock
from langgraph.types import Command

# Add project root to path
sys.path.append(os.getcwd())

from app.agents.email import EmailAgent
from app.core.context import AgentContext

def test_email_edit_flow():
    print("Initializing EmailAgent...", flush=True)
    
    # Mock Gmail service
    import app.tools.email
    mock_gmail = MagicMock()
    mock_gmail.users().messages().send().execute.return_value = {"id": "mock_msg_id"}
    app.tools.email.get_gmail_service = MagicMock(return_value=mock_gmail)
    
    # Mock print_agent_step
    # import app.core.utils
    # app.core.utils.print_agent_step = MagicMock()
    
    agent = EmailAgent()
    print("EmailAgent initialized.", flush=True)
    
    # 1. Send Request
    request = "Send an email to test@example.com with subject 'Test' and body 'Original Body'"
    print(f"\n--- Step 1: Sending Request: {request} ---", flush=True)
    
    try:
        result = agent.invoke(request)
        print(f"DEBUG: Result type: {type(result)}", flush=True)
        print(f"DEBUG: Result: {result}", flush=True)

        interrupt_value = None
        if isinstance(result, (list, tuple)) and len(result) > 0:
            first_item = result[0]
            if hasattr(first_item, "value"):
                interrupt_value = first_item.value
        elif hasattr(result, "value"):
                interrupt_value = result.value

        if interrupt_value:
             print("SUCCESS: Interrupt received (Draft 1).", flush=True)
             val = interrupt_value["action_requests"][0]["args"]
             print(f"Draft 1 Body: {val.get('body')}", flush=True)
        else:
             print("FAILURE: No interrupt received.", flush=True)
             return

    except Exception as e:
        print(f"Error in Step 1: {e}", flush=True)
        return

    # 2. Resume with Edit (simulated as Reject with message)
    print("\n--- Step 2: Resuming with Edit (Reject + Feedback) ---", flush=True)
    feedback = "User requested changes: Change body to 'Edited Body'. Please update the email draft and try again."
    command = Command(resume={"decisions": [{"type": "reject", "message": feedback}]})
    
    try:
        # This should trigger the agent to think, see the rejection, and call the tool again with new args
        result = agent.resume(command)
        
        # We expect ANOTHER interrupt with the new draft
        # We expect ANOTHER interrupt with the new draft
        print(f"DEBUG: Result type: {type(result)}", flush=True)
        print(f"DEBUG: Result: {result}", flush=True)

        interrupt_value = None
        if isinstance(result, (list, tuple)) and len(result) > 0:
            first_item = result[0]
            if hasattr(first_item, "value"):
                interrupt_value = first_item.value
        elif hasattr(result, "value"):
                interrupt_value = result.value

        if interrupt_value:
             print("SUCCESS: Interrupt received (Draft 2).", flush=True)
             val = interrupt_value["action_requests"][0]["args"]
             print(f"Draft 2 Body: {val.get('body')}", flush=True)
             
             if "Edited Body" in val.get('body', ''):
                 print("SUCCESS: Draft 2 contains requested changes.", flush=True)
             else:
                 print("WARNING: Draft 2 might not contain changes. Check LLM output.", flush=True)
                 
        else:
             print(f"FAILURE: Expected second interrupt, got: {result}", flush=True)
             return
            
    except Exception as e:
        print(f"Error in Step 2: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return

    # 3. Approve Draft 2
    print("\n--- Step 3: Approving Draft 2 ---", flush=True)
    command = Command(resume={"decisions": [{"type": "approve"}]})
    
    try:
        result = agent.resume(command)
        if "sent" in str(result).lower():
            print("SUCCESS: Email sent.", flush=True)
        else:
            print("FAILURE: Email not confirmed sent.", flush=True)
            
    except Exception as e:
        print(f"Error in Step 3: {e}", flush=True)

if __name__ == "__main__":
    test_email_edit_flow()
