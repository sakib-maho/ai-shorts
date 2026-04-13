# AI Shorts Generator

<!-- BrandCloud:readme-standard -->
[![Maintained](https://img.shields.io/badge/Maintained-yes-brightgreen.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Showcase](https://img.shields.io/badge/Portfolio-Showcase-blue.svg)](#)

_Part of the `sakib-maho` project showcase series with consistent documentation and quality standards._

Generate short-form vertical videos from a single topic prompt using AI-generated scripts, images, and voiceover.

This repository is focused on fast production of social-ready videos for YouTube Shorts, TikTok, and Facebook Reels.

## Features

- Prompt-to-video workflow from one command
- Bangla narration support with text-to-speech
- AI image generation for scene-based storytelling
- FFmpeg-based rendering with smooth zoom and transitions
- Optional background music mixing for final export
- 1080x1920 vertical MP4 output

## Pipeline Overview

1. Topic prompt input
2. Script generation (scene-based narration + visual prompts)
3. Scene image generation
4. Voiceover generation
5. Video assembly with FFmpeg
6. Final social-ready export

## Requirements

- Python 3.9+
- FFmpeg available in `PATH`
- OpenAI API key for script and image generation

## Quick Start

```bash
git clone https://github.com/sakib-maho/ai-shorts.git
cd ai-shorts
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo "OPENAI_API_KEY=your_key_here" > .env
```

Optional: download free background tracks.

```bash
python download_music.py
```

## Usage

```bash
python generate_short.py "কৃত্রিম বুদ্ধিমত্তার ভবিষ্যৎ"
python generate_short.py "why the universe is expanding"
python generate_short.py "5 facts about the Titanic"
```

Output is written as `*_short.mp4` in the project directory.

## Output Specs

| Property | Value |
| --- | --- |
| Resolution | 1080 x 1920 |
| Aspect ratio | 9:16 |
| Frame rate | 30 fps |
| Video codec | H.264 |
| Audio codec | AAC |
| Typical duration | 30-45 seconds |

## Project Files

- `generate_short.py` - Main pipeline entrypoint
- `download_music.py` - Optional royalty-free music fetcher
- `requirements.txt` - Python dependencies

## Notes

- Keep `.env` local and never commit API keys.
- You can place your own music files in `music/` (`.mp3`, `.wav`, `.m4a`).
- Cost per generated video depends on model usage and number of scenes.

## License

MIT. See [LICENSE](LICENSE).
