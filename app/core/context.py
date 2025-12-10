from pydantic import BaseModel, Field

class AgentContext(BaseModel):
    """
    Context shared across agents.
    """
    user_name: str = Field(default="User", description="The name of the user interacting with the agent.")
