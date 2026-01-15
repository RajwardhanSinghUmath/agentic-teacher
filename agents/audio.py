from schemas.state import AgentState
from schemas.audio import AudioMetadata
from utils import structured_generator

SYSTEM_PROMPT = """
You are an audio director for educational content.

Your task is to take a full narration script and split it 
into timed segments that align with visual beats.

Rules:
- Break text at natural pauses (commas, periods).
- Assign a 'voice_style' (calm, explanatory).
- Estimate 'duration' for each segment (approx 150 words/min).
- 'start_time' should be cumulative.

Output STRICT JSON following this schema:
{{
  "scene_id": number,
  "voice_style": "calm | explanatory | enthusiastic",
  "segments": [
    {{
      "text": string,
      "start_time": number,
      "duration": number
    }}
  ],
  "total_duration": number
}}
"""



def audio_agent(state: AgentState) -> AgentState:
    """Data processing node for the Audio Agent."""
    script = state["current_script"]
    storyboard = state["current_storyboard"]
    session = state.get("session")
    index = state.get("current_step_index", 0)
    cache_key = f"step_{index}_audio_metadata"

    print(f"--- AUDIO: Generating audio metadata for '{script.title}' ---")
    
    # Check cache
    if session and session.has_cached(cache_key):
        print(f"--- AUDIO: Loading cached metadata for step {index} ---")
        cached = session.get_cached(cache_key)
        audio_meta = AudioMetadata(**cached)
    else:
        audio_meta = structured_generator(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"Generate audio timing for:\nNarration: {script.narration}\nVisuals: {storyboard.model_dump_json()}",
            output_schema=AudioMetadata
        )
        if session:
            session.set_cached(cache_key, audio_meta.model_dump())
            print(f"--- AUDIO: Metadata cached ---")
    
    # Generate actual audio file using TTS
    audio_file_path = None
    if session:
        try:
            from gtts import gTTS
            import os
            
            # Create audio file
            audio_dir = session.get_path("audio")
            audio_dir.mkdir(parents=True, exist_ok=True)
            audio_file_path = str(audio_dir / f"scene_{storyboard.scene_id}.mp3")
            
            # Generate TTS
            print(f"--- AUDIO: Generating speech file... ---")
            tts = gTTS(text=script.narration, lang='en', slow=False)
            tts.save(audio_file_path)
            print(f"--- AUDIO: Successfully saved to {audio_file_path} ---")
            
            # Verify file was created
            if os.path.exists(audio_file_path):
                file_size = os.path.getsize(audio_file_path)
                print(f"--- AUDIO: File size: {file_size} bytes ---")
            else:
                print(f"--- AUDIO: Warning - file not found after save ---")
            
        except ImportError:
            print("--- AUDIO: Warning - gTTS not installed, skipping audio file generation ---")
            print("--- AUDIO: Install with: pip install gTTS ---")
        except Exception as e:
            print(f"--- AUDIO: Error generating audio file: {e} ---")
            import traceback
            print(traceback.format_exc())
    else:
        print("--- AUDIO: Warning - No session manager, skipping audio file generation ---")
    
    return {
        "current_audio_metadata": audio_meta,
        "audio_file_path": audio_file_path
    }

