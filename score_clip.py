#!/usr/bin/env python3
"""CreatorJoy - score a clip's TikTok highlight worthiness via Nous LLM."""
import subprocess, os, json, sys, base64, requests

NOUS_URL = "https://inference-api.nousresearch.com/v1/chat/completions"

def clip_features(clip):
    """Extract lightweight features to describe the clip for the LLM."""
    # duration
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=noprint_wrappers=1:nokey=1", clip],
                         capture_output=True, text=True).stdout.strip()
    # avg motion via bitrate proxy (higher = more motion)
    br = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                         "-show_entries", "stream=bit_rate", "-of",
                         "default=noprint_wrappers=1:nokey=1", clip],
                        capture_output=True, text=True).stdout.strip()
    # thumbnail (middle frame)
    thumb = clip + ".jpg"
    subprocess.run(["ffmpeg", "-y", "-ss", "2", "-i", clip, "-frames:v", "1",
                    "-q:v", "3", thumb], capture_output=True)
    return {"duration": dur, "bitrate": br, "thumb": thumb if os.path.exists(thumb) else None}

def score_clip(clip, token):
    feat = clip_features(clip)
    prompt = (
        "You score short video clips for TikTok 'highlight' worthiness: "
        "would a creator post this as a hook or shareable moment? "
        "Reward: visible action, emotion, novelty, a clear subject, punchy moment. "
        "Penalize: static/empty frames, smooth talking-head with no visual change, dead air.\n"
        f"Clip duration: {feat['duration']}s. Perceived motion (bitrate): {feat['bitrate']}.\n"
        "Reply ONLY JSON: {\"score\": <0-10 int>, \"reason\": <one short phrase>}"
    )
    content = [{"type": "text", "text": prompt}]
    r = requests.post(NOUS_URL, headers={"Authorization": f"Bearer {token}"},
                      json={"model": "tencent/hy3:free", "messages": [
                          {"role": "user", "content": content}], "max_tokens": 400}, timeout=40)
    try:
        msg = r.json()["choices"][0]["message"]
        txt = msg.get("content") or msg.get("reasoning") or ""
        import re
        m = re.search(r"\{.*\}", txt, re.DOTALL)
        obj = json.loads(m.group(0)) if m else {}
        return float(obj.get("score", 0)), obj.get("reason", "")
    except Exception:
        return 0.0, "parse_fail"

if __name__ == "__main__":
    clip = sys.argv[1]
    token = os.environ.get("NOUS_TOKEN", "")
    s, reason = score_clip(clip, token)
    print(json.dumps({"clip": clip, "score": s, "reason": reason}))
