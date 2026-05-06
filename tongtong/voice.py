import os
import asyncio
import uuid
from gtts import gTTS
import edge_tts

# Constants for voices
VOICES = {
    "female": "zh-TW-HsiaoChenNeural",
    "male": "zh-TW-YunJheNeural"
}

# Directory to save audio files for web serving
AUDIO_DIR = os.path.join("static", "audio")
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

async def _edge_speak(text, voice_name, filename):
    """
    Internal helper to generate speech using edge-tts.
    """
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(filename)

def generate_bot_audio(text, voice_type="female"):
    """
    Converts text to speech and saves it as an MP3 file.
    Returns the relative path to the generated file.
    """
    if not text.strip():
        return None

    # Generate a unique filename to avoid collisions and caching issues
    file_id = str(uuid.uuid4())
    filename = f"voice_{file_id}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)
    
    voice_name = VOICES.get(voice_type, VOICES["female"])

    success = False
    try:
        # Try edge-tts first
        asyncio.run(_edge_speak(text, voice_name, filepath))
        success = True
    except Exception as e:
        print(f"edge-tts error: {e}, falling back to gTTS")
        try:
            # Fallback to gTTS
            tts = gTTS(text=text, lang='zh-TW')
            tts.save(filepath)
            success = True
        except Exception as ge:
            print(f"gTTS error: {ge}")

    if success and os.path.isfile(filepath):
        # Return the relative path for web access
        return f"/static/audio/{filename}"
    return None
