from pydantic import BaseModel
from typing import List

class AudioSegment(BaseModel):
    text: str
    start_time: float
    duration: float

class AudioMetadata(BaseModel):
    scene_id: int
    voice_style: str  # calm | explanatory | enthusiastic
    segments: List[AudioSegment]
    total_duration: float
