"""
tts.py -- edge-tts (Microsoft, natural-sounding free voice) use karta hai.
"""

import asyncio
from config import AUDIO_FILE

VOICE = "hi-IN-MadhurNeural"  # natural male Hindi voice


async def _generate(text: str, output_path: str):
    import edge_tts
    communicate = edge_tts.Communicate(text, VOICE, rate="-5%")
    await communicate.save(output_path)


def generate_audio_sync(text: str, output_path: str):
    asyncio.run(_generate(text, output_path))


if __name__ == "__main__":
    from config import SCRIPT_FILE
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script_text = f.read()
    generate_audio_sync(script_text, AUDIO_FILE)
    print(f"Audio saved to {AUDIO_FILE}")
