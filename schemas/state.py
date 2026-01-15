from typing import TypedDict, Optional, List, Dict, Any
from .curriculum import Curriculum
from .script import TeachingScript
from .storyboard import Storyboard
from .audio import AudioMetadata

class AgentState(TypedDict):
    topic: str
    curriculum: Optional[Curriculum]
    current_step_index: int
    current_script: Optional[TeachingScript]
    current_storyboard: Optional[Storyboard]
    current_audio_metadata: Optional[AudioMetadata]
    manim_code: Optional[str]
    critique_feedback: Optional[str]
    approved: bool
    mp4_file_path: Optional[str]
    audio_file_path: Optional[str]
    critic_iterations: int  # Track how many times we've critiqued
    
    # Code Critique Loop State
    code_critique_feedback: Optional[str]
    code_approved: bool
    code_critic_iterations: int
    
    session: Any  # SessionManager instance for caching
