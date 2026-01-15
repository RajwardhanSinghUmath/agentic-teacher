import sys
from session_manager import SessionManager

try:
    from graph import compiled_graph
except Exception as e:
    print("\n" + "!"*50)
    print("CRITICAL IMPORT/CONFIGURATION ERROR")
    print("!"*50)
    print(f"Error: {e}")
    print(f"Type: {type(e).__name__}")
    print("\nThis is likely due to incompatible library versions (LangChain vs Pydantic).")
    print("Please run the following command in your terminal to fix this:")
    print("\n    pip install -r requirements.txt --upgrade\n")
    print("!"*50 + "\n")
    sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <topic>")
        sys.exit(1)
        
    topic = sys.argv[1]
    
    # Initialize session manager
    session = SessionManager(topic)
    print(f"Starting Agentic Teacher for topic: {topic}")
    print(f"Session directory: {session.session_dir}")
    print("="*50)
    
    # Load cached state if available
    current_step_index = session.get_cached("current_step_index") or 0
    
    # Load curriculum if cached
    from schemas.curriculum import Curriculum
    curriculum_data = session.get_cached("curriculum")
    curriculum = Curriculum(**curriculum_data) if curriculum_data else None

    # Helper to load step-specific artifacts
    def get_step_cached(key, model_class=None):
        full_key = f"step_{current_step_index}_{key}"
        data = session.get_cached(full_key)
        if data and model_class:
            return model_class(**data)
        return data

    # Import schemas for reconstruction
    from schemas.script import TeachingScript
    from schemas.storyboard import Storyboard
    from schemas.audio import AudioMetadata

    initial_state = {
        "topic": topic,
        "current_step_index": current_step_index,
        "curriculum": curriculum,
        "current_script": get_step_cached("script", TeachingScript),
        "current_storyboard": get_step_cached("storyboard", Storyboard),
        "current_audio_metadata": get_step_cached("audio_metadata", AudioMetadata),
        "manim_code": get_step_cached("manim_code"), # str
        "critique_feedback": get_step_cached("critique_feedback"), # str
        "approved": get_step_cached("approved") or False,
        "critic_iterations": get_step_cached("critic_iterations") or 0,
        "mp4_file_path": get_step_cached("mp4_file_path"),
        "session": session  # Add session to state
    }
    
    # Run the graph
    # Note: Using invoke for synchronous execution
    result = compiled_graph.invoke(initial_state)
    
    print("="*50)
    print("FINAL OUTPUT:")
    if result.get("mp4_file_path"):
        print(f"Video created at: {result['mp4_file_path']}")
    else:
        print("Workflow finished without video generation.")

if __name__ == "__main__":
    main()

