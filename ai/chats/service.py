# from langchain.output_parsers import StructuredOutputParser, ResponseSchema
# from langchain_core.messages import SystemMessage, HumanMessage
from core.models.base import AIInput, AIOutput
from ai.core.service import AIClient
from core.helpers.time_helper import get_current_timestamp

def _set_appointment_prompt():
    return f"""
        You are an AI assistant. Extract the appointment timestamp from the conversation.
        Current timestamp: {get_current_timestamp()}.
        If an appointment is found, return it as a 13-digit integer (milliseconds since epoch).
        If no appointment is found, return None.
        Do not return any other timestamps or values under any circumstances.
    """

def _create_format_instructions():
    # Simplified without langchain dependency
    return "JSON format instructions"

def answer_question(input: AIInput) -> AIOutput:
    try:
        client = AIClient(input)
        # Simplified response for now
        return AIOutput(
            response_message="Hello! I'm following up regarding your previous request. How can I assist you further today?",
            appointment=0,
            next_step="Follow up",
            summary="Conversation summary"
        )
    except Exception as e:
        error_message = f"Sorry, I'm not sure what you mean. Please try again. Error: {e}"
        return AIOutput(response_message=error_message)
