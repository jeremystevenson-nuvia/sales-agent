import os
from ai.core.model import AISettings
from core.models.base import AIOutput
from langchain_openai import ChatOpenAI
from typing import List, Optional, Union
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage

class OpenAI:
    def __init__(self, ai_settings: AISettings = None):
        self.llm = None
        self.ai_settings = ai_settings
        self.initialize()


    def initialize(self):
        # Ensure API key is picked up from env
        api_key = os.getenv("OPENAI_API_KEY")
        if self.ai_settings:
            self.llm = ChatOpenAI(
                model=self.ai_settings.model_name,
                temperature=self.ai_settings.temperature,
                verbose=self.ai_settings.verbose,
                use_responses_api=self.ai_settings.use_responses_api,
                api_key=api_key
            )
        else:
            self.llm = ChatOpenAI(
                model="gpt-4.1-mini", #TODO put fine tuned model id here
                temperature=0.5,
                verbose=True,
                use_responses_api=True,
                api_key=api_key
            )       
    
    def call(self,
             messages: List[BaseMessage],
             response_id: Optional[str] = None
        ) -> AIOutput:
        try:
            if messages:
                response = self.llm.invoke(messages, previous_response_id=response_id)
                if response:
                    response_id = response.response_metadata.get("id")
                    response_text = response.text()
                    total_tokens = int(response.usage_metadata.get('total_tokens', 0))
                    return AIOutput(
                        response_text = response_text, 
                        response_id = response_id,
                        total_token = total_tokens)
            return AIOutput(error_message='No messages provided')
        except Exception as e:
            return AIOutput(error_message=str(e))

    
        
