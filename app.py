from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import glob
import time
from tongtong.brain import TongTongBrain
from tongtong.voice import generate_bot_audio
from tongtong.text_utils import bot_speak_re

app = Flask(__name__)
CORS(app)

# Initialize Brain
brain = TongTongBrain()

@app.route('/')
def index():
    return render_template('index.html')

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
    
    # Clean text for speech
    cleaned_text = bot_speak_re(response_text)
    
    # Generate audio file
    audio_url = generate_bot_audio(cleaned_text, voice_type)

    return jsonify({
        'reply': response_text,
        'audio_url': audio_url
    })

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
