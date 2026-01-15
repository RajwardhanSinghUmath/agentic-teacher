from langgraph.graph import StateGraph, END

from schemas.state import AgentState
from agents.planner import planner_agent
from agents.teacher import teacher_agent
from agents.storyboard import storyboard_agent
from agents.critic import critic_agent
from agents.audio import audio_agent
from agents.manim_codegen import manim_codegen_agent
from agents.concatenator import concatenator_agent
from agents.renderer import renderer_agent

graph = StateGraph(AgentState)

graph.add_node("planner", planner_agent)
graph.add_node("teacher", teacher_agent)
graph.add_node("storyboard", storyboard_agent)
graph.add_node("critic", critic_agent)
graph.add_node("audio", audio_agent)
graph.add_node("manim", manim_codegen_agent)
graph.add_node("renderer", renderer_agent)
graph.add_node("concatenator", concatenator_agent)

def step_cleaner_agent(state: AgentState) -> AgentState:
    """Resets the state for the next step."""
    print("--- CLEANER: Resetting state for next step ---")
    return {
        "current_script": None,
        "current_storyboard": None,
        "current_audio_metadata": None,
        "manim_code": None,
        "critique_feedback": None,
        "approved": False,
        "mp4_file_path": None,
        "audio_file_path": None,
        "critic_iterations": 0,
        "code_critique_feedback": None,
        "code_approved": False,
        "code_critic_iterations": 0
    }

graph.add_node("cleaner", step_cleaner_agent)

graph.set_entry_point("planner")

def check_curriculum_status(state: AgentState):
    curriculum = state.get("curriculum")
    index = state.get("current_step_index", 0)
    
    if curriculum and index >= len(curriculum.steps):
        print("--- GRAPH: All steps already completed. Skipping to concatenation. ---")
        return "concatenator"
    return "teacher"

graph.add_conditional_edges("planner", check_curriculum_status)
graph.add_edge("teacher", "storyboard")
graph.add_edge("storyboard", "critic")

def check_approval(state: AgentState):
    if state["approved"]:
        return "audio"
    return "storyboard"

graph.add_conditional_edges("critic", check_approval)

from agents.code_critic import code_critic_agent

graph.add_node("code_critic", code_critic_agent)

graph.add_edge("audio", "manim")
graph.add_edge("manim", "code_critic")

def check_code_approval(state: AgentState):
    if state.get("code_approved", False):
        return "renderer"
    return "manim"

graph.add_conditional_edges("code_critic", check_code_approval)

def check_next_step(state: AgentState):
    curriculum = state.get("curriculum")
    index = state.get("current_step_index", 0)
    
    if curriculum and index < len(curriculum.steps):
        print(f"--- GRAPH: Looping to step {index} ---")
        return "cleaner"
    
    print("--- GRAPH: All steps completed. Concatenating... ---")
    return "concatenator"

graph.add_conditional_edges("renderer", check_next_step)
graph.add_edge("cleaner", "teacher")
graph.add_edge("concatenator", END)

compiled_graph = graph.compile()

