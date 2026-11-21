"""Corrected word list for the voiceover (shared by vo_edit.py and timeline.py).

Whisper's words from video/transcript.json with mishearings fixed and onset
times checked against the audio energy envelope. Times are on the ORIGINAL
recording's clock.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def corrected_words():
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
    fix = {0: 0.80}                                 # "Kalau"
    for i, w in enumerate(words):
        if w["w"] == "Sekali":
            fix[i], fix[i + 1] = 28.10, 28.42
        if w["w"] == "Akhirnya":
            fix[i] = 34.60
    for i, t in fix.items():
        words[i]["t0"] = t
    for i, w in enumerate(words):
        nxt = words[i + 1]["t0"] if i + 1 < len(words) else 39.15
        w["t1"] = min(nxt, w["t0"] + 0.7)
    return words
