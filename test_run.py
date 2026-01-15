import sys
import json
from datetime import datetime
from pathlib import Path
from langgraph.graph import StateGraph, END
from schemas.state import AgentState
from schemas.curriculum import Curriculum, Step
from agents.teacher import teacher_agent
from agents.storyboard import storyboard_agent
from agents.critic import critic_agent
from agents.audio import audio_agent
from agents.manim_codegen import manim_codegen_agent
from agents.renderer import renderer_agent
from session_manager import SessionManager

# 1. Define Static Curriculum
static_curriculum = Curriculum(
    topic="Neural Networks",
    steps=[
        Step(
            id=1,
            title="The Perceptron",
            goal="Understand the basic unit of a neural network as a decision boundary.",
            difficulty="intuitive"
        )
    ]
)

# Helper function to save state after each step
def save_step_state(session: SessionManager, step_name: str, state: AgentState, step_number: int):
    """Save the current state to a JSON file after each step"""
    output_dir = session.get_path("steps")
    output_dir.mkdir(exist_ok=True)
    
    # Create a serializable version of the state
    serializable_state = {}
    for key, value in state.items():
        if key == "session":
            continue  # Skip the session object itself
        elif hasattr(value, 'model_dump'):
            # Pydantic models
            serializable_state[key] = value.model_dump()
        elif isinstance(value, (str, int, float, bool, type(None))):
            serializable_state[key] = value
        elif isinstance(value, dict):
            serializable_state[key] = value
        else:
            serializable_state[key] = str(value)
    
    # Add metadata
    serializable_state['_metadata'] = {
        'step_name': step_name,
        'step_number': step_number,
        'timestamp': datetime.now().isoformat()
    }
    
    # Save to file
    output_file = output_dir / f"step_{step_number:02d}_{step_name}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(serializable_state, f, indent=2, ensure_ascii=False)
    
    print(f"--- Saved state to: {output_file} ---")

# 2. Re-construct Graph specifically for running from Teacher onwards
def check_approval(state: AgentState):
    if state["approved"]:
        return "audio"
    return "storyboard"

graph = StateGraph(AgentState)

# Note: We SKIP the planner node
graph.add_node("teacher", teacher_agent)
graph.add_node("storyboard", storyboard_agent)
graph.add_node("critic", critic_agent)
graph.add_node("audio", audio_agent)
graph.add_node("manim", manim_codegen_agent)
graph.add_node("renderer", renderer_agent)

# Entry point is TEACHER directly
graph.set_entry_point("teacher")

graph.add_edge("teacher", "storyboard")
graph.add_edge("storyboard", "critic")
graph.add_conditional_edges("critic", check_approval)
graph.add_edge("audio", "manim")
graph.add_edge("manim", "renderer")
graph.add_edge("renderer", END)

test_graph = graph.compile()

# 3. Execution
import time

def main():
    print("--- RUNNING TEST MODE WITH STATIC CURRICULUM ---")
    
    # Initialize session manager
    session = SessionManager(topic="Neural Networks")
    print(f"--- Session directory: {session.session_dir} ---")
    
    # Create subdirectories for outputs
    session.get_path("steps").mkdir(exist_ok=True)
    session.get_path("audio").mkdir(exist_ok=True)
    session.get_path("videos").mkdir(exist_ok=True)
    session.get_path("manim_code").mkdir(exist_ok=True)
    
    initial_state = {
        "topic": "Neural Networks",
        "current_step_index": 0,
        "curriculum": static_curriculum, # Pre-filled
        "current_script": None,
        "current_storyboard": None,
        "current_audio_metadata": None,
        "manim_code": None,
        "critique_feedback": None,
        "approved": False,
        "critic_iterations": 0,
        "mp4_file_path": None,
        "session": session  # Add session to state
    }

    try:
        # Stream the graph execution to save state after each step
        final_state = None
        step_counter = 0
        
        for event in test_graph.stream(initial_state):
            for node_name, result in event.items():
                step_counter += 1
                print(f"--- Finished node: {node_name} ---")
                
                # Merge result into state for saving
                if final_state is None:
                    final_state = initial_state.copy()
                final_state.update(result)
                
                # Save state after each step
                save_step_state(session, node_name, final_state, step_counter)
                
                # Save manim code to separate file if generated
                if node_name == "manim" and final_state.get("manim_code"):
                    manim_dir = session.get_path("manim_code")
                    manim_file = manim_dir / f"scene_{final_state['current_storyboard'].scene_id}.py"
                    with open(manim_file, 'w', encoding='utf-8') as f:
                        f.write(final_state["manim_code"])
                    print(f"--- Saved Manim code to: {manim_file} ---")

        print("="*50)
        print("TEST RUN COMPLETE")
        print("="*50)
        
        if final_state:
            # Print summary
            print(f"\nSession Directory: {session.session_dir}")
            print(f"\nGenerated Files:")
            print(f"  - Steps data: {session.get_path('steps')}")
            
            audio_files = list(session.get_path("audio").glob("*.mp3"))
            if audio_files:
                print(f"  - Audio files: {len(audio_files)} file(s)")
                for audio_file in audio_files:
                    print(f"    • {audio_file}")
            
            video_files = list(session.get_path("videos").glob("*.mp4"))
            if video_files:
                print(f"  - Video files: {len(video_files)} file(s)")
                for video_file in video_files:
                    print(f"    • {video_file}")
            
            manim_files = list(session.get_path("manim_code").glob("*.py"))
            if manim_files:
                print(f"  - Manim code: {len(manim_files)} file(s)")
                for manim_file in manim_files:
                    print(f"    • {manim_file}")
            
            if final_state.get("mp4_file_path"):
                print(f"\nFinal Video: {final_state['mp4_file_path']}")
        else:
            print("Workflow finished without final state.")
            
    except Exception as e:
        import traceback
        print(f"Test run failed: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
