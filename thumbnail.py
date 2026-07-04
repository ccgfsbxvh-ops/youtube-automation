"""
thumbnail.py -- simple dark horror-style thumbnail generate karta hai
using PIL (text overlay on a dark gradient/still frame from the video).
"""

import json
import textwrap
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip
from config import VIDEO_FILE, THUMBNAIL_FILE, OUTPUT_DIR

WIDTH, HEIGHT = 1280, 720


def get_frame_background():
    """Video ke beech se ek frame nikal ke background banate hain."""
    clip = VideoFileClip(VIDEO_FILE)
    frame = clip.get_frame(clip.duration / 2)
    img = Image.fromarray(frame).resize((WIDTH, HEIGHT))
    clip.close()
    return img


def add_dark_gradient(img):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(HEIGHT):
        alpha = int(180 * (y / HEIGHT))
        draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def add_title_text(img, title):
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70)
    except IOError:
        font = ImageFont.load_default()

    wrapped = textwrap.fill(title, width=18)
    lines = wrapped.split("\n")
    y = HEIGHT - (len(lines) * 85) - 40

    for line in lines:
        # stroke/outline for readability
        draw.text((44, y), line, font=font, fill="white",
                   stroke_width=4, stroke_fill="black")
        y += 85

    return img


def build_thumbnail():
    with open(f"{OUTPUT_DIR}/metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)

    img = get_frame_background()
    img = add_dark_gradient(img)
    img = add_title_text(img, meta["title"])
    img.convert("RGB").save(THUMBNAIL_FILE, quality=95)


if __name__ == "__main__":
    build_thumbnail()
    print(f"Thumbnail saved to {THUMBNAIL_FILE}")
