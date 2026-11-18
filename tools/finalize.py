"""Gabung video + muzik + SFX (+ VO) menjadi MP4 akhir.

  python3 tools/finalize.py projects/durian preview
      -> output/<nama>_preview.mp4  (tiada VO; muzik lebih kuat, sesuai juga sebagai teleprompter)

  python3 tools/finalize.py projects/durian final projects/durian/vo/rakaman.m4a
      -> output/<nama>_final.mp4
      1. bersihkan VO (high-pass, buang hingar, kompres, normalkan)
      2. cari setiap ayat dalam rakaman (Whisper) & letak tepat pada bar ayat itu
      3. duck muzik bila suara masuk, mix dengan SFX, loudness -14 LUFS (standard IG/TikTok)
"""
import json
import re
import subprocess
import sys
import wave
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np

SR = 44100


def run(cmd):
    subprocess.run(cmd, check=True)


def read_wav(p):
    with wave.open(str(p)) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return a.reshape(-1, w.getnchannels()).mean(1), w.getframerate()


def write_wav(p, a, sr=SR):
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype("<i2").tobytes())


def norm_words(s):
    s = s.lower().replace("*", "").replace("|", " ")
    return [w for w in re.sub(r"[^a-z0-9\s]", " ", s).split() if w]


def clean_vo(src, dst):
    af = ("highpass=f=80,lowpass=f=14000,afftdn=nf=-25,"
          "acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=3,"
          "equalizer=f=3500:t=q:w=1.2:g=2,loudnorm=I=-16:TP=-1.5:LRA=7")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-ac", "1", "-ar", str(SR), "-af", af, str(dst)])


def align(proj, tl, vo_clean, out_wav):
    """Cari permulaan/akhir setiap ayat dalam rakaman, letak pada bar yang betul."""
    from faster_whisper import WhisperModel
    audio, sr = read_wav(vo_clean)
    a16 = audio[:: sr // 16000] if sr % 16000 == 0 else np.interp(np.arange(0, len(audio), sr / 16000), np.arange(len(audio)), audio)
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(a16.astype(np.float32), language="ms", word_timestamps=True)
    words = [(w.word, w.start, w.end) for s in segs for w in s.words]
    hyp = [norm_words(w[0])[0] if norm_words(w[0]) else "" for w in words]

    beat = 60 / tl["bpm"]
    total = tl["totalBeats"] * beat + tl["tailSeconds"]
    out = np.zeros(int(total * sr) + sr)
    cursor = 0
    report = []
    for i, ln in enumerate(tl["lines"]):
        ref = norm_words(ln["text"])
        # cari padanan terbaik bermula dari cursor
        best = (0, cursor, cursor + len(ref))
        for st in range(cursor, min(len(hyp), cursor + 40)):
            for ln_ in range(max(1, len(ref) - 3), len(ref) + 4):
                sc = SequenceMatcher(None, ref, hyp[st:st + ln_]).ratio()
                if sc > best[0]:
                    best = (sc, st, st + ln_)
        sc, st, en = best
        if sc < 0.4 or st >= len(words):
            report.append(f"ayat {i+1}: TIDAK DIJUMPAI (skor {sc:.2f})")
            continue
        t0 = max(0, words[st][1] - 0.08)
        t1 = words[min(en, len(words)) - 1][2] + 0.15
        seg = audio[int(t0 * sr): int(t1 * sr)].copy()
        f = int(0.01 * sr); seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
        slot = ln["bars"] * tl["beatsPerBar"] * beat
        place = ln["bar"] * tl["beatsPerBar"] * beat + 0.05
        if len(seg) / sr > slot - 0.1:
            report.append(f"ayat {i+1}: {len(seg)/sr:.2f}s > slot {slot:.2f}s (bertindih sedikit)")
        a = int(place * sr)
        out[a:a + len(seg)] += seg[: len(out) - a]
        cursor = en
        report.append(f"ayat {i+1}: skor {sc:.2f}, {t0:.2f}-{t1:.2f}s -> {place:.2f}s")
    write_wav(out_wav, out[: int(total * sr)], sr)
    return report


def main():
    proj = Path(sys.argv[1]); mode = sys.argv[2] if len(sys.argv) > 2 else "preview"
    tl = json.loads((proj / "timeline.json").read_text())
    b = proj / "build"; name = proj.name
    outdir = Path("output"); outdir.mkdir(exist_ok=True)
    video, music, sfx = b / "video.mp4", b / "music.wav", b / "sfx.wav"
    if mode == "preview":
        out = outdir / f"{name}_preview.mp4"
        fc = ("[1:a]volume=0.9[m];[2:a]volume=0.75[s];[m][s]amix=inputs=2:normalize=0,"
              "loudnorm=I=-16:TP=-1.5:LRA=11[a]")
        run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(music), "-i", str(sfx),
             "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-shortest", str(out)])
        print(out)
        return
    vo_src = Path(sys.argv[3])
    vo_clean = b / "vo_clean.wav"; vo_aligned = b / "vo_aligned.wav"
    clean_vo(vo_src, vo_clean)
    for r in align(proj, tl, vo_clean, vo_aligned):
        print(r)
    out = outdir / f"{name}_final.mp4"
    fc = ("[3:a]asplit=2[vo][key];"
          "[1:a]volume=0.32[m0];[m0][key]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[m];"
          "[2:a]volume=0.45[s];"
          "[vo][m][s]amix=inputs=3:normalize=0,alimiter=limit=0.9,loudnorm=I=-14:TP=-1:LRA=9[a]")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(music), "-i", str(sfx), "-i", str(vo_aligned),
         "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", str(out)])
    print(out)


if __name__ == "__main__":
    main()
