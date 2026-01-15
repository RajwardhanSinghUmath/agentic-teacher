import subprocess
import os
from schemas.state import AgentState

def renderer_agent(state: AgentState) -> AgentState:
    """Executes the Manim code to generate the video."""
    code = state["manim_code"]
    storyboard = state["current_storyboard"]
    scene_name = "GeneratedScene"
    session = state.get("session")
    
    session = state.get("session")
    index = state.get("current_step_index", 0)
    cache_key = f"step_{index}_mp4_file_path"
    
    # Check cache
    if session and session.has_cached(cache_key):
        cached_path = session.get_cached(cache_key)
        if cached_path and os.path.exists(cached_path):
            print(f"--- RENDERER: Loading cached video for step {index} ---")
            return {"mp4_file_path": cached_path}

    file_path = f"manim_scenes/scene_{storyboard.scene_id}.py"
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Write code to file
    try:
        with open(file_path, "w", encoding='utf-8') as f:
            f.write(code)
        print(f"--- RENDERER: written code to {file_path} ---")
    except Exception as e:
        print(f"--- RENDERER: Error writing code file: {e} ---")
        return {"mp4_file_path": None}
    
    # Execute Manim
    # -qh: Quality High (1080p60)
    print(f"--- RENDERER: Starting Manim rendering... ---")
    try:
        # Extend PYTHONPATH to include the project root so manim can find local modules
        env = os.environ.copy()
        cwd = os.getcwd()
        env["PYTHONPATH"] = cwd + os.pathsep + env.get("PYTHONPATH", "")
        
        # Check for ffmpeg
        import shutil
        if not shutil.which("ffmpeg"):
            print("--- RENDERER: CRITICAL ERROR - ffmpeg not found in PATH ---")
            print("--- RENDERER: Manim requires ffmpeg to generate videos. ---")
            print("--- RENDERER: Please install ffmpeg (e.g., 'winget install ffmpeg') and restart. ---")
            return {"mp4_file_path": None}
            
        # Stream output to see progress
        # Using -ql (Low Quality, 480p15) for faster iteration
        process = subprocess.Popen(
            ["manim", "-ql", "--disable_caching", file_path, scene_name],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Reader thread for stdout
        def reader(pipe, label):
            try:
                with pipe:
                    for line in iter(pipe.readline, ''):
                        print(f"[{label}] {line.strip()}")
            except Exception:
                pass

        import threading
        t_out = threading.Thread(target=reader, args=(process.stdout, "MANIM_OUT"))
        t_err = threading.Thread(target=reader, args=(process.stderr, "MANIM_ERR"))
        
        t_out.start()
        t_err.start()
        
        process.wait()
        t_out.join()
        t_err.join()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, process.args)

        print(f"--- RENDERER: Manim execution completed successfully ---")
        
    except subprocess.CalledProcessError as e:
        print(f"--- RENDERER: Error during rendering ---")
        print(f"Return code: {e.returncode}")
        # Logs have already been streamed to console
        print("--- RENDERER: Check MANIM_ERR logs above for details ---")
        return {"mp4_file_path": None}
    except FileNotFoundError:
        print(f"--- RENDERER: Manim command not found. Please install Manim: pip install manim ---")
        return {"mp4_file_path": None}
    except Exception as e:
        print(f"--- RENDERER: Unexpected error during rendering: {e} ---")
        return {"mp4_file_path": None}
        
    # Expected output path for -ql (480p15)
    # Manim structure: media/videos/<module_name>/480p15/<scene_name>.mp4
    # module_name is the filename without extension: scene_{storyboard.scene_id}
    output_path = f"media/videos/scene_{storyboard.scene_id}/480p15/{scene_name}.mp4"
    
    if os.path.exists(output_path):
        print(f"--- RENDERER: Video successfully rendered to {output_path} ---")
        
        # Combine with audio if available
        audio_path = state.get("audio_file_path")
        if audio_path and os.path.exists(audio_path):
            print(f"--- RENDERER: Found audio at {audio_path}. Merging... ---")
            merged_output_path = output_path.replace(".mp4", "_merged.mp4")
            
            try:
                # ffmpeg command to combine video and audio
                # -y: overwrite output
                # -c:v copy: copy video stream without re-encoding
                # -c:a aac: encode audio to aac
                # -shortest: finish when the shortest stream ends
                cmd = [
                    "ffmpeg", "-y",
                    "-i", output_path,
                    "-i", audio_path,
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-shortest",
                    merged_output_path
                ]
                
                subprocess.run(cmd, check=True, capture_output=True)
                
                print(f"--- RENDERER: Merged video created at {merged_output_path} ---")
                output_path = merged_output_path
                
            except subprocess.CalledProcessError as e:
                print(f"--- RENDERER: ffmpeg merge failed: {e} ---")
                if e.stderr:
                    print(f"STDERR: {e.stderr}")
            except Exception as e:
                print(f"--- RENDERER: Error merging audio: {e} ---")

        
        # Copy to session folder for organization
        if session:
            import shutil
            video_dir = session.get_path("videos")
            video_dir.mkdir(parents=True, exist_ok=True)
            session_video_path = video_dir / f"scene_{storyboard.scene_id}.mp4"
            
            try:
                shutil.copy2(output_path, session_video_path)
                print(f"--- RENDERER: Copied to session: {session_video_path} ---")
                output_path = str(session_video_path)  # Use session path for final output
            except Exception as e:
                print(f"--- RENDERER: Error copying video to session: {e} ---")
        else:
            print(f"--- RENDERER: No session manager, using default path ---")
    else:
        print(f"--- RENDERER: Video file not found at {output_path} ---")
        print(f"--- RENDERER: Checking media directory for any generated files... ---")
        # Try to find any mp4 files in media directory
        import glob
        media_files = glob.glob("media/**/*.mp4", recursive=True)
        if media_files:
            print(f"--- RENDERER: Found these video files: ---")
            for mf in media_files:
                print(f"  - {mf}")
            # Use the most recent one
            output_path = max(media_files, key=os.path.getmtime)
            print(f"--- RENDERER: Using most recent: {output_path} ---")
        else:
            print(f"--- RENDERER: No video files found. Rendering likely failed. ---")
            output_path = None
    
    if output_path and os.path.exists(output_path):
        if session:
            # Cache the video path
            session.set_cached(cache_key, output_path)
            # Increment step index for next run
            session.set_cached("current_step_index", index + 1)
            # Return updated index to State
            return {"mp4_file_path": output_path, "current_step_index": index + 1}
    
    return {"mp4_file_path": output_path}

