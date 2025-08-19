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
        client.call()
        return AIOutput(
            response_id=client.response_id,
            response_message=client.response_message or "No response message available",
            appointment=0 or "No appointment available",
            next_step=client.next_step or "No next step available",
            summary=client.summary or "No summary available"
        )
    except Exception as e:
        error_message = f"Sorry, I'm not sure what you mean. Please try again. Error: {e}"
        return AIOutput(response_message=error_message)
