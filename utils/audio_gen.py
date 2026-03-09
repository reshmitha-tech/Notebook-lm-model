"""
audio_gen.py - Generates audio narration from text using gTTS.
"""
import os
import uuid
from gtts import gTTS


AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "audio")


def generate_audio_summary(summary_text: str) -> str:
    """
    Convert a summary text to an MP3 audio file using gTTS.
    
    Args:
        summary_text: The text to convert to speech.
    
    Returns:
        Relative path to the generated audio file (e.g., 'audio/summary_xyz.mp3').
    """
    os.makedirs(AUDIO_DIR, exist_ok=True)
    
    filename = f"summary_{uuid.uuid4().hex[:8]}.mp3"
    output_path = os.path.join(AUDIO_DIR, filename)
    
    # Use gTTS to generate speech
    tts = gTTS(text=summary_text, lang="en", slow=False)
    tts.save(output_path)
    
    return f"audio/{filename}"
