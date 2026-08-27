# CreatorJoy

Turn any long video into ready-to-post TikTok highlights. CreatorJoy automatically cuts a video into short clips, scores each on "highlight worthiness" with an LLM, and assembles the top moments into a shareable reel.

Built for TikTok TechJam 2026 — "Build with joy, code for change."

## How it works
1. **Slice** — ffmpeg splits the input into 8-second overlapping clips.
2. **Score** — each clip is scored 0-10 by an LLM on motion, novelty, emotion, and whether a creator would post it.
3. **Assemble** — top-scoring clips are concatenated into one highlight reel.

## Run
```bash
export CJ_LLM_BASE="http://45.85.250.43:8080/v1"
export CJ_LLM_MODEL="qwen"
python3 creatorjoy.py input.mp4 output_dir
```
Output: `output_dir/highlight_reel.mp4` plus a JSON of ranked clips.

## LLM backend
CreatorJoy scores clips with our own self-hosted **Qwen** (OSS), served as an OpenAI-compatible API. No cloud, no external API keys. See `.env.example`.

## Batch over a folder
```bash
python3 run_corpus.py
```

## Files
- `extract_samples.py` — ffmpeg clip slicing
- `score_clip.py` — LLM highlight scoring (self-hosted OSS Qwen)
- `creatorjoy.py` — orchestration + reel assembly
- `run_corpus.py` — batch runner

## Why it matters
Creators waste hours finding the good moments in long streams. CreatorJoy gives them the reel in one command. It is practical, works on real video today, and is built to scale.
