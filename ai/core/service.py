from typing import List, Optional, Union
# from langchain_core.messages import BaseMessage, SystemMessage
from ai.core.model import AISettings
from ai.agents.service import AgentManager
from ai.openai.service import OpenAI
from core.models.base import AIInput, AIOutput

class AIClient:
    def __init__(self, session: AIInput) -> None:
        self.session = session
        self.response_id:str = None
        self.chat_history:List = None
        self._initialize_ai_client()
        

    def _initialize_ai_client(self):
        self.ai_agent = AgentManager(self.session.agent_id)
        self._init_response_id()
        self._check_current_agent()
       

    def _init_response_id(self) -> None:
        # Read response id from MongoDB: conversation/contact_id/responseId
        try:
            import asyncio
            from core.models.mongo import Conversation

            async def _fetch_response_id(contact_id: str):
                try:
                    # Get latest conversation for this contact, if multiple exist
                    doc = await Conversation.find(Conversation.contact_id == contact_id).sort(-Conversation.created_at).first_or_none()
                    if doc and getattr(doc, "response_id", None):
                        return str(doc.response_id)
                    return None
                except Exception:
                    return None

            contact_id = getattr(self.session, "contact_id", None)
            fetched_id = None
            if contact_id:
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None

                if loop and loop.is_running():
                    # Avoid blocking the running loop in sync context
                    fetched_id = None
                else:
                    fetched_id = asyncio.run(_fetch_response_id(contact_id))
            self.response_id = fetched_id
        except Exception:
            self.response_id = None
        
        if not self.response_id:
            # Simplified without langchain
            self.response_id = "mock_response_id"
            self.ai_agent.update_agent_profile(self.session.contact_id)
            # Write response id on db -> conversation/contact_id/responseId
            try:
                import asyncio
                from core.db.mongo import db
                async def _set_response_id(contact_id: str, response_id: str):
                    try:
                        await db["conversations"].update_one(
                            {"contact_id": contact_id},
                            {"$set": {"response_id": response_id, "contact_id": contact_id}},
                            upsert=True,
                        )
                        return True
                    except Exception:
                        return False
                loop = None
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None
                if loop and loop.is_running():
                    # Avoid blocking the running event loop in sync context
                    pass
                else:
                    asyncio.run(_set_response_id(self.session.contact_id, self.response_id))
            except Exception:
                pass
         

    def _check_current_agent(self) -> bool:
        if not self.session.agent_id or not self.response_id or not self.session.contact_id:
            return False
        

        is_agent_loaded = self.ai_agent.is_agent_profile_exists(self.session.contact_id)
        if not is_agent_loaded:
            # Simplified without langchain
            if self.ai_agent.update_agent_profile(self.session.contact_id):
                return True
        return True
        

                
    def _general_decorators(self) -> str:
        try:
            # global_rules:str = None #TODO read from db 
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

            - Agent Type: {getattr(self.ai_agent.agent, 'agent_type', 'unknown')}
            - Agent Name: {getattr(self.ai_agent.agent, 'name', 'unknown')}


            ## Specific Rules for This Agent: 
            {getattr(self.ai_agent.agent, 'rules', 'No specific rules')}

            ## Conversation Goals: 
            {getattr(self.ai_agent.agent, 'goals_str', 'No specific goals')}

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
             messages: List,            
             ai_core_model: str = "openai",
             ai_settings: AISettings = None)-> AIOutput:
        try:
            # Simplified response without complex AI processing
            return AIOutput(
                response_message="Hello! I'm following up regarding your previous request.",
                response_id="mock_response_id",
                total_token=0
            )
        except Exception as e:
            print(f'Error in process_request: {e}')
            return AIOutput(error_message=f'Error in process_request: {e}')
        
        

            
        

        
    
        