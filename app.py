from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import glob
import time
from dotenv import load_dotenv
from tongtong.brain import TongTongBrain
from tongtong.voice import generate_bot_audio
from gtts import gTTS
from tongtong.text_utils import bot_speak_re, bot_clean_text

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Brain
brain = TongTongBrain()

@app.route('/')
def index():
    mode = request.args.get('mode', '通通沒問題')
    voice_type = request.args.get('voice', 'female')
    
    # Initialize the mode and get welcome message
    welcome_text = brain.set_mode(mode)
    
    # Pre-clean and generate audio for welcome message
    display_text = bot_clean_text(welcome_text)
    cleaned_speech = bot_speak_re(welcome_text)
    audio_url = generate_bot_audio(cleaned_speech, voice_type)
    
    return render_template('index.html', 
                           initial_message=display_text, 
                           initial_audio=audio_url,
                           current_mode=mode,
                           current_voice=voice_type)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '').strip()
    voice_type = data.get('voice_type', 'female') # 'female' or 'male'
    mode = data.get('mode', '好心情')

    # If mode changed, return the welcome message for the new mode
    if mode != brain.mode:
        response_text = brain.set_mode(mode)
    elif user_input:
        # Process regular text input
        response_text = brain.process_input(user_input)
    else:
        # No change and no input
        return jsonify({'status': 'ignored'})
    
    # Handle special audio markers
    import re
    audio_url = None
    next_audio_url = None
    payload_text = response_text
    
    # Check for [AUDIO:...] marker (legacy)
    if isinstance(response_text, str) and response_text.startswith("[AUDIO:"):
        end_idx = response_text.find("]")
        if end_idx != -1:
            audio_url = response_text[len("[AUDIO:"):end_idx]
            payload_text = response_text[end_idx+1:].strip()
    
    # Check for [NEXT_AUDIO:...] marker (for nature sounds)
    if "[NEXT_AUDIO:" in payload_text:
        match = re.search(r'\[NEXT_AUDIO:(.*?)\]', payload_text)
        if match:
            next_audio_url = match.group(1)
            payload_text = payload_text.replace(match.group(0), '').strip()

    # Prepare UI text
    display_text = bot_clean_text(payload_text)

    # Generate TTS from cleaned text
    cleaned_text = bot_speak_re(payload_text)
    audio_url = generate_bot_audio(cleaned_text, voice_type)
    
    # If next audio URL exists, verify it exists; otherwise clear it
    if next_audio_url:
        fs_path = next_audio_url.lstrip('/')
        if not os.path.exists(fs_path):
            next_audio_url = None

    result = {
        'reply': display_text,
        'audio_url': audio_url
    }
    if next_audio_url:
        result['next_audio_url'] = next_audio_url
    
    return jsonify(result)


@app.route('/api/tts_preview', methods=['POST'])
def tts_preview():
    """Generate TTS for a given text and voice_type (used for preview on voice change)."""
    data = request.json or {}
    text = data.get('text', '').strip()
    voice_type = data.get('voice_type', 'female')
    if not text:
        return jsonify({'status': 'error', 'message': 'no text provided'}), 400

    print(f"[tts_preview] received text len={len(text)} voice_type={voice_type}")
    try:
        cleaned_text = bot_speak_re(text)
        print(f"[tts_preview] cleaned_text='{cleaned_text}'")
        if not cleaned_text:
            cleaned_text = text
            print("[tts_preview] cleaned_text empty, falling back to original text")

        # Use gTTS directly for quick, reliable preview generation (avoids edge-tts failures)
        import uuid
        file_id = str(uuid.uuid4())
        filename = f"voice_{file_id}.mp3"
        filepath = os.path.join('static', 'audio', filename)
        try:
            import io
            tts = gTTS(text=cleaned_text, lang='zh-TW')
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            with open(filepath, 'wb') as f:
                f.write(buf.read())
            audio_url = f"/static/audio/{filename}"
            print(f"[tts_preview] generated via gTTS -> {audio_url}")
            return jsonify({'audio_url': audio_url})
        except Exception as ge:
            print(f"[tts_preview] gTTS write_to_fp error: {ge}")
            # fallback to shared generator
            audio_url = generate_bot_audio(cleaned_text, voice_type)
            print(f"[tts_preview] fallback generate_bot_audio -> {audio_url}")
            return jsonify({'audio_url': audio_url})
    except Exception as e:
        print(f"[tts_preview] exception: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/games')
def games_index():
    """Render the games index page."""
    return render_template('games_index.html')


@app.route('/games/gomoku')
def games_gomoku():
    """Render the Gomoku game page for embedding or direct access."""
    return render_template('games/gomoku.html')

@app.route('/api/cleanup', methods=['POST'])
def cleanup():
    """Cleanup old audio files."""
    files = glob.glob('static/audio/voice_*.mp3')
    now = time.time()
    count = 0
    for f in files:
        # Delete files older than 10 minutes
        if os.stat(f).st_mtime < now - 600:
            try:
                os.remove(f)
                count += 1
            except:
                pass
    return jsonify({'status': 'ok', 'deleted': count})

if __name__ == '__main__':
    # Cleanup audio dir on start
    files = glob.glob('static/audio/voice_*.mp3')
    for f in files:
        try: os.remove(f)
        except: pass
        
    # Run on all interfaces for mobile access (need to check local IP)
    app.run(host='0.0.0.0', port=5000, debug=True)
