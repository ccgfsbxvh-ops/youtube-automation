"""
tts.py -- script ko narration audio mein convert karta hai.
edge-tts free hai, koi API key nahi chahiye.
"""

import asyncio
import edge_tts
from config import VOICE, SCRIPT_FILE, AUDIO_FILE


async def generate_audio(text: str, output_path: str):
    communicate = edge_tts.Communicate(text, VOICE, rate="-2%")  # thoda slow, horror feel ke liye
    await communicate.save(output_path)


if __name__ == "__main__":
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script_text = f.read()

    asyncio.run(generate_audio(script_text, AUDIO_FILE))
    print(f"Audio saved to {AUDIO_FILE}")
