from schemas.state import AgentState
from schemas.storyboard import Storyboard
from utils import structured_generator

SYSTEM_PROMPT = """
You are a visual designer creating educational animations
in the style of 3Blue1Brown.

Your task is to convert a teaching explanation into a
visual storyboard.

Rules:
- Use detailed animations for best learning experience.
- Prefer spatial intuition over text.
- Introduce objects gradually.
- Each animation must have a clear purpose.
- Avoid clutter.

Output STRICT JSON following this schema:
{{
  "scene_id": number,
  "title": string,
  "objects": [
    {{
      "id": string,
      "type": "dot | line | arrow | text | axes | surface | group",
      "label": string | null,
      "position": "left | right | center | top | bottom | null"
    }}
  ],
  "animations": [
    {{
      "action": "fade_in | move | transform | highlight | fade_out",
      "target": string,
      "description": string
    }}
  ],
  "duration": number
}}
"""



def storyboard_agent(state: AgentState) -> AgentState:
    """Data processing node for the Storyboard Agent."""
    script = state["current_script"]
    if not script:
        return {}
        
    session = state.get("session")
    index = state["current_step_index"]
    cache_key = f"step_{index}_storyboard"
    
    # Check cache
    if session and session.has_cached(cache_key):
        print(f"--- STORYBOARD: Loading cached storyboard for step {index} ---")
        cached = session.get_cached(cache_key)
        storyboard = Storyboard(**cached)
        return {"current_storyboard": storyboard}

    print(f"--- STORYBOARD: visualizing '{script.title}' ---")
    
    storyboard = structured_generator(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=f"Create a storyboard for this explanation:\n{script.model_dump_json()}",
        output_schema=Storyboard
    )
    
    # Cache the result
    if session:
        session.set_cached(cache_key, storyboard.model_dump())
        print(f"--- STORYBOARD: Storyboard cached ---")
    
    return {"current_storyboard": storyboard}

