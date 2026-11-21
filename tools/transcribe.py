"""Transcribe assets/voiceover.m4a with word timestamps -> video/transcript.json."""
import json, os, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model = WhisperModel(sys.argv[1] if len(sys.argv) > 1 else "medium", device="cpu", compute_type="int8")
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(ROOT, "assets", "voiceover.m4a"), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0
segs, info = model.transcribe(audio, language="ms",
                              word_timestamps=True, vad_filter=False, beam_size=5)
out = []
for s in segs:
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}", flush=True)
    out.append({"start": s.start, "end": s.end, "text": s.text.strip(),
                "words": [{"w": w.word.strip(), "t0": w.start, "t1": w.end} for w in s.words]})
json.dump(out, open(os.path.join(ROOT, "video", "transcript.json"), "w"), indent=1, ensure_ascii=False)
