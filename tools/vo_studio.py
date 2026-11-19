"""Sunting + proses VO jadi bunyi 'studio', dan selaraskan setiap ayat dengan ketukan.

  python3 tools/vo_studio.py projects/alphard

Input : <proj>/vo/edit.json (+ fail rakaman), <proj>/timeline.json (bpm, teks ayat)
Output: <proj>/vo/vo_edit.wav    (disunting, mentah)
        <proj>/vo/vo_studio.wav  (disunting + rantaian studio)  <- digunakan dalam video
        <proj>/vo_timing.json    (masa setiap ayat & perkataan dalam output)
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 48000


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def write(path, a):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-c:a", "pcm_s24le", str(path)], input=a.astype(np.float32).tobytes(), check=True)


def xfade_concat(pieces, fade=0.012):
    """Sambung kepingan dengan crossfade equal-power."""
    n = int(fade * SR)
    out = pieces[0].copy()
    for p in pieces[1:]:
        if len(out) < n or len(p) < n:
            out = np.concatenate([out, p]); continue
        t = np.linspace(0, np.pi / 2, n)
        mixed = out[-n:] * np.cos(t) + p[:n] * np.sin(t)
        out = np.concatenate([out[:-n], mixed, p[n:]])
    return out


def build_line(a, s, e, gaps, pre=0.05, post=0.10):
    """Potong satu ayat dari rakaman, pendekkan jeda dalam ayat."""
    pieces, cur = [], max(0.0, s - pre)
    for g0, g1, tgt, *_ in gaps:
        if not (s < g0 < e):
            continue
        keep_a = g0 + tgt * 0.45
        keep_b = g1 - tgt * 0.55
        pieces.append(a[int(cur * SR): int(keep_a * SR)])
        cur = keep_b
    pieces.append(a[int(cur * SR): int((e + post) * SR)])
    seg = xfade_concat(pieces)
    f = int(0.008 * SR)
    seg[:f] *= np.linspace(0, 1, f)
    seg[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR))
    return seg


STUDIO = ",".join([
    "highpass=f=75:poles=2",
    "afftdn=nr=10:nf=-62:tn=1",                      # buang hingar halus
    "agate=threshold=0.008:ratio=2.5:range=0.2:attack=4:release=140",  # kurangkan nafas & bunyi bilik
    "equalizer=f=120:t=q:w=0.9:g=1.5",               # kehangatan (proximity mic kondenser)
    "equalizer=f=320:t=q:w=1.2:g=-3.5",              # buang 'boxy' bilik
    "equalizer=f=900:t=q:w=1.5:g=-1",
    "equalizer=f=4200:t=q:w=1.0:g=2.5",              # kejelasan / presence
    "treble=g=3.5:f=11000:t=s",                      # 'air' mic mahal
    "deesser=i=0.35:m=0.5:f=0.5",
    "acompressor=threshold=-24dB:ratio=2.6:attack=8:release=120:knee=5:makeup=4",
    "acompressor=threshold=-10dB:ratio=4:attack=2:release=60:makeup=1",  # tangkap puncak
    "alimiter=limit=0.89:attack=3:release=50",
    "loudnorm=I=-16:TP=-1.5:LRA=7",
])


def words_for_lines(vo_path, lines_out, texts):
    from faster_whisper import WhisperModel
    a = decode(vo_path)
    a16 = a[::3]  # 48k -> 16k
    m = WhisperModel("small", device="cpu", compute_type="int8")
    res = []
    for (t0, t1), txt in zip(lines_out, texts):
        seg = a16[int(max(0, t0 - 0.05) * 16000): int((t1 + 0.1) * 16000)]
        seg = np.concatenate([np.zeros(3200, np.float32), seg, np.zeros(3200, np.float32)])
        prompt = txt.replace("*", "").replace("|", "")
        segs, _ = m.transcribe(seg, language="ms", word_timestamps=True, condition_on_previous_text=False,
                               initial_prompt=prompt, no_speech_threshold=0.99, log_prob_threshold=-5)
        ws = [{"w": w.word.strip(), "t": round(max(0, t0 - 0.05) - 0.2 + w.start, 3), "e": round(max(0, t0 - 0.05) - 0.2 + w.end, 3)}
              for s in segs for w in s.words]
        res.append(ws)
    return res


def main():
    proj = Path(sys.argv[1])
    ed = json.loads((proj / "vo" / "edit.json").read_text())
    tl = json.loads((proj / "timeline.json").read_text())
    beat = 60 / tl["bpm"]
    a = decode(proj / "vo" / ed["source"])

    segs = [build_line(a, s, e, ed["innerGaps"]) for s, e in zip(ed["lineStarts"], ed["lineEnds"])]
    gmin, gmax = ed["lineGapRange"]
    pre = 0.05
    starts, t_end = [], 0.0
    for i, sg in enumerate(segs):
        if i == 0:
            st = 0.0
        else:
            grid = beat if i in ed["fullBeatLines"] else beat / 2
            k = int(np.ceil((t_end + gmin) / grid))
            st = k * grid
        starts.append(st)
        t_end = st + len(sg) / SR - pre - 0.10
    total = starts[-1] + len(segs[-1]) / SR + 0.2
    out = np.zeros(int(total * SR) + SR)
    lines_out = []
    for st, sg in zip(starts, segs):
        i0 = int(max(0, st - pre) * SR)
        out[i0:i0 + len(sg)] += sg
        lines_out.append((round(st, 3), round(st + len(sg) / SR - pre - 0.10, 3)))
    out = out[: int(total * SR)]
    vo_dir = proj / "vo"
    write(vo_dir / "vo_edit.wav", out)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vo_dir / "vo_edit.wav"), "-af", STUDIO,
                    "-ar", str(SR), "-c:a", "pcm_s24le", str(vo_dir / "vo_studio.wav")], check=True)

    texts = [ln["text"] for ln in tl["lines"]]
    words = words_for_lines(vo_dir / "vo_studio.wav", lines_out, texts)
    timing = {"bpm": tl["bpm"], "duration": round(total, 3), "lines": []}
    for i, ((t0, t1), ws) in enumerate(zip(lines_out, words)):
        timing["lines"].append({"start": t0, "end": t1, "startBeat": round(t0 / beat, 3), "endBeat": round(t1 / beat, 3), "words": ws})
    (proj / "vo_timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=1))
    raw_dur = len(a) / SR
    print(f"asal {raw_dur:.2f}s -> disunting {total:.2f}s (jimat {raw_dur - total:.2f}s)")
    for i, l in enumerate(timing["lines"]):
        print(f"ayat {i+1:2d}: {l['start']:6.2f}-{l['end']:6.2f}s  beat {l['startBeat']:6.2f}  | " + " ".join(w["w"] for w in l["words"]))


if __name__ == "__main__":
    main()
