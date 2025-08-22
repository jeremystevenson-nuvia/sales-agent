from ai.agents.model import AIAgent, Goal


class AgentManager:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.agent_goals:str = None
        self.agent = self._static_agent() #TODO load from db
        

    def _get_agent_goals_str(self, goals_list:list[Goal] = None) -> str:
        goals = ''
        if goals_list:
            sorted_goals = sorted(goals_list, key=lambda item: item.order)
            for item in sorted_goals:
                if item.title:
                    goals += f"{item.order}. [{item.title}]: {item.description}\n"
        return goals

    def _load_agent(self) -> AIAgent:
        try:
            if not self.agent_id:
                return None
            # Fetch agent from MongoDB (Beanie) and map to AIAgent
            import asyncio
            from core.models.mongo import Agent as AgentDoc

            async def _fetch():
                try:
                    return await AgentDoc.get(self.agent_id)
                except Exception:
                    return None

            doc = None
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # Avoid blocking current event loop; skip DB fetch in this context
                doc = None
            else:
                doc = asyncio.run(_fetch())

            if not doc:
                return None

            rules_text = ""
            try:
                rules_text = "\n".join([r.value for r in (doc.rules or []) if getattr(r, 'value', None)])
            except Exception:
                rules_text = ""

            agent = AIAgent(
                id=str(getattr(doc, 'id', '') or ''),
                name=getattr(doc, 'name', None),
                description=getattr(doc, 'description', None),
                rules=rules_text,
                agent_type=getattr(doc, 'type', None),
            )
            agent.goals_str = self._get_agent_goals_str(agent.goals)
            
            if agent:
                return agent
            else:
                return None
        except Exception as e:
            print(f'Error in agent_id:{self.agent_id} error is: {e}')
            return None    
    
    def is_agent_profile_exists(self, contact_id) -> bool:
        # Check flag at path conversation/contact_id/agents/agent_id/isLoaded
        try:
            if not contact_id or not self.agent_id:
                return False

            import asyncio
            from core.db.mongo import db

            async def _fetch_flag() -> bool:
                try:
                    projection_key = f"agents.{self.agent_id}.isLoaded"
                    doc = await db["conversations"].find_one(
                        {"contact_id": contact_id}, {projection_key: 1}
                    )
                    if not doc:
                        return False
                    agents = doc.get("agents") or {}
                    if not isinstance(agents, dict):
                        return False
                    agent_entry = agents.get(self.agent_id)
                    if not isinstance(agent_entry, dict):
                        return False
                    value = agent_entry.get("isLoaded")
                    return bool(value) if isinstance(value, bool) else False
                except Exception:
                    return False

            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # Avoid blocking the running event loop in sync context
                return False
            else:
                return bool(asyncio.run(_fetch_flag()))
        except Exception:
            return False
    
    def update_agent_profile(self, contact_id) -> bool:
        # Set flag at path conversation/contact_id/agents/agent_id/isLoaded = True
        try:
            if not contact_id or not self.agent_id:
                return False

            import asyncio
            from core.db.mongo import db

            async def _set_flag() -> bool:
                try:
                    field_path = f"agents.{self.agent_id}.isLoaded"
                    result = await db["conversations"].update_one(
                        {"contact_id": contact_id},
                        {"$set": {field_path: True, "contact_id": contact_id}},
                        upsert=True,
                    )
                    return bool(getattr(result, "modified_count", 0) or getattr(result, "upserted_id", None) or getattr(result, "matched_count", 0))
                except Exception:
                    return False

            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # Avoid blocking event loop in sync context
                return False
            else:
                return bool(asyncio.run(_set_flag()))
        except Exception:
            return False
        
    def _static_agent(self) -> AIAgent:
        return AIAgent(
            id='agent_1',
            name='Elena Marlowe',
            description='Assistant at Nuvia Dental Implant Center',
            rules='',
            agent_type='assistant',
            goals_str='',
            behavior='Calm and patient, always offering suggestions and guidance to the user.',
        )
    