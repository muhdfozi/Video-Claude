"""Tighten the voiceover: cut dead air, breaths and hesitations, land sentences on the beat.

Pauses are found from RMS energy (breaths sit above digital silence, so a plain
silence gate misses them). Then:
  * a pause inside a sentence (previous word has no . , ?) shrinks to 0.10 s
  * a pause between sentences/clauses shrinks to >= 0.12 s and the next phrase
    starts on the next half-beat of the 110 BPM grid
  * leading silence and the trailing tail are removed
Writes build/voice_edit.wav and build/vo_map.json ([src_start, src_end, dst_start]
per kept piece) so timeline.py can move every word time to the edited clock.
"""
import json, os, subprocess, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
HALF = 60 / 110 / 2                 # half-beat = 0.2727 s
THRESH_DB, MIN_PAUSE = -29.0, 0.22
PRE, POST = 0.04, 0.07              # keep a little air so consonants aren't clipped
MID_GAP, MIN_GAP = 0.10, 0.12
FADE = int(0.012 * SR)

pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(ROOT, "assets", "voiceover.m4a"),
                      "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
x = np.frombuffer(pcm, np.int16).astype(np.float64) / 32768

hop = int(0.01 * SR)
rms = np.array([np.sqrt(np.mean(x[i:i + 2 * hop] ** 2)) for i in range(0, len(x) - 2 * hop, hop)])
quiet = 20 * np.log10(rms + 1e-7) < THRESH_DB

# speech segments = complement of quiet runs >= MIN_PAUSE
pauses, i = [], 0
while i < len(quiet):
    if quiet[i]:
        j = i
        while j < len(quiet) and quiet[j]:
            j += 1
        if (j - i) * 0.01 >= MIN_PAUSE or i == 0 or j == len(quiet):
            pauses.append((i * 0.01, j * 0.01))
        i = j
    else:
        i += 1
total = len(x) / SR
speech, cur = [], 0.0
for a, b in pauses:
    if a > cur:
        speech.append([cur, a])
    cur = b
if cur < total:
    speech.append([cur, total])
speech = [[max(0, a - PRE), min(total, b + POST)] for a, b in speech if b - a > 0.08]

from vo_words import corrected_words
words = corrected_words()


def ends_clause(t):
    """Does the word before the one starting nearest t end with punctuation?"""
    idx = min(range(len(words)), key=lambda i: abs(words[i]["t0"] - t))
    return idx > 0 and words[idx - 1]["w"].rstrip()[-1:] in ".,?!"


pieces, out_t = [], 0.0
for k, (a, b) in enumerate(speech):
    if k == 0:
        start = 0.0
    else:
        prev_end = out_t
        if ends_clause(a + PRE):
            start = np.ceil((prev_end + MIN_GAP) / HALF) * HALF - PRE
            start = max(start, prev_end + MIN_GAP - PRE)
        else:
            start = prev_end + MID_GAP - PRE - POST + 0.06
            start = max(start, prev_end)
    pieces.append([a, b, float(start)])
    out_t = start + (b - a)

dur = out_t + 0.05
y = np.zeros(int(dur * SR) + 1)
for a, b, d in pieces:
    seg = x[int(a * SR):int(b * SR)].copy()
    n = min(FADE, len(seg) // 2)
    seg[:n] *= np.linspace(0, 1, n); seg[-n:] *= np.linspace(1, 0, n)
    i0 = int(d * SR)
    y[i0:i0 + len(seg)] += seg[: len(y) - i0]

os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
with wave.open(os.path.join(ROOT, "build", "voice_edit.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
json.dump(pieces, open(os.path.join(ROOT, "build", "vo_map.json"), "w"), indent=1)
print(f"voice edit: {total:.2f}s -> {dur:.2f}s  ({len(pieces)} pieces, cut {total - dur:.2f}s)")
for (a, b, d), nxt in zip(pieces, pieces[1:] + [None]):
    gap = (nxt[2] - (d + b - a)) if nxt else 0
    print(f"  src {a:6.2f}-{b:6.2f} -> dst {d:6.2f}   gap after {gap:.2f}s")
