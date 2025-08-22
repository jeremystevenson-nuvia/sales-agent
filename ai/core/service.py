from typing import List, Optional, Union
from langchain_core.messages import BaseMessage, SystemMessage
from ai.core.model import AISettings
from ai.agents.service import AgentManager
from ai.openai.service import OpenAI
from core.models.base import AIInput, AIOutput

class AIClient:
    def __init__(self, session: AIInput) -> None:
        self.session = session
        self.response_id:str = session.response_id if session.response_id else None
        self.chat_history:List[BaseMessage] = None
        self._initialize_ai_client()


    def _initialize_ai_client(self):
        self.ai_agent = AgentManager(self.session.agent_id)
        self._init_response_id()
        # self._check_current_agent()
       
        
    def _init_response_id(self) -> None:    
        if not self.response_id:
            messages = [
                SystemMessage(content=self._general_decorators()),   
                SystemMessage(content=self._agent_decorators())
            ]
            last_conversation = self._load_last_conversation()
            if last_conversation:
                messages.append(SystemMessage(content=last_conversation))
            response = self.call(messages=messages)
            if response:
                self.response_id = response.response_id
                self.ai_agent.update_agent_profile(self.session.contact_id)
                #TODO we must like write response id on db -> conversation/contact_id/responseId
          
 
    def _check_current_agent(self) -> bool:
        if not self.session.agent_id or not self.response_id or not self.session.contact_id:
            return False
        

        is_agent_loaded = self.ai_agent.is_agent_profile_exists(self.session.contact_id)
        if not is_agent_loaded:
            agent_decorators = self._agent_decorators()
            if agent_decorators:
                messages = [
                    SystemMessage(content=agent_decorators)
                ]
                response = self.call(messages=messages)
                if not response.error_message or response.error_message == '':
                    if self.ai_agent.update_agent_profile(self.session.contact_id):
                        return True
        return True
        
                
    def _general_decorators(self) -> str:
        try:
            global_rules:str = None #TODO read from db 
            
            # Add dental implant type to this prompt
            prompt = f"""
            You are a assistant at Nuvia Dental Implant Center.
            Your behavior and response should adapt accordingly based on this context.

            ### Universal Rules, which take highest priority and must always be followed:
            {global_rules}
            """

            return prompt
        except Exception as e:
            print(f'Error in _general_decorators: {e}')
            return ''

    
    def _agent_decorators(self) -> str:
        try:
            prompt = f"""
            You are a conversational AI agent.

            - Agent Type: {self.ai_agent.agent.agent_type}
            - Agent Name: {self.ai_agent.agent.name}
            - Agent Behavior: {self.ai_agent.agent.behavior}


            ## Specific Rules for This Agent: 
            {self.ai_agent.agent.rules}

            ## Conversation Goals: 
            {self.ai_agent.agent.goals_str}

            Your objective is to gently guide the conversation toward achieving the above goals. Do not force the user to respond to goal-related topics—allow the conversation to flow naturally and respectfully.
            """
            return prompt
        except Exception as e:
            print(f'Error in _agent_decorators: {e}')
            return ''


    def _load_last_conversation(self) -> str:
        prompt = ''
        if self.session.data:
            prompt = "This is the last conversation with the user:\n"
            for item in self.session.data:
                prompt += f"{item.type}({item.direction}): {item.context}\n"
        if prompt:
            print('\n\nLast conversation is:\n\n', prompt)
        return prompt
    

    def call(self,      
             messages: List[BaseMessage],            
             ai_core_model: str = "openai",
             ai_settings: AISettings = None)-> AIOutput:
        try:
            #if ai core not open ai must first append chat history to messages and load decorator in the first of messages
            if ai_core_model == 'openai':
                open_ai = OpenAI(ai_settings)
                return open_ai.call(messages=messages, response_id=self.response_id)
            else:
                return AIOutput(errorMessage='AI Core model not supported')
        except Exception as e:
            print(f'Error in process_request: {e}')
            return AIOutput(errorMessage=f'Error in process_request: {e}')
        
        

            
        

        
    
        