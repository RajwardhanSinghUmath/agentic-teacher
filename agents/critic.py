from pydantic import BaseModel
from schemas.state import AgentState
from utils import structured_generator

SYSTEM_PROMPT = """
You are a strict reviewer for educational animations.

Evaluate the given teaching script and storyboard.
Check for:
- Conceptual clarity
- Visual alignment with explanation
- Overcomplexity
- Missing intuition

Respond in STRICT JSON:
{{
  "approved": true | false,
  "feedback": string
}}
"""



class CriticResponse(BaseModel):
    approved: bool
    feedback: str

def critic_agent(state: AgentState) -> AgentState:
    """Data processing node for the Critic Agent."""
    script = state["current_script"]
    storyboard = state["current_storyboard"]
    iterations = state.get("critic_iterations", 0)
    session = state.get("session")
    index = state.get("current_step_index", 0)
    cache_key = f"step_{index}_critic"
    
    # Check cache for APPROVAL only (to avoid stuck rejection loops)
    if session and session.has_cached(cache_key):
        cached = session.get_cached(cache_key)
        if cached.get("approved"):
            print(f"--- CRITIC: Loading cached APPROVAL for step {index} ---")
            return {
                "approved": True,
                "critique_feedback": cached.get("critique_feedback"),
                "critic_iterations": 0
            }
    
    MAX_ITERATIONS = 2  # Prevent infinite loops with local LLMs
    
    print(f"--- CRITIC: Reviewing scene {storyboard.scene_id} (iteration {iterations + 1}/{MAX_ITERATIONS}) ---")
    
    # Force approve after max iterations
    if iterations >= MAX_ITERATIONS:
        print(f"--- CRITIC: FORCE APPROVED after {MAX_ITERATIONS} iterations ---")
        result = {
            "approved": True,
            "critique_feedback": f"Approved after {MAX_ITERATIONS} review iterations",
            "critic_iterations": 0
        }
        if session:
            session.set_cached(cache_key, result)
        return result
    
    response = structured_generator(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=f"Review this Pair:\nSCRIPT: {script.model_dump_json()}\nSTORYBOARD: {storyboard.model_dump_json()}",
        output_schema=CriticResponse
    )
    
    # Process result
    if response.approved:
        print("--- CRITIC: APPROVED ---")
        result = {
            "approved": True,
            "critique_feedback": response.feedback,
            "critic_iterations": 0
        }
    else:
        print(f"--- CRITIC: REJECTED: {response.feedback} ---")
        result = {
            "approved": False,
            "critique_feedback": response.feedback,
            "critic_iterations": iterations + 1
        }
        
    # Cache the result
    if session:
        session.set_cached(cache_key, result)

    return result

