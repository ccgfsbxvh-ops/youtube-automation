"""
tts.py -- Priority order try karta hai: ElevenLabs (best quality, limited
free quota) -> edge-tts (natural, kabhi kabhi Microsoft-side issue) ->
gTTS (robotic but always works). Jo bhi pehle successfully chale, wahi use
hoga -- isse pipeline kabhi bhi is step pe fail nahi hota.
"""

import os
import asyncio
from config import AUDIO_FILE

EDGE_VOICE = "hi-IN-MadhurNeural"
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # "Rachel" - default, badla ja sakta hai


def _try_elevenlabs(text: str, output_path: str):
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY not set")

    from elevenlabs import ElevenLabs
    client = ElevenLabs(api_key=api_key)

    audio = client.text_to_speech.convert(
        voice_id=ELEVENLABS_VOICE_ID,
        text=text,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    with open(output_path, "wb") as f:
        for chunk in audio:
            f.write(chunk)


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
        _try_elevenlabs(text, output_path)
        print("Used ElevenLabs (best quality)")
        return
    except Exception as e:
        print(f"ElevenLabs failed/unavailable: {e}")

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
