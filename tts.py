"""
tts.py -- edge-tts (natural voice) try karta hai, fail hone par gTTS
(reliable fallback) use karta hai. ElevenLabs free-tier API se voice
generate nahi kar sakta (unki policy), isliye chain se hataya.
"""

import asyncio
from config import AUDIO_FILE

EDGE_VOICE = "hi-IN-MadhurNeural"


async def _try_edge_tts_async(text: str, output_path: str):
    import edge_tts
    communicate = edge_tts.Communicate(text, EDGE_VOICE, rate="-5%")
    await communicate.save(output_path)


def _try_edge_tts(text: str, output_path: str):
    asyncio.run(_try_edge_tts_async(text, output_path))


def _try_gtts(text: str, output_path: str):
    from gtts import gTTS
    tts = gTTS(text=text, lang="hi", slow=False)
    tts.save(output_path)


def generate_audio_sync(text: str, output_path: str):
    try:
        _try_edge_tts(text, output_path)
        print("Used edge-tts (natural voice)")
        return
    except Exception as e:
        print(f"edge-tts failed: {e}")

    _try_gtts(text, output_path)
    print("Used gTTS (fallback voice)")


if __name__ == "__main__":
    from config import SCRIPT_FILE
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script_text = f.read()
    generate_audio_sync(script_text, AUDIO_FILE)
    print(f"Audio saved to {AUDIO_FILE}")
