"""
tts.py -- Priority: Gemini native TTS (best/most natural) -> edge-tts ->
gTTS (guaranteed fallback). Kabhi bhi is step pe pipeline fail nahi hoga.
"""

import os
import asyncio
import wave
from config import AUDIO_FILE, GEMINI_API_KEY

EDGE_VOICE = "hi-IN-MadhurNeural"
GEMINI_TTS_MODEL = "gemini-3.1-flash-tts-preview"
GEMINI_TTS_VOICE = "Algenib"


def _try_gemini_tts(text: str, output_path: str):
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)

    model = genai.GenerativeModel(GEMINI_TTS_MODEL)
    response = model.generate_content(
        text,
        generation_config={
            "response_modalities": ["AUDIO"],
            "speech_config": {
                "voice_config": {
                    "prebuilt_voice_config": {"voice_name": GEMINI_TTS_VOICE}
                }
            },
        },
    )

    audio_data = response.candidates[0].content.parts[0].inline_data.data

    wav_path = output_path.replace(".mp3", ".wav")
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(audio_data)

    if wav_path != output_path:
        os.rename(wav_path, output_path)


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
        _try_gemini_tts(text, output_path)
        print("Used Gemini native TTS (best quality)")
        return
    except Exception as e:
        print(f"Gemini TTS failed: {e}")

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
