"""Build build/timeline.json from the transcribed voiceover (video/transcript.json).

Whisper's words are corrected here (mishearings, onset times checked against
the audio envelope), styled for captions, and combined with the story events
(calls, tow trucks arriving / hitching / breaking down) that both the 3D scene
and the audio mix read. All story beats sit on the 110 BPM grid.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BPM = 110
BEAT = 60 / BPM
BARS = 19
DURATION = round(BARS * 4 * BEAT, 4)          # 41.4545 s

# --- caption words -------------------------------------------------------
raw = [w for s in json.load(open(os.path.join(ROOT, "video", "transcript.json"))) for w in s["words"]]
words = []
for w in raw:
    t = w["w"]
    if t == "perusak.":                         # "pun rosak." misheard
        words += [{"w": "pun", "t0": 29.42}, {"w": "rosak.", "t0": 29.62}]
    elif t == "tersahadai":
        words.append({"w": "tersadai", "t0": w["t0"]})
    elif t == "terbijalan.":                    # "tepi jalan." misheard
        words += [{"w": "tepi", "t0": 36.62}, {"w": "jalan.", "t0": 36.86}]
    else:
        words.append({"w": t, "t0": w["t0"]})

# Onsets corrected from the audio envelope.
fix = {0: 0.80}                                 # "Kalau"
for i, w in enumerate(words):
    if w["w"] == "Sekali":
        fix[i], fix[i + 1] = 28.10, 28.42
    if w["w"] == "Akhirnya":
        fix[i] = 34.60
for i, t in fix.items():
    words[i]["t0"] = t
for i, w in enumerate(words):
    w["t1"] = words[i + 1]["t0"] if i + 1 < len(words) else 39.15
    w["t1"] = min(w["t1"], w["t0"] + 0.7)

# Caption styling: red = breakdowns / failure, yellow = escalating numbers.
RED = {"rosak", "rosak.", "tak", "bergerak."}
YEL = {"pertama", "pertama.", "kedua", "kedua.", "ketiga", "ketiga.", "keempat", "keempat.", "kelima", "tersadai"}
for w in words:
    base = w["w"].lower()
    w["style"] = "red" if base in RED else "yel" if base in YEL else ""
i = next(i for i, w in enumerate(words) if w["w"] == "lori")   # first "lori towing" is the hook
words[i]["style"] = words[i + 1]["style"] = "yel"
words[next(i for i, w in enumerate(words) if w["w"] == "tak")]["style"] = "red"

# --- story events (seconds) ---------------------------------------------
def b(n):  # beat n -> seconds
    return round(n * BEAT, 4)

events = {
    "bpm": BPM, "beat": BEAT,
    # phone calls: tally increments, call card shows
    "calls": [3.42, 10.42, 16.84, 23.80, 30.42],
    # tow truck i reverses in [start, end]
    "arrive": [[b(9) + 0.05, b(11)], [b(22), b(24)], [b(33), b(35)], [b(46), b(48)], [b(58.5), b(61)]],
    "load": [b(11), b(12.75)],                  # car winched onto truck 1
    "hitch": [None, b(24.25), b(35.25), b(48.25), b(61.25)],
    # whole chain creeps forward [start, end, metres]
    "drive": [[b(13.5), b(16.5), 3.5], [b(26.5), b(29.8), 2.5], [b(37.25), b(40.4), 2.0],
              [b(51.5), b(54.1), 1.5], [b(62.5), b(64.1), 1.0]],
    # breakdown moments, on the spoken "rosak"
    "break": [9.02, 16.36, 22.08, 29.62, b(64.2)],
    "facepalm": 37.9,
}

# Shot cuts on the beat / half-beat grid.
cuts = [0, b(6), b(9), b(13), b(18), b(22), b(26), b(31), b(33), b(37), b(43), b(46),
        b(51), b(55), b(58.5), b(63), b(68), b(72)]
shots = ["establish", "call1", "load", "break1", "call2", "hitch2", "break2", "call3", "hitch3",
         "break3", "call4", "hitch4", "break4", "call5", "hitch5", "reveal", "still", "facepalm"]
assert len(cuts) == len(shots)
shot_list = [{"id": s, "start": c, "end": cuts[i + 1] if i + 1 < len(cuts) else DURATION}
             for i, (s, c) in enumerate(zip(shots, cuts))]

out = {"title": "Lori Towing", "fps": 30, "width": 1080, "height": 1920, "duration": DURATION,
       "words": words, "events": events, "shots": shot_list}
json.dump(out, open(os.path.join(ROOT, "build", "timeline.json"), "w"), indent=1, ensure_ascii=False)
print(f"timeline: {len(words)} words, {len(shot_list)} shots, {DURATION:.2f}s")
for s in shot_list:
    print(f"  {s['id']:10s} {s['start']:6.2f} -> {s['end']:6.2f}  ({s['end'] - s['start']:.2f}s)")
