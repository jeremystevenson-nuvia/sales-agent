from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class ChatbotSession(BaseModel):
    """
    Pydantic model for representing a chatbot session.
    """
    customer_id: Optional[str] = Field(
        default=None, description="Unique identifier of the customer interacting with the chatbot."
    )
    chat_id: Optional[str] = Field(
        default=None, description="Unique identifier of the chat or conversation."
    )
    agent_id: Optional[str] = Field(
        default=None, description="Identifier of the agent (human or AI) managing the conversation."
    )


    class Config:
        orm_mode = True
        anystr_strip_whitespace = True
        schema_extra = {
            "example": {
                "customer_id": "12345",
                "chat_id": "abcde12345",
                "agent_id": "agent-001"
            }
        }



class AISettings(BaseModel):
    """
    Settings for AI model configuration.
    """
    temperature: float = Field(default=0.5, description="Temperature setting for AI model output randomness.")
    model_name: str = Field(default="gpt-4.1-mini", description="Name of the AI model to use.")
    verbose: bool = Field(default=True, description="Whether to enable verbose logging.")
    use_responses_api: bool = Field(default=True, description="Whether to use the responses API for generation.")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "temperature": 0.7,
                "model_name": "gpt-4.1-mini",
                "verbose": True,
                "use_responses_api": True
            }
        }


class ConversationMetrics(BaseModel):
    """
    Metrics summarizing a chatbot conversation.
    """
    summary: str = Field(default="", description="Brief summary of the conversation.")
    set_appointment: str = Field(default="", description="Details about any appointment set in the conversation.")
    next_step: str = Field(default="", description="Planned next step in the conversation flow.")
    score: int = Field(default=0, description="Conversation score or evaluation metric.")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "summary": "Discussed dental implant benefits and scheduled consultation for Aug 20.",
                "set_appointment": "Yes - Aug 20, 2025 at 10:00 AM",
                "next_step": "Send confirmation email and directions to the Nuvia center.",
                "score": 95
            }
        }


class AIOutput(BaseModel):
    """
    AI response output including metadata and conversation metrics.
    """
    response_text: str = Field(default="", description="Main response text from the AI.")
    response_id: str = Field(default="", description="Unique identifier for the AI response.")
    total_tokens: int = Field(default=0, description="Total number of tokens used in the AI request.")
    links: List[str] = Field(default_factory=list, description="List of relevant links found or generated.")
    contact_info: Optional[Dict] = Field(default=None, description="Extracted contact information.")
    data: Optional[Dict] = Field(default=None, description="Additional structured data returned by the AI.")
    conversation_metrics: Optional[ConversationMetrics] = Field(
        default=None, description="Conversation metrics object."
    )
    errorMessage: str = Field(default="", description="Error message if the AI request failed.")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "response_text": "We can get you a brand-new smile in just 24 hours. Would you like me to reserve your free consultation for next week?",
                "response_id": "resp-2025-08-11-001",
                "total_tokens": 356,
                "links": [
                    "https://nuvia.com/dental-implants",
                    "https://nuvia.com/patient-reviews"
                ],
                "contact_info": {
                    "phone": "+1-888-888-8888",
                    "email": "info@nuvia.com"
                },
                "data": {
                    "appointment_date": "2025-08-20",
                    "appointment_time": "10:00 AM",
                    "location": "Nuvia Dental Implant Center - Salt Lake City"
                },
                "conversation_metrics": {
                    "summary": "Scheduled consultation for Aug 20.",
                    "set_appointment": "2025-08-20 10:00 AM",
                    "next_step": "Send patient prep packet.",
                    "score": 95
                },
                "errorMessage": ""
            }
        }


class ChatHistory(BaseModel):
    """
    Represents stored chat, SMS, and email history.
    """
    chat_history_json_path: str = Field(default="", description="Path to JSON file containing chat history.")
    chat_summary: str = Field(default="", description="Summary of the chat history.")
    chat_history: List[Dict] = Field(default_factory=list, description="List of chat message records.")
    sms_history: List[Dict] = Field(default_factory=list, description="List of SMS message records.")
    email_history: List[Dict] = Field(default_factory=list, description="List of email message records.")

    class Config:
        schema_extra = {
            "example": {
                "chat_history_json_path": "/data/nuvia/chat_cust-78451.json",
                "chat_summary": "Patient was interested in same-day implants. Booked a consultation.",
                "chat_history": [
                    {"sender": "user", "message": "Hi, how long does the implant process take?"},
                    {"sender": "agent", "message": "At Nuvia, you can get permanent teeth in just 24 hours."}
                ],
                "sms_history": [
                    {"sender": "agent", "message": "Your consultation for Aug 20 at 10:00 AM is confirmed."}
                ],
                "email_history": [
                    {"subject": "Nuvia Consultation Confirmation", "body": "We look forward to seeing you on Aug 20 at 10:00 AM at our Salt Lake City center."}
                ]
            }
        }
