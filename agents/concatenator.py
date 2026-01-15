import os
import subprocess
from schemas.state import AgentState

def concatenator_agent(state: AgentState) -> AgentState:
    """Concatenates all generated video segments into a final video."""
    session = state.get("session")
    curriculum = state.get("curriculum")
    
    if not session or not curriculum:
        print("--- CONCATENATOR: Missing session or curriculum, cannot concat ---")
        return {}

    video_dir = session.get_path("videos")
    output_filename = "final_complete_video.mp4"
    final_output_path = video_dir / output_filename
    
    print(f"--- CONCATENATOR: Stitching videos for '{state['topic']}' ---")

    # Collect all video files in order
    input_files = []
    
    # We deliberately check steps in order from the curriculum
    for step in curriculum.steps:
        # Assuming scene_id matches step.id
        # Note: scene_id in storyboard usually comes from step.id
        # We need to handle the file naming convention used in renderer.py:
        # scene_{storyboard.scene_id}.mp4
        
        # We can try to find the file
        possible_name = f"scene_{step.id}.mp4"
        file_path = video_dir / possible_name
        
        if file_path.exists():
            input_files.append(file_path)
        else:
            print(f"--- CONCATENATOR: Warning - Missing video for step {step.id} at {file_path} ---")

    if not input_files:
        print("--- CONCATENATOR: No videos found to concatenate. ---")
        return {}

    # Create a file list for ffmpeg
    list_file_path = video_dir / "files_to_concat.txt"
    with open(list_file_path, "w") as f:
        for vid in input_files:
            # escaped_path = str(vid).replace("\\", "/") # ffmpeg likes forward slashes or escaped backslashes
            # Actually for file list, it's safer to use relative paths or just standard formatting
            f.write(f"file '{vid.name}'\n")
    
    print(f"--- CONCATENATOR: Found {len(input_files)} videos. ---")

    try:
        # ffmpeg command to concat
        # -f concat: usage of concat demuxer
        # -safe 0: allow unsafe file paths (sometimes needed)
        # -i lists_file: input file list
        # -c copy: copy streams without re-encoding
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file_path),
            "-c", "copy",
            str(final_output_path)
        ]
        
        # Run in the video directory so relative paths in text file work
        subprocess.run(cmd, check=True, cwd=str(video_dir), capture_output=True)
        
        print(f"--- CONCATENATOR: Success! Final video: {final_output_path} ---")
        return {"mp4_file_path": str(final_output_path)}
        
    except subprocess.CalledProcessError as e:
        print(f"--- CONCATENATOR: Error concatenating videos: {e} ---")
        return {}
    except Exception as e:
        print(f"--- CONCATENATOR: Unexpected error: {e} ---")
        return {}
