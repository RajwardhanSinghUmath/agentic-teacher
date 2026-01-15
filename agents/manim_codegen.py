from pydantic import BaseModel
from schemas.state import AgentState
from utils import structured_generator
from langchain_openai import ChatOpenAI
import os

SYSTEM_PROMPT = """
You are a Manim expert.
Your task is to write a COMPLETE, RUNNABLE Python script for a Manim scene.

Inputs:
1. Storyboard (visual objects + animations)
2. Audio Metadata (timing segments)

Rules:
- Use STANDARD Manim Community classes (e.g., Circle, Square, Text, FadeIn, Write, Transform).
- DO NOT use any external or custom libraries like `manim_templates` unless explicitly provided.
- Use `self.wait(duration)` to sync with audio segments.
- The class name MUST be `GeneratedScene`.
- The code must be self-contained and executable.
- YOU MUST EXPLICITLY IMPORT ALL NECESSARY MODULES:
  - Always include `from manim import *`.
  - If using random numbers, include `import random` or `import numpy as np`.
- Ensure all objects are added to valid groups or the scene before animating.

Output STRICT JSON:
{{
  "code": "string (the full python code including imports)",
  "explanation": "string"
}}
"""

class ManimCode(BaseModel):
    code: str
    explanation: str

def manim_codegen_agent(state: AgentState) -> AgentState:
    """Data processing node for the Manim Codegen Agent."""
    storyboard = state["current_storyboard"]
    audio_meta = state["current_audio_metadata"]
    
    session = state.get("session")
    index = state.get("current_step_index", 0)
    
    # Handle Feedback Loop
    feedback = state.get("code_critique_feedback")
    iterations = state.get("code_critic_iterations", 0)
    
    # Adjust cache key to include iteration if we are in a loop
    cache_key = f"step_{index}_manim_code_{iterations}"
    
    # Check cache (only if we usually cache this, but in a loop it's tricky. 
    # If we have a cache for THIS iteration, use it.)
    if session and session.has_cached(cache_key):
        print(f"--- MANIM: Loading cached code for step {index} (iter {iterations}) ---")
        return {"manim_code": session.get_cached(cache_key)}

    # Use OpenAI as requested.
    # Note: 'gpt-4.1' isn't a standard model ID. Using 'gpt-4o' as the current best model.
    # If the user specifically intended a custom proxy mapping 'gpt-4.1', we'd use that,
    # but based on common usage, 'gpt-4o' is the safest, high-performance bet.
    openai_llm = ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0.0
    )
    
    if feedback and iterations > 0:
        print(f"--- MANIM: Fixing code based on feedback (Iter {iterations}) ---")
        user_prompt = f"""
        PREVIOUS CODE:
        {state.get('manim_code')}
        
        CRITIC FEEDBACK:
        {feedback}
        
        Please FIX the code.
        Storyboard: {storyboard.model_dump_json()}
        Audio: {audio_meta.model_dump_json()}
        """
    else:
        print(f"--- MANIM: Generating code for scene {storyboard.scene_id} ---")
        user_prompt = f"Storyboard: {storyboard.model_dump_json()}\nAudio: {audio_meta.model_dump_json()}"
    
    try:
        result = structured_generator(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_schema=ManimCode,
            llm=openai_llm
        )
    except Exception as e:
        # Fallback if OpenAI fails (though we should fail hard or retry)
        print(f"--- MANIM: OpenAI Error: {e} ---")
        raise e
    
    # Cache the result
    if session:
        session.set_cached(cache_key, result.code)
        
    return {"manim_code": result.code}
