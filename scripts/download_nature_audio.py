"""
簡單的下載腳本：將指定的音檔 URL 下載到 `static/audio/nature/`。

使用方式：
  python scripts/download_nature_audio.py

編輯下方的 `FILES_TO_DOWNLOAD` 列表，填入 (url, filename) 元組。
請確認音檔有允許下載與使用的授權。
"""
import os
import requests

TARGET_DIR = os.path.join('static', 'audio', 'nature')
os.makedirs(TARGET_DIR, exist_ok=True)

# 在這裡填入要下載的 (url, filename)
FILES_TO_DOWNLOAD = [
    # ('https://example.com/path/to/rain_thunder1.mp3', 'rain_thunder1.mp3'),
    # ('https://example.com/path/to/fall_morning_river.mp3', 'fall_morning_river.mp3'),
    # ('https://example.com/path/to/ocean_wave1.mp3', 'ocean_wave1.mp3'),
]

def download(url, filename):
    dest = os.path.join(TARGET_DIR, filename)
    print(f"下載: {url} -> {dest}")
    try:
        resp = requests.get(url, stream=True, timeout=30)
        resp.raise_for_status()
        with open(dest, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print("完成")
    except Exception as e:
        print("下載失敗:", e)

def main():
    if not FILES_TO_DOWNLOAD:
        print("請在 FILES_TO_DOWNLOAD 裡填入要下載的音檔 URL 與檔名。")
        return
    for url, filename in FILES_TO_DOWNLOAD:
        download(url, filename)

if __name__ == '__main__':
    main()
