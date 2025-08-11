from ai.agents.model import AIAgent, Goal


class AgentManager:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.agent_goals:str = None


    def _get_agent_goals_str(self, goals_list:list[Goal] = None) -> str:
        goals = ''
        if goals_list:
            sorted_goals = sorted(goals_list, key=lambda item: item.order)
            for item in sorted_goals:
                if item.title:
                    goals += f"{item.order}. [{item.title}]: {item.description}\n"
        return goals


    def load_agent(self) -> AIAgent:
        try:
            if not self.agent_id:
                return None
            agent_object = None # read from db
            if not agent_object:
                return None
            agent = AIAgent(agent_object)
            agent.goals_str = self._get_agent_goals_str(agent.goals)
            
            if agent:
                return agent
            else:
                return None
        except Exception as e:
            print(f'Error in agent_id:{self.agent_id} error is: {e}')
            return None    
    
    
    def is_agent_profile_exists(self, response_id) -> bool:
        #Check if agent is loaded for a response_id
        ...
    
    def update_agent_profile(self, response_id) -> bool:
        #If we want change agent for a response_id
        ...