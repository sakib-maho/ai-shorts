#!/usr/bin/env python3
"""
AI Animated YouTube Shorts Generator
Pipeline: GPT-4o script → DALL-E 3 images → gTTS (Bangla) → FFmpeg video
Usage: python generate_short.py "your topic here"
"""

import os
import sys
import json
import uuid
import shutil
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from gtts import gTTS

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API")
if not API_KEY:
    print("ERROR: OPENAI_API_KEY not found in .env file")
    sys.exit(1)

client = OpenAI(api_key=API_KEY)
SESSION_ID = uuid.uuid4().hex[:8]
TEMP_DIR = Path(f"temp_{SESSION_ID}")


# ──────────────────────────────────────────────
# STEP 1 — Generate script with GPT-4o
# ──────────────────────────────────────────────
def generate_script(topic: str) -> dict:
    print(f"\n[1/5] Generating script for: \"{topic}\"")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a viral YouTube Shorts scriptwriter. "
                    "Return ONLY valid JSON, no markdown, no explanation.\n"
                    "Structure:\n"
                    "{\n"
                    '  "title": "short catchy title in Bangla",\n'
                    '  "scenes": [\n'
                    "    {\n"
                    '      "narration": "MUST be in Bangla (Bengali script). One sentence of a continuous story.",\n'
                    '      "image_prompt": "detailed cinematic DALL-E 3 prompt in English, '
                    'vibrant colors, dramatic lighting, photorealistic or digital art style, '
                    'no text, no words, no letters in the image",\n'
                    '      "duration": 4\n'
                    "    }\n"
                    "  ]\n"
                    "}\n"
                    "Rules:\n"
                    "- 6 to 8 scenes\n"
                    "- Each scene narration continues from the previous — ONE flowing story about the topic\n"
                    "- Scene 1: hook the viewer with a bold opening statement\n"
                    "- Scenes 2-6: build the story, explain, go deeper into the topic\n"
                    "- Last scene: strong conclusion or call to action\n"
                    "- Each narration: 10-15 words in Bangla — natural spoken sentences\n"
                    "- Each image should visually match that part of the story\n"
                    "- Total: 30-45 seconds\n"
                    "- narration MUST be written in Bangla (Bengali) language\n"
                    "- image_prompt must always be in English\n"
                    "- NEVER include text/letters in image_prompt"
                )
            },
            {
                "role": "user",
                "content": (
                    f"Create a YouTube Short that tells a complete, engaging story about: {topic}\n"
                    f"Do NOT make a list of facts. Tell it as one continuous narrative from start to finish."
                )
            }
        ],
        response_format={"type": "json_object"}
    )

    script = json.loads(response.choices[0].message.content)
    total = sum(s.get("duration", 4) for s in script["scenes"])
    print(f"   Title   : {script['title']}")
    print(f"   Scenes  : {len(script['scenes'])}")
    print(f"   Duration: ~{total}s")
    return script


# ──────────────────────────────────────────────
# STEP 2 — Generate images with DALL-E 3
# ──────────────────────────────────────────────
def generate_images(scenes: list) -> list:
    print(f"\n[2/5] Generating {len(scenes)} images with DALL-E 3...")
    image_paths = []

    for i, scene in enumerate(scenes):
        prompt = scene["image_prompt"]
        print(f"   [{i+1}/{len(scenes)}] {prompt[:70]}...")

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt + (
                " Vertical portrait orientation, suitable for mobile screens. "
                "No text, no words, no captions, no letters anywhere in the image."
            ),
            size="1024x1792",   # native 9:16 vertical
            quality="standard",
            n=1
        )

        img_url = response.data[0].url
        img_data = requests.get(img_url, timeout=30).content

        img_path = TEMP_DIR / f"scene_{i:02d}.png"
        img_path.write_bytes(img_data)
        print(f"   Saved → {img_path.name}")
        image_paths.append(img_path)

    return image_paths


# ──────────────────────────────────────────────
# STEP 3 — Generate voiceover with gTTS (Bangla)
# ──────────────────────────────────────────────
def generate_audio(scenes: list) -> list:
    print(f"\n[3/5] Generating Bangla voiceover with gTTS...")
    audio_paths = []

    for i, scene in enumerate(scenes):
        narration = scene["narration"]
        print(f"   [{i+1}/{len(scenes)}] \"{narration}\"")

        # Generate Bangla TTS using gTTS (free, no API key needed)
        raw_path = TEMP_DIR / f"audio_{i:02d}_raw.mp3"
        tts = gTTS(text=narration, lang="bn", slow=False)
        tts.save(str(raw_path))

        # Re-encode to 44100 Hz stereo WAV for universal compatibility
        audio_path = TEMP_DIR / f"audio_{i:02d}.wav"
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(raw_path),
                "-ar", "44100", "-ac", "2",
                "-af", "volume=2.5",
                str(audio_path)
            ],
            check=True, capture_output=True
        )
        audio_paths.append(audio_path)

    return audio_paths


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def get_audio_duration(audio_path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path)
        ],
        capture_output=True, text=True, check=True
    )
    return float(result.stdout.strip())


