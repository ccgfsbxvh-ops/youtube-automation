"""
assemble_video.py -- background footage + narration audio + captions ko combine
karke final video banata hai.

Approach: Pexels se dark/horror-themed stock video clips download karta hai,
unhe loop/concat karke audio ki length tak stretch karta hai, aur simple
burned-in captions overlay karta hai.
"""

import os
import json
import random
import requests
from moviepy.editor import (
    VideoFileClip, AudioFileClip, concatenate_videoclips,
    CompositeVideoClip, TextClip, ColorClip
)
from config import PEXELS_API_KEY, AUDIO_FILE, VIDEO_FILE, OUTPUT_DIR

PEXELS_SEARCH_TERMS = [
    "dark forest night", "abandoned house", "fog road night",
    "old hallway", "candle flame dark", "empty street night"
]

CLIPS_DIR = f"{OUTPUT_DIR}/clips"


def download_stock_clips(count=6):
    os.makedirs(CLIPS_DIR, exist_ok=True)
    headers = {"Authorization": PEXELS_API_KEY}
    paths = []

    for i in range(count):
        term = random.choice(PEXELS_SEARCH_TERMS)
        resp = requests.get(
            "https://api.pexels.com/videos/search",
            headers=headers,
            params={"query": term, "per_page": 5, "orientation": "landscape"}
        )
        resp.raise_for_status()
        videos = resp.json().get("videos", [])
        if not videos:
            continue

        video = random.choice(videos)
        # pick a mid-quality file to keep render fast
        video_files = sorted(video["video_files"], key=lambda v: v.get("width", 0))
        file_url = video_files[len(video_files) // 2]["link"]

        out_path = f"{CLIPS_DIR}/clip_{i}.mp4"
        r = requests.get(file_url)
        with open(out_path, "wb") as f:
            f.write(r.content)
        paths.append(out_path)

    return paths


def build_video():
    audio = AudioFileClip(AUDIO_FILE)
    target_duration = audio.duration

    clip_paths = download_stock_clips(count=8)
    if not clip_paths:
        raise RuntimeError("No stock clips downloaded -- check PEXELS_API_KEY")

    clips = []
    total = 0
    while total < target_duration:
        for p in clip_paths:
            c = VideoFileClip(p).without_audio()
            clips.append(c)
            total += c.duration
            if total >= target_duration:
                break

    full = concatenate_videoclips(clips, method="compose")
    full = full.subclip(0, target_duration)
    full = full.resize(height=1080)  # normalize resolution

    # dark overlay for horror mood + readability of captions
    overlay = ColorClip(size=full.size, color=(0, 0, 0)).set_opacity(0.35).set_duration(target_duration)

    final = CompositeVideoClip([full, overlay]).set_audio(audio)
    final.write_videofile(VIDEO_FILE, fps=24, codec="libx264", audio_codec="aac", threads=4)

    # cleanup temp clips to save disk
    for p in clip_paths:
        os.remove(p)


if __name__ == "__main__":
    build_video()
    print(f"Video saved to {VIDEO_FILE}")
