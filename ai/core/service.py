from typing import List, Optional, Union
from langchain_core.messages import BaseMessage, SystemMessage
from ai.core.model import ChatbotSession, AISettings, AIOutput
from ai.agents.service import AgentManager
from ai.openai.service import OpenAI


class AIClient:
    def __init__(self, session: ChatbotSession) -> None:
        self.session = session
        self.response_id:str = None
        self.agent_id:str = None
        self.chat_history:List[BaseMessage] = None
        self._initialize_ai_client()


    def _initialize_ai_client(self):
        self._init_response_id()
        self._init_chat_history()
        self.ai_agent = AgentManager(self.session.agent_id).load_agent()
        self._check_current_agent()
        
            
    def _check_current_agent(self) -> bool:
        if not self.agent_id or not self.response_id or not self.session.customer_id:
            return False
        
        loaded_agent = AgentManager(self.agent_id)
        is_agent_loaded = loaded_agent.is_agent_profile_exists(self.response_id)
        if not is_agent_loaded:
            agent_decorators = self._agent_decorators()
            if agent_decorators:
                messages = [
                    SystemMessage(content=agent_decorators)
                ]
                response = self.call(messages=messages)
                if not response.errorMessage or response.errorMessage == '':
                    if loaded_agent.update_agent_profile(self.response_id):
                        return True
        return False
        

    def _init_chat_history(self) -> None:
        if not self.session.customer_id:
            return
        if self.session.customer_id and self.session.chat_id:
                # self.chat_history = read_chat_history(self.user_id, self.chat_id, 10)
                ...
                

    def _init_response_id(self) -> None:
        #Read response id from db
        self.response_id = None #read from db
        
        if not self.response_id:
            messages = [
                SystemMessage(content=self._general_decorators()),   
            ]
            response = self.call(messages=messages)
            if response:
                self.response_id = response.response_id
                # we must like write response id-> write_response_id(self.response_id, self.session.user_id, self.session.chat_id)

        
    def _general_decorators(self) -> str:
        try:
            global_rules:str = None # read from db
            
            # Add dental implant type to this prompt
            prompt = f"""
            You are sales agent representing Nuvia Dental Implant Center.
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

            - Agent Type: {self.ai_agent.agent_type}
            - Agent Name: {self.ai_agent.name}


            ## Specific Rules for This Agent: 
            {self.ai_agent.rules}

            ## Conversation Goals: 
            {self.ai_agent.goals_str}

            Your objective is to gently guide the conversation toward achieving the above goals. Do not force the user to respond to goal-related topics—allow the conversation to flow naturally and respectfully.
            """
            return prompt
        except Exception as e:
            print(f'Error in _agent_decorators: {e}')
            return ''

    
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
        
        
    def update_ai_memory(self, agent_id:str) -> bool:
        #todo update ai memory from last conversation or new data
        ...
            
        

        
    
        