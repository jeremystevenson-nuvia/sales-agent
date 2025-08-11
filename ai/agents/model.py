from typing import Optional, List
from pydantic import BaseModel, Field


class Goal(BaseModel):
    """
    Represents a goal for an AI agent.
    """
    id: Optional[str] = Field(default=None, description="Unique identifier of the goal.")
    order: Optional[int] = Field(default=None, description="Display or processing order of the goal.")
    title: Optional[str] = Field(default=None, description="Short title of the goal.")
    type: Optional[str] = Field(default=None, description="Type or category of the goal.")
    description: Optional[str] = Field(default=None, description="Detailed description of the goal.")

    class Config:
        orm_mode = True
        anystr_strip_whitespace = True
        schema_extra = {
            "example": {
                "id": "goal-001",
                "order": 1,
                "title": "Increase engagement",
                "type": "marketing",
                "description": "Drive higher user engagement through personalized recommendations."
            }
        }


class AIAgent(BaseModel):
    """
    Represents an AI agent with defined goals, rules, and behaviors.
    """
    id: Optional[str] = Field(default=None, description="Unique identifier of the AI agent.")
    name: Optional[str] = Field(default=None, description="Name of the AI agent.")
    description: Optional[str] = Field(default=None, description="Description of the AI agent.")
    goals: Optional[List[Goal]] = Field(default=None, description="List of goals associated with the agent.")
    goals_str: Optional[str] = Field(default=None, description="Stringified representation of the goals.")
    rules: Optional[str] = Field(default=None, description="Operational rules for the AI agent.")
    behavior: Optional[str] = Field(default=None, description="Behavioral description or patterns.")
    agent_type: Optional[str] = Field(default=None, description="Type of AI agent.")

    class Config:
        orm_mode = True
        anystr_strip_whitespace = True
        schema_extra = {
            "example": {
                "id": "agent-001",
                "name": "Sales Assistant",
                "description": "AI agent for handling sales conversations and booking appointments.",
                "goals": [
                    {
                        "id": "goal-001",
                        "order": 1,
                        "title": "Book more appointments",
                        "type": "sales",
                        "description": "Increase appointment bookings through proactive engagement."
                    }
                ],
                "goals_str": "Book more appointments; Improve response time",
                "rules": "Follow company policy and script.",
                "behavior": "Friendly and persuasive.",
                "agent_type": "sales"
            }
        }
