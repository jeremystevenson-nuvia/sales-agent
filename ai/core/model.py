from dataclasses import dataclass
from typing import Optional


@dataclass
class AISettings:
	model_name: str = "gpt-4.1-mini"
	temperature: float = 0.5
	verbose: bool = False
	use_responses_api: bool = True


