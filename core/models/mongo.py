from typing import List, Optional
from beanie import Document, Indexed
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class Rule(BaseModel):
    id: str
    value: str


class Goal(BaseModel):
    id: str
    value: str


class Agent(Document):
    name: str
    type: str
    contact_type: Optional[str] = None
    rules: List[Rule] = Field(default_factory=list)
    goals: List[Goal] = Field(default_factory=list)
    behavior: Optional[str] = None
    description: Optional[str] = None

    class Settings:
        name = "agents"


class UniversalRule(Document):
    value: str

    class Settings:
        name = "universal_rules"


class Metrics(BaseModel):
    summary: Optional[str] = None
    next_step: Optional[str] = None
    score: Optional[float] = None


class Contact(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class Conversation(Document):
    contact_id: Indexed(str)
    agent_ids: List[str] = Field(default_factory=list)
    last_response: Optional[str] = None
    response_id: Optional[str] = None
    total_token: Optional[int] = None
    metrics: Optional[Metrics] = None
    set_appointment: Optional[bool] = None
    contact: Optional[Contact] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "conversations"


class Message(Document):
    conversation_id: Indexed(str)
    inbound: bool
    outbound: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "messages"
