# Enhanced Agentic Teacher Pipeline - Changes Summary

## Overview
The pipeline has been enhanced to save all intermediate states, audio files, and video files after each processing step.

## Key Changes

### 1. **test_run.py** - Main Execution Script
**Added Features:**
- **State Persistence**: After each agent step, the complete state is saved to a JSON file in `sessions/<topic>/steps/`
- **Session Management**: Properly initialized `SessionManager` to organize outputs
- **Directory Structure**: Auto-creates subdirectories for organized storage:
  - `steps/` - JSON files for each step
  - `audio/` - MP3 audio files
  - `videos/` - MP4 video files
  - `manim_code/` - Python code for each scene
- **Summary Report**: Displays all generated files at the end of execution

**JSON State Files:**
Each step saves a file named: `step_<number>_<agent_name>.json`
- Example: `step_01_teacher.json`, `step_02_storyboard.json`, etc.
- Each file contains:
  - All current state data
  - Metadata (step name, number, timestamp)
  - Pydantic models serialized to dictionaries

### 2. **agents/renderer.py** - Video Rendering Agent
**Improvements:**
- **Enhanced Error Handling**: Captures and displays stdout/stderr from Manim
- **Better File Detection**: If expected path fails, searches for any generated MP4 files
- **Robust Copying**: Properly copies video to session directory with error handling
- **Missing Tool Detection**: Helpful message if Manim is not installed
- **Encoding Fix**: Uses UTF-8 encoding for file writing

### 3. **agents/audio.py** - Audio Generation Agent
**Improvements:**
- **File Verification**: Checks if audio file was created and displays file size
- **Better Error Messages**: Full traceback on errors
- **Directory Creation**: Uses `parents=True` for robust directory creation
- **Session Check**: Warns if session manager is not available

## Output Structure

```
sessions/
└── neural_networks/
    ├── cache.json              # Session cache
    ├── steps/                  # State JSON files
    │   ├── step_01_teacher.json
    │   ├── step_02_storyboard.json
    │   ├── step_03_critic.json
    │   ├── step_04_audio.json
    │   ├── step_05_manim.json
    │   └── step_06_renderer.json
    ├── audio/                  # Audio files
    │   └── scene_1.mp3
    ├── videos/                 # Video files
    │   └── scene_1.mp4
    └── manim_code/            # Generated Manim code
        └── scene_1.py
```

## How to Run

```bash
cd d:\Projects\Velocity\agentic-teacher
python test_run.py
```

## Output Summary
At the end of execution, you'll see:
- Session directory path
- List of all generated files with counts
- Paths to audio files
- Paths to video files
- Path to Manim code files
- Final video path (if successful)

## Error Handling
All agents now include:
- Try-catch blocks for file operations
- Detailed error messages
- Full tracebacks for debugging
- Graceful degradation (continues even if some operations fail)

## Dependencies
Make sure these are installed:
```bash
pip install manim
pip install gTTS
pip install langgraph
pip install pydantic
```

## Step-by-Step Data Flow

1. **Teacher Agent** → Generates script → Saves to `step_01_teacher.json`
2. **Storyboard Agent** → Creates visual plan → Saves to `step_02_storyboard.json`
3. **Critic Agent** → Reviews content → Saves to `step_03_critic.json`
4. **Audio Agent** → Generates TTS → Saves to `step_04_audio.json` + `scene_1.mp3`
5. **Manim Agent** → Generates code → Saves to `step_05_manim.json` + `scene_1.py`
6. **Renderer Agent** → Renders video → Saves to `step_06_renderer.json` + `scene_1.mp4`

## Troubleshooting

### If video rendering fails:
1. Check if Manim is installed: `manim --version`
2. Look at the detailed error output in console
3. Check the generated Manim code in `manim_code/scene_1.py`
4. Try running manually: `manim -qh manim_scenes/scene_1.py GeneratedScene`

### If audio generation fails:
1. Check if gTTS is installed: `pip show gTTS`
2. Ensure internet connection (gTTS uses Google's TTS service)
3. Check the error traceback in console

### If state saving fails:
1. Check file permissions in the `sessions/` directory
2. Ensure disk space is available
3. Check the error traceback for specific issues
