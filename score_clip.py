#!/usr/bin/env python3
"""CreatorJoy - score a clip's TikTok highlight worthiness via a local OSS LLM (Qwen).

Uses an OpenAI-compatible endpoint (our self-hosted Qwen). No cloud, no external API.
Configured via env:
  CJ_LLM_BASE  - base URL, default http://45.85.250.43:8080/v1
  CJ_LLM_MODEL - model name, default qwen (server picks)
"""
import subprocess, os, json, sys, re, requests

BASE = os.environ.get("CJ_LLM_BASE", "http://localhost:8080/v1")
MODEL = os.environ.get("CJ_LLM_MODEL", "/home/ojo/unmark-model/Qwen3.5-4B-Q4_K_M.gguf")
KEY = os.environ.get("CJ_LLM_KEY", "")

def clip_features(clip):
    """Extract real, measurable signal from the clip for the LLM to judge."""
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                         "-of", "default=noprint_wrappers=1:nokey=1", clip],
                        capture_output=True, text=True).stdout.strip()
    # scene cuts: count frames where scene-change score > 0.3 (dynamic = more action)
    cuts = subprocess.run(["ffmpeg", "-i", clip, "-vf", "select='gt(scene,0.3)',showinfo",
                         "-f", "null", "-"], stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT, text=True).stdout
    n_cuts = cuts.count("showinfo") if cuts else 0
    # audio loudness (mean volume in dB); None if no audio track
    vol = subprocess.run(["ffmpeg", "-i", clip, "-af", "volumedetect", "-f", "null", "-"],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True).stdout
    m = re.search(r"mean_volume:\s*([-\d.]+)\s*dB", vol)
    mean_vol = float(m.group(1)) if m else None
    return {"duration": dur, "scene_cuts": n_cuts, "mean_volume_db": mean_vol}

def score_clip(clip, base=None, model=None):
    base = base or BASE
    model = model or MODEL
    feat = clip_features(clip)
    prompt = (
        "Score this short video clip for TikTok 'highlight' worthiness: "
        "would a creator post this as a hook or shareable moment? "
        "Use the provided signal. Reward visible action (more scene cuts = more motion), "
        "clear audio presence (louder mean volume), and a punchy length. "
        "Penalize static/empty frames (0 cuts), near-silent audio, dead air.\n"
        f"Duration: {feat['duration']}s. Scene cuts (motion): {feat['scene_cuts']}. "
        f"Mean audio volume: {feat['mean_volume_db']} dB.\n"
        "Reply ONLY JSON: {\"score\": <0-10 int>, \"reason\": <one short phrase>}"
    )
    last_err = "parse_fail"
    headers = {"Content-Type": "application/json"}
    if KEY:
        headers["Authorization"] = f"Bearer {KEY}"
    for _ in range(3):
        try:
            r = requests.post(f"{base}/chat/completions", headers=headers,
                              json={"model": model,
                                    "messages": [{"role": "user", "content": prompt}],
                                    "max_tokens": 400, "temperature": 0.2,
                                    "chat_template_kwargs": {"enable_thinking": False}},
                              timeout=120)
            txt = r.json()["choices"][0]["message"].get("content", "") or ""
            m = re.search(r"\{.*\}", txt, re.DOTALL)
            if m:
                obj = json.loads(m.group(0))
                return float(obj.get("score", 0)), obj.get("reason", "")
        except Exception as e:
            last_err = f"err:{e}"
    return 0.0, last_err

if __name__ == "__main__":
    clip = sys.argv[1]
    s, reason = score_clip(clip)
    print(json.dumps({"clip": clip, "score": s, "reason": reason}))
