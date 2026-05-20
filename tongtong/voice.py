import os
import asyncio
import uuid
import sys
import edge_tts
import pyttsx3

# --- 語音性格整形設定：拉開「男生」與「陽光男孩」的差距 ---
VOICE_PROFILES = {
    "female": {"voice": "zh-TW-HsiaoChenNeural", "rate": "+0%", "pitch": "+0Hz"},
    "male":   {"voice": "zh-TW-YunJheNeural",    "rate": "-5%", "pitch": "-5Hz"},  # 男生：調低、調慢，聽起來更成熟穩重
    "loli":   {"voice": "zh-TW-HsiaoChenNeural", "rate": "+30%", "pitch": "+15Hz"}, # 蘿莉：極快極尖，像小女孩
    "sister": {"voice": "zh-TW-HsiaoYuNeural",    "rate": "-12%", "pitch": "-4Hz"},  # 姐姐：慢速溫柔
    "sunny":  {"voice": "zh-TW-YunJheNeural",    "rate": "+20%", "pitch": "+10Hz"}  # 陽光男孩：大幅調高、變快，聽起來像熱血少年
}


if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except: pass

AUDIO_DIR = os.path.join("static", "audio")
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

async def _edge_speak(text, profile, filename):
    communicate = edge_tts.Communicate(
        text, 
        profile["voice"], 
        rate=profile["rate"], 
        pitch=profile["pitch"]
    )
    await communicate.save(filename)

def generate_bot_audio(text, voice_type="female"):
    if not text or not text.strip():
        return None

    file_id = str(uuid.uuid4())
    filename = f"voice_{file_id}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)
    
    voice_key = voice_type.lower()
    if voice_key not in VOICE_PROFILES:
        voice_key = "female"
    
    # --- Level 1: 台灣高品質客製化語音 ---
    try:
        profile = VOICE_PROFILES[voice_key]
        print(f"[VOICE] L1 Trying Taiwan Customized: {voice_key} ({profile['voice']})")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_edge_speak(text, profile, filepath))
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                print("[VOICE] L1 Success!")
                return f"/static/audio/{filename}"
        finally:
            loop.close()
    except Exception:
        print("[VOICE] L1 (TW) Failed. Falling back to offline (L3)...")

    # --- Level 3: 離線語音模擬 ---
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for v in voices:
            if "taiwan" in v.name.lower() or "chinese" in v.name.lower():
                engine.setProperty('voice', v.id)
                break
        
        if voice_key in ["male", "sunny"]:
            # 離線模式也手動拉開語速
            rate = 140 if voice_key == "male" else 220
            engine.setProperty('rate', rate)
        elif voice_key == "loli": engine.setProperty('rate', 250)
        elif voice_key == "sister": engine.setProperty('rate', 150)
        else: engine.setProperty('rate', 200)
            
        engine.save_to_file(text, filepath)
        engine.runAndWait()
        return f"/static/audio/{filename}"
    except:
        return None
