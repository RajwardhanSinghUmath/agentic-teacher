print("Start debug")
try:
    print("Importing SessionManager...")
    from session_manager import SessionManager
    print("SessionManager imported.")
    
    print("Importing compiled_graph...")
    from graph import compiled_graph
    print("compiled_graph imported.")

    print("Creating session...")
    s = SessionManager("DebugTopic")
    print(f"Session created at {s.session_dir}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
