"""
main.py -- pura pipeline ek saath chalata hai:
script -> audio -> video -> thumbnail -> upload

Ye hi file GitHub Actions daily run karega.
"""

import os
import traceback
from config import OUTPUT_DIR

def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("== Step 1: Generating script ==")
    import generate_script
    generate_script.__name__ = "__main__"  # noop, just for clarity

    from generate_script import get_next_topic, generate_script as gen_script, generate_title_description
    import json
    from config import SCRIPT_FILE

    topic = get_next_topic()
    print(f"Topic: {topic}")
    script = gen_script(topic)
    with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
        f.write(script)

    meta = generate_title_description(topic, script)
    with open(f"{OUTPUT_DIR}/metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"Title: {meta['title']}")

    print("== Step 2: Generating narration audio ==")
    import asyncio
    from tts import generate_audio
    from config import AUDIO_FILE
    asyncio.run(generate_audio(script, AUDIO_FILE))

    print("== Step 3: Assembling video ==")
    from assemble_video import build_video
    build_video()

    print("== Step 4: Creating thumbnail ==")
    from thumbnail import build_thumbnail
    build_thumbnail()

    print("== Step 5: Uploading to YouTube ==")
    from upload_youtube import upload_video
    video_id = upload_video()

    print(f"DONE. Video live at https://youtube.com/watch?v={video_id}")


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print("PIPELINE FAILED:")
        traceback.print_exc()
        raise
