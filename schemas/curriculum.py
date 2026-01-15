from pydantic import BaseModel
from typing import List

class Step(BaseModel):
    id: int
    title: str
    goal: str
    difficulty: str  # intuitive | visual | mathematical | applied

class Curriculum(BaseModel):
    topic: str
    steps: List[Step]
