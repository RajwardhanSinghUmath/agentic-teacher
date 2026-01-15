from schemas.state import AgentState
from schemas.script import TeachingScript
from utils import structured_generator

SYSTEM_PROMPT = """
You are an exceptional teacher inspired by 3Blue1Brown.

Your task is to explain ONE learning step in a way that is:
- Intuitive
- Visual
- Conceptual
- Calm and story-driven

Rules:
- Assume the learner has never seen this before.
- Avoid formulas unless absolutely necessary.
- Use spatial or physical analogies.
- Explain things as if you were drawing on a board.

Output STRICT JSON following this schema:
{{
  "step_id": number,
  "title": string,
  "narration": string,
  "key_points": [string],
  "analogy": string
}}
"""



def teacher_agent(state: AgentState) -> AgentState:
    """Data processing node for the Teacher Agent."""
    curriculum = state["curriculum"]
    index = state["current_step_index"]
    
    if not curriculum or index >= len(curriculum.steps):
        # Or handle completion
        return {}

    session = state.get("session")
    cache_key = f"step_{index}_script"

    # Check cache
    if session and session.has_cached(cache_key):
        print(f"--- TEACHER: Loading cached script for step {index} ---")
        cached = session.get_cached(cache_key)
        script = TeachingScript(**cached)
        return {"current_script": script}

    step = curriculum.steps[index]
    print(f"--- TEACHER: Explaining step {step.id} - {step.title} ---")
    
    script = structured_generator(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=f"Explain this step: {step.model_dump_json()}",
        output_schema=TeachingScript
    )
    
    # Cache the result
    if session:
        session.set_cached(cache_key, script.model_dump())
        print(f"--- TEACHER: Script cached ---")
    
    return {"current_script": script}

