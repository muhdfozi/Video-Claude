"""Build build/timeline.json on the EDITED voiceover clock.

Word times come from vo_words.py (original clock) and are moved through
build/vo_map.json (written by vo_edit.py). Every shot cut and story event is
then derived from anchor words and snapped to the 110 BPM grid, so re-editing
the voice never needs hand-typed times.
"""
import json, math, os, re
from vo_words import corrected_words

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BPM = 110
BEAT = 60 / BPM
HALF = BEAT / 2

pieces = json.load(open(os.path.join(ROOT, "build", "vo_map.json")))


def remap(t):
    """Original-recording time -> edited time."""
    for a, b, d in pieces:
        if t < a:
            return d                       # inside a removed pause: snap to the next piece
        if t <= b:
            return d + (t - a)
    a, b, d = pieces[-1]
    return d + (b - a)


words = corrected_words()
for w in words:
    w["t0"], w["t1"] = round(remap(w["t0"]), 3), round(remap(w["t1"]), 3)
    w["t1"] = max(w["t1"], w["t0"] + 0.12)

# Caption styling: red = breakdowns / failure, yellow = escalating numbers.
RED = {"rosak", "tak", "bergerak"}
YEL = {"pertama", "kedua", "ketiga", "keempat", "kelima", "tersadai"}
norm = lambda s: re.sub(r"[^a-z]", "", s.lower())
for w in words:
    n = norm(w["w"])
    w["style"] = "red" if n in RED else "yel" if n in YEL else ""
i = next(i for i, w in enumerate(words) if norm(w["w"]) == "lori")   # first "lori towing" is the hook
words[i]["style"] = words[i + 1]["style"] = "yel"


def find(seq, nth=0):
    """Index of the first word of the nth occurrence of a word sequence."""
    seq = [norm(s) for s in seq]
    hits = [i for i in range(len(words) - len(seq) + 1) if [norm(w["w"]) for w in words[i:i + len(seq)]] == seq]
    return hits[nth]


def at(seq, nth=0):
    return words[find(seq, nth)]["t0"]


def snap_down(t, grid=HALF):
    return round(math.floor((t + 1e-6) / grid) * grid, 4)


def snap_up(t, grid=HALF):
    return round(math.ceil((t - 1e-6) / grid) * grid, 4)


# --- shot cuts: just before each anchor phrase, floored to the half-beat --------
anchors = [
    ("establish", 0.0),
    ("call1", at(["kau", "panggil"])),
    ("load", at(["untuk", "angkut"])),
    ("break1", at(["tapi", "lori", "towing", "pertama"])),
    ("call2", at(["jadi", "kau", "panggil"], 0)),
    ("hitch2", at(["untuk", "towing", "lori", "towing", "pertama"])),
    ("break2", at(["lepas", "tu"])),
    ("call3", at(["kau", "panggil", "lori", "towing", "ketiga"])),
    ("hitch3", at(["untuk", "towing", "lori", "towing", "kedua"])),
    ("break3", at(["tapi", "lori", "towing", "ketiga"])),
    ("call4", at(["panggil", "lori", "towing", "keempat"])),
    ("hitch4", at(["untuk", "towing", "lori", "towing", "ketiga"])),
    ("break4", at(["sekali"])),
    ("call5", at(["jadi", "kau", "panggil"], 1)),
    ("hitch5", at(["untuk", "towing", "lori", "towing", "keempat"])),
    ("reveal", at(["akhirnya"])),
    ("still", at(["kereta", "kau", "pula"])),
    ("facepalm", words[-1]["t1"] + 0.15),
]
cuts = [0.0] + [snap_down(t - 0.06) for _, t in anchors[1:]]
cuts[-1] = snap_up(anchors[-1][1])
DURATION = round(snap_up(cuts[-1] + 2.55, BEAT), 4)       # room for the sad-trombone tag
shots = [{"id": n, "start": c, "end": cuts[i + 1] if i + 1 < len(cuts) else DURATION}
         for i, ((n, _), c) in enumerate(zip(anchors, cuts))]
S = {s["id"]: s for s in shots}

# --- story events -----------------------------------------------------------------
calls = [at(["panggil"], k) for k in range(5)]
breaks = [at(["rosak"], k) for k in (1, 2, 3, 4)]          # rosak #0 is the car in line 1
# Each truck backs in, then winches the whole stack (car, or the previous truck with
# everything on it) up its tilted bed: truck i carries item i.
arrive, loads, drive = [], [], []
for i, shot in enumerate(["load", "hitch2", "hitch3", "hitch4", "hitch5"]):
    s = S[shot]
    a0 = s["start"] + 0.03
    a1 = a0 + min(2 * BEAT, (s["end"] - s["start"]) * 0.5)
    arrive.append([round(a0, 3), round(a1, 3)])
    loads.append([round(a1 + 0.02, 3), round(min(a1 + 1.7 * BEAT, s["end"] - 0.06), 3)])
# the stack creeps forward during each breakdown shot, stalling right on "rosak"
for i, shot in enumerate(["break1", "break2", "break3", "break4"]):
    s = S[shot]
    drive.append([round(s["start"] + 0.12, 3), round(breaks[i] - 0.04, 3), [3.5, 3.0, 2.5, 2.0][i]])
# truck 5 tries once the tower is complete and dies on "semua"
breaks.append(at(["semua"]))
drive.append([round(S["reveal"]["start"] + 0.05, 3), round(breaks[-1] - 0.04, 3), 1.5])

events = {
    "bpm": BPM, "beat": BEAT,
    "calls": calls, "arrive": arrive, "loads": loads, "drive": drive, "break": breaks,
    "gag": at(["masih"]),               # "BENGKEL masih 42 km" + the band stops
    "facepalm": S["facepalm"]["start"],
    "reveal": S["reveal"]["start"],
}

out = {"title": "Lori Towing", "fps": 30, "width": 1080, "height": 1920, "duration": DURATION,
       "words": words, "events": events, "shots": shots}
json.dump(out, open(os.path.join(ROOT, "build", "timeline.json"), "w"), indent=1, ensure_ascii=False)
print(f"timeline: {len(words)} words, {len(shots)} shots, {DURATION:.2f}s ({DURATION / BEAT / 4:.2f} bars)")
for s in shots:
    print(f"  {s['id']:10s} {s['start']:6.2f} -> {s['end']:6.2f}  ({s['end'] - s['start']:.2f}s)")
print("calls", [round(c, 2) for c in calls]); print("breaks", [round(b, 2) for b in breaks])
assert all(s["end"] - s["start"] > 0.7 for s in shots), "a shot is too short"
assert all(d[1] > d[0] for d in drive), drive
