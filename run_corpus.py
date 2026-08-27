#!/usr/bin/env python3
"""Run CreatorJoy over the whole corpus, emit a results.json + reels."""
import os, sys, json, subprocess
from creatorjoy import run

CORPUS = "assets/corpus"
OUT = "runs"
os.makedirs(OUT, exist_ok=True)

results = []
for vid in sorted(os.listdir(CORPUS)):
    if not vid.endswith(".mp4"):
        continue
    path = os.path.join(CORPUS, vid)
    work = os.path.join(OUT, vid.replace(".mp4", ""))
    os.makedirs(work, exist_ok=True)
    try:
        res = run(path, work)
        results.append(res)
        print(f"{vid}: {res['clip_count']} clips, reel={'yes' if res.get('reel') else 'no'}")
    except Exception as e:
        print(f"{vid}: ERROR {e}")

json.dump(results, open(os.path.join(OUT, "results.json"), "w"), indent=2)
print(f"done {len(results)} videos")
