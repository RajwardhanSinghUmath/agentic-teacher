from schemas.state import AgentState
from schemas.curriculum import Curriculum
from utils import structured_generator

SYSTEM_PROMPT = """
You are an expert curriculum designer.

Your job is to break ANY topic into a step-by-step
learning path suitable for animated teaching.

Rules:
- Assume the learner is intelligent but unfamiliar.
- Start with intuition and motivation.
- Gradually increase abstraction.
- Ensure each step can be visualized.
- Do NOT include formulas early unless necessary.
- Limit to 5–7 steps.

Output STRICT JSON following this schema:
{{
  "topic": string,
  "steps": [
    {{
      "id": number,
      "title": string,
      "goal": string,
      "difficulty": "intuitive | visual | mathematical | applied"
    }}
  ]
}}
"""



def planner_agent(state: AgentState) -> AgentState:
    """Data processing node for the Planner Agent."""
    topic = state["topic"]
    session = state.get("session")
    
    # Check cache
    if session and session.has_cached("curriculum"):
        print(f"--- PLANNER: Loading cached curriculum for '{topic}' ---")
        cached = session.get_cached("curriculum")
        curriculum = Curriculum(**cached)
    else:
        print(f"--- PLANNER: Generating curriculum for '{topic}' ---")
        curriculum = structured_generator(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"Create a curriculum for the topic: {topic}",
            output_schema=Curriculum
        )
        
        # Cache the result
        if session:
            session.set_cached("curriculum", curriculum.model_dump())
            print(f"--- PLANNER: Curriculum cached ---")
    
    return {
        "curriculum": curriculum,
        "current_step_index": state.get("current_step_index", 0),
        "approved": False 
    }