def make_clip(img_path: Path, audio_path: Path, index: int, duration: float) -> Path:
    """Create a single video clip: image + Ken Burns zoom + audio."""
    clip_path = TEMP_DIR / f"clip_{index:02d}.mp4"

    # Ken Burns zoom-in effect — slow, cinematic pan
    frames = int(duration * 30)
    zoom_filter = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,"
        f"zoompan="
        f"z='min(zoom+0.0008,1.15)':"
        f"x='iw/2-(iw/zoom/2)':"
        f"y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s=1080x1920:fps=30,"
        f"fade=t=in:st=0:d=0.4,"
        f"fade=t=out:st={duration-0.4:.2f}:d=0.4"
        f"[v]"
    )

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(img_path),
            "-i", str(audio_path),
            "-filter_complex", zoom_filter,
            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "128k",
            "-t", str(duration),
            "-r", "30",
            "-shortest",
            str(clip_path)
        ],
        check=True,
        capture_output=True
    )
    return clip_path


# ──────────────────────────────────────────────
# STEP 4 — Build each clip
# ──────────────────────────────────────────────
def build_clips(image_paths: list, audio_paths: list, scenes: list) -> list:
    print(f"\n[4/5] Building video clips with Ken Burns animation...")
    clip_paths = []

    for i, (img, audio, scene) in enumerate(zip(image_paths, audio_paths, scenes)):
        # Use actual TTS duration (more accurate than script estimate)
        audio_dur = get_audio_duration(audio) + 0.5   # 0.5s buffer
        print(f"   Clip {i+1}/{len(scenes)}: {audio_dur:.1f}s")
        clip = make_clip(img, audio, i, audio_dur)
        clip_paths.append(clip)

    return clip_paths


# ──────────────────────────────────────────────
# STEP 5 — Concatenate all clips
# ──────────────────────────────────────────────
def concat_clips(clip_paths: list, title: str) -> Path:
    print(f"\n[5/5] Merging all clips into final Short...")

    concat_file = TEMP_DIR / "concat.txt"
    lines = [f"file '{p.resolve()}'" for p in clip_paths]
    concat_file.write_text("\n".join(lines))

    slug = "".join(c if c.isalnum() or c == "_" else "_" for c in title.replace(" ", "_"))[:40]
    merged_path = TEMP_DIR / f"merged_{SESSION_ID}.mp4"

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "44100",
            "-ac", "2",
            "-af", "aresample=async=1",
            "-movflags", "+faststart",
            str(merged_path)
        ],
        check=True,
        capture_output=True
    )

    return merged_path


# ──────────────────────────────────────────────
# STEP 6 — Mix background music
# ──────────────────────────────────────────────
def mix_background_music(video_path: Path, title: str) -> Path:
    music_dir = Path("music")
    music_files = list(music_dir.glob("*.mp3")) + list(music_dir.glob("*.wav")) + list(music_dir.glob("*.m4a"))

    slug = "".join(c if c.isalnum() or c == "_" else "_" for c in title.replace(" ", "_"))[:40]
    output_path = Path(f"{slug}_{SESSION_ID}_short.mp4")

    if not music_files:
        print(f"\n[6/6] No music found in music/ folder — skipping.")
        video_path.rename(output_path)
        return output_path

    import random
    music_file = random.choice(music_files)
    print(f"\n[6/6] Mixing background music: {music_file.name}")

    video_dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
        capture_output=True, text=True, check=True
    ).stdout.strip())

    # Loop music to cover full video, fade out last 2s, mix at 18% under voice
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-stream_loop", "-1", "-i", str(music_file),
            "-filter_complex",
            (
                f"[1:a]volume=0.18,afade=t=out:st={video_dur-2:.2f}:d=2,"
                f"aresample=44100[music];"
                f"[0:a][music]amix=inputs=2:duration=first:dropout_transition=2[a]"
            ),
            "-map", "0:v",
            "-map", "[a]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", str(video_dur),
            "-movflags", "+faststart",
            str(output_path)
        ],
        check=True,
        capture_output=True
    )

    print(f"   Music mixed at 18% volume with 2s fade-out")
    return output_path


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print("Usage:   python generate_short.py \"your topic here\"")
        print("Example: python generate_short.py \"5 mind-blowing facts about black holes\"")
        print("Example: python generate_short.py \"why you should wake up at 5am\"")
        sys.exit(1)

    topic = " ".join(sys.argv[1:])
    TEMP_DIR.mkdir(exist_ok=True)

    try:
        script      = generate_script(topic)
        image_paths = generate_images(script["scenes"])
        audio_paths = generate_audio(script["scenes"])
        clip_paths  = build_clips(image_paths, audio_paths, script["scenes"])
        merged      = concat_clips(clip_paths, script["title"])
        output      = mix_background_music(merged, script["title"])

        total_dur = sum(get_audio_duration(a) + 0.5 for a in audio_paths)
        size_mb   = output.stat().st_size / (1024 * 1024)

        print(f"\n{'─'*50}")
        print(f"  Output : {output}")
        print(f"  Size   : {size_mb:.1f} MB")
        print(f"  Length : {total_dur:.1f}s")
        print(f"  Format : 1080x1920 (9:16 vertical)")
        print(f"{'─'*50}")
        print("  Done! Ready to upload to Facebook Reels / YouTube Shorts / TikTok")

    except subprocess.CalledProcessError as e:
        print(f"\nFFmpeg error:\n{e.stderr.decode()}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        raise
    finally:
        if TEMP_DIR.exists():
            shutil.rmtree(TEMP_DIR)
            print("  Temp files cleaned up.")


if __name__ == "__main__":
    main()
