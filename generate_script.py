"""
generate_script.py -- ek horror script generate karta hai using Gemini (free tier).
Topic pool se ek topic pick karta hai jo abhi tak use nahi hua (used_topics.json track karta hai).
"""

import json
import os
import random
import google.generativeai as genai
from config import GEMINI_API_KEY, TOPIC_POOL, SCRIPT_FILE, OUTPUT_DIR

USED_TOPICS_FILE = "used_topics.json"


def get_next_topic():
    """Pehle unused topic pool se pick karo, sab use ho gaye toh reset karo."""
    if os.path.exists(USED_TOPICS_FILE):
        with open(USED_TOPICS_FILE, "r") as f:
            used = json.load(f)
    else:
        used = []

    available = [t for t in TOPIC_POOL if t not in used]
    if not available:
        used = []
        available = TOPIC_POOL[:]

    topic = random.choice(available)
    used.append(topic)
    with open(USED_TOPICS_FILE, "w") as f:
        json.dump(used, f, ensure_ascii=False, indent=2)

    return topic


def generate_script(topic: str) -> str:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""Tum ek expert Hindi horror story YouTube script writer ho.
Topic: {topic}

Ek 7-8 minute ka (roughly 900-1100 words) horror narration script likho jo:
- Simple bolchaal ki Hindi mein ho (Hinglish thoda chalega but mostly Hindi)
- Ek strong hook se shuru ho (pehle 10 second mein curiosity banao)
- Slow build-up, phir climax, phir twist ending
- Second person ya first person narrator style mein ho, jaise koi kahani suna raha ho
- Beech beech mein "dosto", "ab suniye aage" jaise engagement phrases ho
- Sirf narration text do, koi stage directions ya headings nahi, seedha bolne wala script
- End mein "channel ko subscribe karo agli kahani ke liye" jaisa CTA daalo

Sirf final script do, koi extra explanation nahi."""

    response = model.generate_content(prompt)
    return response.text.strip()


def generate_title_description(topic: str, script: str) -> dict:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""Is horror story ke liye ek clickable YouTube title aur description do.
Topic: {topic}
Script (pehle 300 chars): {script[:300]}

Format strictly JSON mein do, kuch aur text nahi:
{{"title": "...", "description": "..."}}

Title rules: max 80 characters, curiosity-driven, emoji ok, Hindi/Hinglish.
Description rules: 3-4 lines, story ka hook, phir subscribe request, phir hashtags."""

    response = model.generate_content(prompt)
    text = response.text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    topic = get_next_topic()
    print(f"Selected topic: {topic}")

    script = generate_script(topic)
    with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
        f.write(script)
    print(f"Script saved to {SCRIPT_FILE} ({len(script.split())} words)")

    meta = generate_title_description(topic, script)
    with open(f"{OUTPUT_DIR}/metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"Title: {meta['title']}")
