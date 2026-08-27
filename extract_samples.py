#!/usr/bin/env python3
"""CreatorJoy - extract N-second sample clips from a video via ffmpeg."""
import subprocess, os, json, sys

def probe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
                         capture_output=True, text=True)
    return float(out.stdout.strip() or 0)

def extract_samples(video, out_dir, clip_len=8, overlap=2):
    os.makedirs(out_dir, exist_ok=True)
    dur = probe_duration(video)
    if dur <= 0:
        return []
    step = max(1, clip_len - overlap)
    clips = []
    start = 0.0
    idx = 0
    while start < dur - clip_len/2:
        seg = os.path.join(out_dir, f"clip_{idx:03d}.mp4")
        subprocess.run(["ffmpeg", "-y", "-ss", f"{start:.2f}", "-i", video,
                        "-t", str(clip_len), "-c:v", "libx264", "-crf", "23",
                        "-preset", "veryfast", "-c:a", "aac", "-movflags", "+faststart", seg],
                       capture_output=True)
        if os.path.exists(seg) and os.path.getsize(seg) > 2000:
            clips.append(seg)
        idx += 1
        start += step
    return clips

if __name__ == "__main__":
    video = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "samples"
    clips = extract_samples(video, out)
    print(json.dumps({"video": video, "clips": len(clips)}))
