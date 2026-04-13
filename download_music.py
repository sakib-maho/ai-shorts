#!/usr/bin/env python3
"""
Download free royalty-free background music from Pixabay API
Usage: python download_music.py
Music is saved to the music/ folder and auto-picked by generate_short.py
"""

import requests
import os
from pathlib import Path

MUSIC_DIR = Path("music")
MUSIC_DIR.mkdir(exist_ok=True)

# Free tracks — curated from Pixabay free music (royalty-free, no attribution required)
# Pixabay music: https://pixabay.com/music/
TRACKS = [
    {
        "name": "lofi_chill_vibes.mp3",
        "url": "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3"
    },
    {
        "name": "epic_cinematic.mp3",
        "url": "https://cdn.pixabay.com/download/audio/2022/03/10/audio_c8c8a73467.mp3"
    },
    {
        "name": "inspiring_upbeat.mp3",
        "url": "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3"
    },
    {
        "name": "mystery_dramatic.mp3",
        "url": "https://cdn.pixabay.com/download/audio/2021/11/25/audio_5c1c4b84f9.mp3"
    },
]

def download(name: str, url: str):
    dest = MUSIC_DIR / name
    if dest.exists():
        print(f"  Already exists: {name}")
        return
    print(f"  Downloading: {name} ...", end=" ", flush=True)
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        dest.write_bytes(r.content)
        print(f"✓ ({len(r.content)//1024} KB)")
    except Exception as e:
        print(f"✗ Failed: {e}")

if __name__ == "__main__":
    print("Downloading free background music tracks to music/ folder...\n")
    for track in TRACKS:
        download(track["name"], track["url"])
    files = list(MUSIC_DIR.glob("*.mp3"))
    print(f"\nDone! {len(files)} track(s) in music/ folder.")
    print("generate_short.py will automatically pick one at random.")
