"""
generate_script.py -- Groq (free, generous quota) use karke horror script
generate karta hai. Script + title + description ek hi call mein.
"""

import json
import os
import random
from groq import Groq
from config import TOPIC_POOL, SCRIPT_FILE, OUTPUT_DIR

USED_TOPICS_FILE = "used_topics.json"
MODEL_NAME = "llama-3.3-70b-versatile"


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


def generate_everything(topic: str) -> dict:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    prompt = f"""Tum ek expert Hindi horror story YouTube script writer ho.
Topic: {topic}

Mujhe teen cheezein chahiye, STRICTLY JSON format mein (koi extra text, koi markdown backticks nahi):

{{
  "script": "yahan pura 500-600 words ka Hindi horror narration script",
  "title": "yahan YouTube title, max 80 characters",
  "description": "yahan YouTube description, 3-4 lines"
}}

Script rules:
- Sirf 500-600 words
- Simple bolchaal ki Hindi
- Strong hook se shuru
- Chhota build-up, phir climax, phir twist ending
- Sirf narration text, koi headings nahi
- End mein subscribe CTA

Sirf JSON do, kuch aur nahi."""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
    )

    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()
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