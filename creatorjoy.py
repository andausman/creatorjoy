#!/usr/bin/env python3
"""CreatorJoy - turn a video into ranked TikTok highlight clips + a reel."""
import os, sys, json, subprocess, tempfile, shutil
from extract_samples import extract_samples
from score_clip import score_clip

def assemble_reel(scored, out_reel, max_clips=5):
    """Concat top clips into one mp4 reel."""
    top = [c for c, s, r in scored if s >= 6][:max_clips]
    if not top:
        top = [c for c, s, r in sorted(scored, key=lambda x: -x[1])[:max_clips]]
    if not top:
        return None
    # concat via ffmpeg concat demuxer
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        for c in top:
            f.write(f"file '{os.path.abspath(c)}'\n")
        listf = f.name
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listf,
                    "-c", "copy", out_reel], capture_output=True)
    os.remove(listf)
    return out_reel if os.path.exists(out_reel) else None

def run(video, token, workdir=None):
    workdir = workdir or tempfile.mkdtemp()
    clips = extract_samples(video, os.path.join(workdir, "samples"))
    scored = []
    for c in clips:
        s, reason = score_clip(c, token)
        scored.append((c, s, reason))
    scored.sort(key=lambda x: -x[1])
    reel = assemble_reel(scored, os.path.join(workdir, "highlight_reel.mp4"))
    result = {
        "input": video,
        "clip_count": len(clips),
        "highlights": [{"clip": os.path.basename(c), "score": s, "reason": r}
                       for c, s, r in scored[:8]],
        "reel": reel,
    }
    # cleanup sample clips (keep reel)
    for c, _, _ in scored:
        try: os.remove(c)
        except OSError: pass
    return result

if __name__ == "__main__":
    video = sys.argv[1]
    token = os.environ.get("NOUS_TOKEN", "")
    out = sys.argv[2] if len(sys.argv) > 2 else "output"
    res = run(video, token, out)
    print(json.dumps(res, indent=2))
