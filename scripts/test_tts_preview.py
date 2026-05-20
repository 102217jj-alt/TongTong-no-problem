from app import app
import os

with app.test_client() as c:
    resp = c.post('/api/tts_preview', json={'text':'測試男聲','voice_type':'male'})
    print('status_code:', resp.status_code)
    print('json:', resp.get_json())
    data = resp.get_json() or {}
    audio_url = data.get('audio_url')
    if audio_url:
        fs_path = audio_url.lstrip('/')
        print('fs_path:', fs_path)
        print('exists:', os.path.exists(fs_path))
        if os.path.exists(fs_path):
            print('file size:', os.path.getsize(fs_path))
    else:
        print('No audio_url returned')
