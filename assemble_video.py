
        """
assemble_video.py -- Pexels se topic-relevant horror B-roll download karta
hai (keyword matching ke through, horror-mood explicit keywords ke saath),
audio ko mute karta hai (original clip ka), aur poore 1920x1080 frame ko
crop-to-fill se bharta hai (koi black bars nahi).
"""

import os
import random
import requests
from moviepy.editor import (
    VideoFileClip, AudioFileClip, concatenate_videoclips,
    CompositeVideoClip, ColorClip
)
from config import PEXELS_API_KEY, AUDIO_FILE, VIDEO_FILE, OUTPUT_DIR

CLIPS_DIR = f"{OUTPUT_DIR}/clips"
TARGET_W, TARGET_H = 1920, 1080

TOPIC_KEYWORD_MAP = {
    "school": ["creepy empty school hallway", "haunted abandoned school", "dark old classroom horror"],
    "haveli": ["haunted mansion horror", "creepy abandoned mansion interior", "spooky old haveli dark"],
    "hostel": ["dark creepy dormitory hallway", "haunted hostel room horror", "eerie building corridor night"],
    "train": ["creepy train at night horror", "haunted train compartment eerie", "dark train station fog horror"],
    "kuan": ["creepy old well horror", "haunted dark well night", "spooky abandoned well fog"],
    "doctor": ["creepy hospital corridor horror", "haunted empty hospital room", "eerie dark hospital hallway night"],
    "dhaba": ["creepy empty highway night horror", "haunted roadside dhaba fog", "eerie deserted highway night"],
}

FALLBACK_TERMS = [
    "dark forest night horror", "creepy fog road night", "horror candle flame dark room",
    "haunted abandoned building creepy", "eerie dark hallway horror", "spooky shadow silhouette dark"
]


def get_search_terms_for_topic(topic: str):
    topic_lower = topic.lower()
    matched_terms = []
    for keyword, searches in TOPIC_KEYWORD_MAP.items():
        if keyword in topic_lower:
            matched_terms.extend(searches)

    if not matched_terms:
        matched_terms = FALLBACK_TERMS

    return matched_terms


def download_stock_clips(topic: str, count=8):
    os.makedirs(CLIPS_DIR, exist_ok=True)
    headers = {"Authorization": PEXELS_API_KEY}
    search_terms = get_search_terms_for_topic(topic)
    paths = []

    for i in range(count):
        term = random.choice(search_terms)
        resp = requests.get(
            "https://api.pexels.com/videos/search",
            headers=headers,
            params={"query": term, "per_page": 6, "orientation": "landscape"}
        )
        if resp.status_code != 200:
            continue
        videos = resp.json().get("videos", [])
        if not videos:
            continue

        video = random.choice(videos)
        video_files = sorted(video["video_files"], key=lambda v: v.get("width", 0))
        file_url = video_files[len(video_files) // 2]["link"]

        out_path = f"{CLIPS_DIR}/clip_{i}.mp4"
        try:
            r = requests.get(file_url, timeout=30)
            with open(out_path, "wb") as f:
                f.write(r.content)
            paths.append(out_path)
        except Exception as e:
            print(f"Failed to download clip for '{term}': {e}")

    return paths


def fit_crop_to_fill(clip, target_w=TARGET_W, target_h=TARGET_H):
    clip_ratio = clip.w / clip.h
    target_ratio = target_w / target_h

    if clip_ratio > target_ratio:
        new_height = target_h
        new_width = int(clip.w * (target_h / clip.h))
    else:
        new_width = target_w
        new_height = int(clip.h * (target_w / clip.w))

    resized = clip.resize(newsize=(new_width, new_height))
    cropped = resized.crop(
        x_center=new_width / 2, y_center=new_height / 2,
        width=target_w, height=target_h
    )
    return cropped


def build_video(topic: str = ""):
    audio = AudioFileClip(AUDIO_FILE)
    target_duration = audio.duration

    clip_paths = download_stock_clips(topic, count=10)
    if not clip_paths:
        raise RuntimeError("No stock clips downloaded -- check PEXELS_API_KEY or network")

    clips = []
    total = 0
    idx = 0
    while total < target_duration:
        path = clip_paths[idx % len(clip_paths)]
        idx += 1
        try:
            c = VideoFileClip(path)
            c = c.without_audio()
        except Exception as e:
            print(f"Skipping unreadable clip {path}: {e}")
            continue

        c = fit_crop_to_fill(c)
        clips.append(c)
        total += c.duration

    full = concatenate_videoclips(clips, method="compose")
    full = full.subclip(0, target_duration)

    overlay = ColorClip(size=(TARGET_W, TARGET_H), color=(0, 0, 0)).set_opacity(0.35).set_duration(target_duration)

    final = CompositeVideoClip([full, overlay]).set_audio(audio)
    final.write_videofile(VIDEO_FILE, fps=24, codec="libx264", audio_codec="aac", threads=4)

    for p in clip_paths:
        try:
            os.remove(p)
        except OSError:
            pass


if __name__ == "__main__":
    build_video()
    print(f"Video saved to {VIDEO_FILE}")
