"""
config.py -- saare settings ek jagah.
API keys yahan HARDCODE mat karo -- .env file use karo (README dekh).
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ---------- API KEYS (from .env, never commit these) ----------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# ---------- CHANNEL SETTINGS ----------
CHANNEL_LANGUAGE = "hi"  # hindi
VIDEO_LENGTH_TARGET_SECONDS = 480  # ~8 min (good for horror narration + ads)
VOICE = "hi-IN-MadhurNeural"  # edge-tts hindi male voice (free, no key needed)
# other option: "hi-IN-SwaraNeural" (female)

# ---------- CONTENT TOPICS POOL ----------
# Script randomly/sequentially picks from these so content doesn't repeat.
# Add more anytime -- the more variety, the less "repetitive content" risk.
TOPIC_POOL = [
    "Ek highway dhaba jahan raat 12 baje ajeeb cheezein hoti hain",
    "Ek purani haveli jisme ek pariwar shift hota hai aur ajeeb awazein sunta hai",
    "Ek hostel room jisme naya student aata hai aur purani kahani pata chalti hai",
    "Ek train ka aakhri dabba jisme log gayab ho jaate hain",
    "Ek gaon ka kuan jisme koi bhi jhaakta hai woh gayab ho jaata hai",
    "Ek doctor ki night shift jisme ek marij baar baar wapas aata hai",
    "Ek purani school jisme ek chhatra ka bhoot ghoomta hai",
]

# ---------- OUTPUT PATHS ----------
OUTPUT_DIR = "output"
SCRIPT_FILE = f"{OUTPUT_DIR}/script.txt"
AUDIO_FILE = f"{OUTPUT_DIR}/narration.mp3"
VIDEO_FILE = f"{OUTPUT_DIR}/final_video.mp4"
THUMBNAIL_FILE = f"{OUTPUT_DIR}/thumbnail.png"

# ---------- YOUTUBE UPLOAD SETTINGS ----------
YOUTUBE_CATEGORY_ID = "24"  # Entertainment
YOUTUBE_PRIVACY_STATUS = "public"  # change to "private" if you want to review before publishing
DEFAULT_TAGS = ["horror story hindi", "dar", "bhoot", "horror kahani", "hindi horror stories"]
