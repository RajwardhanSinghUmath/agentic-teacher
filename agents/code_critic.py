from pydantic import BaseModel
from schemas.state import AgentState
from utils import structured_generator, get_gemini_llm

SYSTEM_PROMPT = """
You are a strict Python Code Reviewer for Manim animations.

Your task is to review the given Python code for a Manim scene.
1.  **Syntax & Runtime Errors**: Ensure valid Python syntax. Check for common Manim pitfalls.
2.  **Manim Logic**: Ensure correct usage of Manim Community classes/methods (e.g., `self.play`, `Scene`, `FadeIn`).
3.  **Imports**: MUST have `from manim import *`.
4.  **Matching Storyboard**: Does the code implement the described visuals?

Usage Rules:
- If the code is correct and runnable, APPROVE it.
- If there are errors, REJECT it and provide feedback.
- Be specifically helpful: if you reject, explain exactly what line or logic is wrong.

Respond in STRICT JSON:
{{
  "approved": true | false,
  "feedback": "string"
}}
"""

class CodeCriticResponse(BaseModel):
    approved: bool
    feedback: str

def code_critic_agent(state: AgentState) -> AgentState:
    """Nodes for the Code Critic Agent.
    
    This agent uses Gemini to review the generated Manim code.
    It runs for a maximum of 2 iterations to catch errors.
    """
    code = state.get("manim_code", "")
    storyboard = state.get("current_storyboard")
    iterations = state.get("code_critic_iterations", 0)
    session = state.get("session")
    index = state.get("current_step_index", 0)
    
    # We include iterations in the cache key so we don't return the same critique for a fixed code
    # But wait, if code changes, the state changes.
    # However, for safety, let's include 'code_critic' and iteration in key
    cache_key = f"step_{index}_code_critic_{iterations}" 
    
    # Check cache
    if session and session.has_cached(cache_key):
        print(f"--- CODE CRITIC: Loading cached result for iteration {iterations} ---")
        result = session.get_cached(cache_key)
        # Verify schema match
        if "code_approved" in result:
            return result

    MAX_ITERATIONS = 2
    
    print(f"--- CODE CRITIC: Reviewing code (turn {iterations + 1}/{MAX_ITERATIONS}) ---")
    
    # Check strict cycle limit
    if iterations >= MAX_ITERATIONS:
        print(f"--- CODE CRITIC: Limit reached ({MAX_ITERATIONS}). Force approving to proceed. ---")
        result = {
            "code_approved": True,
            "code_critique_feedback": "Force approved after max iterations.",
            # We don't increment iterations further to avoid confusion, 
            # though the loop should have stopped anyway.
        }
        if session: session.set_cached(cache_key, result)
        return result

    gemini_llm = get_gemini_llm()
    
    response = structured_generator(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=f"Review this Manim Code:\nCODE:\n```python\n{code}\n```\n\nStoryboard: {storyboard.model_dump_json() if storyboard else 'N/A'}",
        output_schema=CodeCriticResponse,
        llm=gemini_llm
    )
    
    if response.approved:
        print("--- CODE CRITIC: APPROVED ---")
        result = {
            "code_approved": True,
            "code_critique_feedback": response.feedback,
            "code_critic_iterations": iterations # Final state of iterations
        }
    else:
        print(f"--- CODE CRITIC: REJECTED: {response.feedback} ---")
        result = {
            "code_approved": False,
            "code_critique_feedback": response.feedback,
            "code_critic_iterations": iterations + 1 # Increment for state tracking
        }
    
    if session:
        session.set_cached(cache_key, result)
        
    return result
