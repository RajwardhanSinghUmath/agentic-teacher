from pydantic import BaseModel
from typing import List

class TeachingScript(BaseModel):
    step_id: int
    title: str
    narration: str
    key_points: List[str]
    analogy: str
