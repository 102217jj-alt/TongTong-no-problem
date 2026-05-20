import os
import sys
# Ensure project root is on path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tongtong.voice import generate_bot_audio
from tongtong.text_utils import bot_speak_re

text = "測試男聲"
clean = bot_speak_re(text)
print("cleaned:", clean)

audio_url = generate_bot_audio(clean, "male")
print("audio_url:", audio_url)

if audio_url:
    fs_path = audio_url.lstrip('/')
    print('fs_path:', fs_path)
    print('exists:', os.path.exists(fs_path))
    if os.path.exists(fs_path):
        print('file size:', os.path.getsize(fs_path))
else:
    print('No audio generated')
