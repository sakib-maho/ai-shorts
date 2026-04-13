# Bangla AI Shorts Generator

Automatically generate Bangla-language YouTube Shorts / Facebook Reels / TikTok videos from a single topic prompt.

**Pipeline:** GPT-4o script → DALL-E 3 images → gTTS Bangla voiceover → FFmpeg (Ken Burns + music) → 1080×1920 MP4

---

## How it works

1. **Script** — GPT-4o writes a 6–8 scene story in Bangla (narration) with English image prompts
2. **Images** — DALL-E 3 generates one cinematic 9:16 image per scene
3. **Voiceover** — gTTS converts Bangla narration to speech (no extra API key needed)
4. **Video clips** — FFmpeg applies a Ken Burns zoom effect and fades on each image+audio pair
5. **Music** — A random royalty-free track from `music/` is mixed at 18% volume under the voice
6. **Output** — A single `title_id_short.mp4` ready to upload

---

## Requirements

- Python 3.9+
- FFmpeg (must be in PATH)
- An OpenAI API key (GPT-4o + DALL-E 3)

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/sakib-maho/ai-shorts.git
cd ai-shorts

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your OpenAI API key
echo "OPENAI_API_KEY=sk-..." > .env

# 4. Download free background music (optional)
python download_music.py
```

---

## Usage

```bash
python generate_short.py "কৃত্রিম বুদ্ধিমত্তার ভবিষ্যৎ"
python generate_short.py "why the universe is expanding"
python generate_short.py "5 facts about the Titanic"
```

The output file is saved in the current directory as `title_sessionid_short.mp4`.

---

## Background music

Run `python download_music.py` once to download 4 free royalty-free tracks (lofi, cinematic, upbeat, dramatic) from Pixabay into the `music/` folder. `generate_short.py` picks one at random each run.

You can also drop your own `.mp3` / `.wav` / `.m4a` files into `music/` — they will be picked up automatically.

---

## Output specs

| Property | Value |
|---|---|
| Resolution | 1080 × 1920 (9:16 vertical) |
| Frame rate | 30 fps |
| Video codec | H.264 |
| Audio codec | AAC 192k, 44100 Hz stereo |
| Duration | ~30–45 seconds |

---

## Cost estimate (OpenAI)

| Step | Model | Approx. cost per video |
|---|---|---|
| Script | GPT-4o | ~$0.01 |
| Images (7 scenes) | DALL-E 3 standard | ~$0.28 |
| Voiceover | gTTS (free) | $0.00 |
| **Total** | | **~$0.30** |

---

## License

MIT — see [LICENSE](LICENSE)
