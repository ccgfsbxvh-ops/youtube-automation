"""
generate_script.py -- ek horror script generate karta hai using Gemini (free tier).
Script + title + description SAB EK HI API call mein generate karta hai
(quota bachane ke liye). Script chhota rakha gaya hai (500-600 words) taaki
per-minute token quota na tute.
Quota/rate-limit error aane par khud retry karta hai.
"""

import json
import os
import random
import time
import google.generativeai as genai
from config import GEMINI_API_KEY, TOPIC_POOL, SCRIPT_FILE, OUTPUT_DIR

USED_TOPICS_FILE = "used_topics.json"
MODEL_NAME = "gemini-2.0-flash-lite"
MAX_RETRIES = 6
RETRY_WAIT_SECONDS = 25


def get_next_topic():
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


def _call_with_retry(model, prompt):
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return model.generate_content(prompt)
        except Exception as e:
            last_error = e
            msg = str(e)
            if "429" in msg or "quota" in msg.lower() or "rate" in msg.lower():
                wait = RETRY_WAIT_SECONDS * attempt
                print(f"Quota/rate limit hit (attempt {attempt}/{MAX_RETRIES}). Waiting {wait}s...")
                time.sleep(wait)
                continue
            raise
    raise last_error


def generate_everything(topic: str) -> dict:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(MODEL_NAME)

    prompt = f"""Tum ek expert Hindi horror story YouTube script writer ho.
Topic: {topic}

Mujhe teen cheezein chahiye, STRICTLY JSON format mein (koi extra text, koi markdown backticks nahi):

{{
  "script": "yahan pura 500-600 words ka Hindi horror narration script",
  "title": "yahan YouTube title, max 80 characters",
  "description": "yahan YouTube description, 3-4 lines"
}}

Script rules:
- Sirf 500-600 words, isse zyada mat likhna
- Simple bolchaal ki Hindi (Hinglish thoda chalega but mostly Hindi)
- Strong hook se shuru (pehle 10 second mein curiosity)
- Chhota build-up, phir climax, phir twist ending
- Beech mein "dosto" jaisa 1-2 engagement phrase
- Sirf narration text, koi stage directions ya headings nahi
- End mein "channel ko subscribe karo agli kahani ke liye" jaisa CTA

Title rules: curiosity-driven, emoji ok, Hindi/Hinglish.
Description rules: story ka hook, subscribe request, phir hashtags.

Sirf JSON do, kuch aur nahi."""

    response = _call_with_retry(model, prompt)
    text = response.text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    topic = get_next_topic()
    print(f"Selected topic: {topic}")

    result = generate_everything(topic)

    with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
        f.write(result["script"])
    print(f"Script saved to {SCRIPT_FILE} ({len(result['script'].split())} words)")

    meta = {"title": result["title"], "description": result["description"]}
    with open(f"{OUTPUT_DIR}/metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"Title: {meta['title']}")