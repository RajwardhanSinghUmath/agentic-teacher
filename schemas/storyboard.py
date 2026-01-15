from pydantic import BaseModel
from typing import List, Optional

class VisualObject(BaseModel):
    id: str
    type: str  # dot | line | arrow | text | axes | surface | group
    label: Optional[str] = None
    position: Optional[str] = None  # left | right | center | top | bottom

class AnimationStep(BaseModel):
    action: str  # fade_in | move | transform | highlight | fade_out
    target: str
    description: str

class Storyboard(BaseModel):
    scene_id: int
    title: str
    objects: List[VisualObject]
    animations: List[AnimationStep]
    duration: int  # seconds
