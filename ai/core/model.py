from dataclasses import dataclass
from typing import Optional


@dataclass
class AISettings:
	model_name: str = "gpt-4.1-mini"
	temperature: float = 0.5
	verbose: bool = False
	use_responses_api: bool = True


# @dataclass
# class AIOutput:
# 	text: str
# 	response_id: str
# 	total_tokens: int
# 	errorMessage: Optional[str] = None

# @dataclass
# class ChatbotSession:
#     contact_id: str
#     agent_id: str
