#!/usr/bin/env python3
"""
Test script to verify available edge-tts voices for Traditional Chinese.
"""
import asyncio
import edge_tts

async def list_voices():
    """List all available voices and filter for zh-TW."""
    voices = await edge_tts.list_voices()
    print("Available Traditional Chinese (zh-TW) voices:")
    print("=" * 60)
    for voice in voices:
        if 'zh-TW' in voice.get('Locale', ''):
            name = voice.get('Name', 'Unknown')
            gender = voice.get('Gender', 'Unknown')
            lang = voice.get('Locale', 'Unknown')
            print(f"  Name: {name}")
            print(f"    Gender: {gender}")
            print(f"    Locale: {lang}")
            print()

async def test_voice(voice_name, test_text="你好，我是通通。"):
    """Test generating speech with a specific voice."""
    print(f"\nTesting voice: {voice_name}")
    print(f"Text: {test_text}")
    try:
        communicate = edge_tts.Communicate(test_text, voice_name)
        filename = f"test_{voice_name.replace('-', '_')}.mp3"
        await communicate.save(filename)
        print(f"✓ Success! Saved to {filename}")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

async def main():
    # List all voices
    await list_voices()
    
    # Test some known voices
    print("\n" + "=" * 60)
    print("Testing known zh-TW voices:")
    print("=" * 60)
    
    test_voices = [
        "zh-TW-HsiaoChenNeural",
        "zh-TW-YunJheNeural",
        "zh-TW-HsiuMenNeural",
        "zh-TW-HsiaozuNeural",
    ]
    
    for voice in test_voices:
        await test_voice(voice)

if __name__ == "__main__":
    asyncio.run(main())
