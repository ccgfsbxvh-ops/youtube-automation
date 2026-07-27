"""
tts.py -- script ko narration audio mein convert karta hai using gTTS
(Google Text-to-Speech, free aur stable, koi token issue nahi).
"""

from gtts import gTTS
from config import SCRIPT_FILE, AUDIO_FILE


def generate_audio_sync(text: str, output_path: str):
    tts = gTTS(text=text, lang="hi", slow=False)
    tts.save(output_path)


if __name__ == "__main__":
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script_text = f.read()

    generate_audio_sync(script_text, AUDIO_FILE)
    print(f"Audio saved to {AUDIO_FILE}")