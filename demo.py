#!/usr/bin/env python3
"""CreatorJoy demo runner for the TechJam submission video.

Runs CreatorJoy on one corpus video, prints the ranked highlights, and
confirms the reel exists. Used to record the 3-minute demo.
"""
import os, sys, json, subprocess
from creatorjoy import run

TOKEN = os.environ.get("NOUS_TOKEN", "")
CORPUS = "assets/corpus"

def main():
    vids = [v for v in sorted(os.listdir(CORPUS)) if v.endswith(".mp4")]
    if not vids:
        print("no corpus videos"); return
    vid = vids[0]
    path = os.path.join(CORPUS, vid)
    print(f"=== CreatorJoy demo on {vid} ===")
    res = run(path, TOKEN, "demo_run")
    print(f"Input: {vid}")
    print(f"Clips produced: {res['clip_count']}")
    print("Ranked highlights:")
    for h in res["highlights"]:
        print(f"  {h['clip']}: score {h['score']} — {h['reason']}")
    reel = res.get("reel")
    print(f"Reel: {reel} ({'OK' if reel and os.path.exists(reel) else 'MISSING'})")

if __name__ == "__main__":
    main()
