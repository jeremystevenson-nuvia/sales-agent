from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.messages import SystemMessage, HumanMessage
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
        response_schemas = [
            ResponseSchema(name="message", description="Response human message based on the conversation flow and the provided data."),
            ResponseSchema(name="appointment", description=_set_appointment_prompt()),
            ResponseSchema(name="next_step", description="Based on the conversation, specify the assistant’s next action (e.g., follow up, send email, call). Max 40 characters."),
            ResponseSchema(name="summary", description="Summary of the conversation. Max up to 400 characters."),
        ]
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        return output_parser

def answer_question(input: AIInput) -> AIOutput:
    try:
        client = AIClient(input)
        output_parser = _create_format_instructions()
        prompt = f"""
                Extract the following structured data from the conversation below.
                Respond ONLY with valid JSON in the exact format specified. Do not include any explanations, markdown, or extra text.

                Format:
                {output_parser.get_format_instructions()}
            """
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=input.message)
        ]
        response = client.call(messages=messages)
        parsed = None
        try:
            parsed = output_parser.parse(response.response_text)
        except Exception as e:
            print("Raw LLM Output:", response.response_text)  # Log this
            parsed = None
        if parsed:
            response.response_message = parsed.get("message") or ""
            response.appointment = parsed.get("appointment") or 0
            response.next_step = parsed.get("next_step") or ""
            response.summary = parsed.get("summary") or ""
        return response
    except Exception as e:
        error_message = f"Sorry, I'm not sure what you mean. Please try again. Error: {e}"
        return AIOutput(response_message=error_message)
