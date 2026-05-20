import os
import asyncio
import uuid
import sys
import edge_tts
import pyttsx3

# Constants for Edge-TTS
VOICES = {
    "female": "zh-TW-HsiaoChenNeural",   # 曉臻
    "male": "zh-TW-YunJheNeural",       # 雲哲
    "loli": "zh-CN-XiaoyiNeural",       # 曉伊
    "sister": "zh-CN-XiaoxiaoNeural",   # 曉曉
    "sunny": "zh-CN-YunxiNeural"        # 雲希
}

# 備用聲音：如果台灣語音被 403，嘗試大陸語音（微軟大陸伺服器通常更穩定）
BACKUP_VOICES = {
    "female": "zh-CN-XiaoxiaoNeural",
    "male": "zh-CN-YunxiNeural",
    "loli": "zh-CN-XiaoyiNeural",
    "sister": "zh-CN-XiaoxiaoNeural",
    "sunny": "zh-CN-YunxiNeural"
}

if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except: pass

AUDIO_DIR = os.path.join("static", "audio")
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

async def _edge_speak(text, voice_name, filename):
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(filename)

def generate_bot_audio(text, voice_type="female"):
    if not text or not text.strip():
        return None

    file_id = str(uuid.uuid4())
    filename = f"voice_{file_id}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)
    
    voice_key = voice_type.lower()
    if voice_key not in VOICES:
        voice_key = "female"
    
    # --- Level 1: 嘗試原本的 Edge-TTS ---
    try:
        print(f"[VOICE] L1 Trying original Edge-TTS: {voice_key}...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_edge_speak(text, VOICES[voice_key], filepath))
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                print("[VOICE] L1 Success!")
                return f"/static/audio/{filename}"
        finally:
            loop.close()
    except Exception:
        print("[VOICE] L1 Failed (403). Trying L2 (Cross-Region Edge)...")

    # --- Level 2: 嘗試跨地區 Edge-TTS (避開封鎖) ---
    try:
        backup_voice = BACKUP_VOICES.get(voice_key, "zh-CN-XiaoxiaoNeural")
        print(f"[VOICE] L2 Trying Backup Edge-TTS: {backup_voice}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_edge_speak(text, backup_voice, filepath))
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                print("[VOICE] L2 Success (Using High-Quality Backup)!")
                return f"/static/audio/{filename}"
        finally:
            loop.close()
    except Exception:
        print("[VOICE] L2 Failed. Falling back to L3 (Extreme Offline Simulation)...")

    # --- Level 3: 離線語音極端模擬 (確保男女有別) ---
    try:
        engine = pyttsx3.init()
        # 尋找所有可用中文語音
        voices = engine.getProperty('voices')
        selected_v = None
        for v in voices:
            if "chinese" in v.name.lower() or "taiwan" in v.name.lower() or "han" in v.name.lower():
                selected_v = v.id
                break
        
        if selected_v: engine.setProperty('voice', selected_v)
        
        # 透過語速製造性別錯覺
        if voice_key in ["male", "sunny", "elder"]:
            engine.setProperty('rate', 150)  # 說話慢一點、沉一點 (模擬男聲)
        elif voice_key == "loli":
            engine.setProperty('rate', 250)  # 說話極快 (模擬小孩)
        else:
            engine.setProperty('rate', 190)  # 一般女聲
            
        engine.save_to_file(text, filepath)
        engine.runAndWait()
        
        if os.path.exists(filepath):
            print(f"[VOICE] L3 Success (Offline Simulation for {voice_key})")
            return f"/static/audio/{filename}"
    except Exception as e:
        print(f"[VOICE] All levels failed: {e}")

    return None
