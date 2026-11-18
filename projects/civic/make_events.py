"""Jana events.json + sfx/music/kapsyen untuk video Civic, dikunci pada perkataan VO.
  python3 projects/civic/make_events.py
"""
import json
import re
from pathlib import Path

P = Path(__file__).parent
vt = json.loads((P / "vo_timing.json").read_text())
tl = json.loads((P / "timeline.json").read_text())
B = 60 / tl["bpm"]
LAG = 0.12


def L(i):
    return vt["lines"][i]["startBeat"]


def W(i, word, nth=0):
    hits = [w for w in vt["lines"][i]["words"] if word.lower() in w["w"].lower()]
    return round((hits[nth]["t"] + LAG) / B, 2)


E = {
    "buy": W(0, "beli"), "title2": W(0, "tapi"),
    "money": W(1, "duit"), "asap": W(1, "asap"),
    "toPack": L(2) - 0.8, "price": W(2, "RM18"),
    "toCal": L(3) - 0.7, "month": W(3, "sebulan"), "m500": W(3, "RM500"),
    "year": W(4, "Setahun"), "y6000": W(4, "RM6"),
    "toBank": L(5) - 0.7, "tabung": W(5, "tabung"),
    "think": W(6, "berapa"), "civic": W(6, "Civic"),
    "toTower": L(7) - 0.7, "k15": W(7, "15"), "rm273": W(7, "RM273"),
    "tapi": L(8), "y41": W(8, "41"),
    "quit": W(9, "berhenti"), "less": W(9, "kurangkan"),
    "back": L(10), "noSmoke": W(10, "merokok"), "fl5": W(10, "FL5"),
    "foot": L(11) - 0.4, "unit2": W(11, "2"), "y2025": W(11, "2025"), "racing": W(11, "Racing"), "ready": W(11, "ready"),
    "footB": W(12, "Harganya") - 0.2, "rm270": W(12, "RM270"),
    "footC": L(13) + 0.6, "komen": W(13, "Komen"), "dm": W(13, "DM"),
}
E["cta"] = E["footC"] + 4.7
E["outro"] = float(int(vt["lines"][-1]["endBeat"]) + 2)
E["total"] = E["outro"] + 5

sfx = [
    [0, "pop"], [E["title2"], "pop"], [E["buy"], "pop"],
    [E["money"], "bubble"], [E["money"] + 0.6, "bubble"], [E["asap"], "swish"],
    [E["toPack"], "whoosh"], [E["price"], "ding"],
    [E["toCal"], "whoosh"], [E["month"], "riser3"], [E["m500"], "hit"], [E["year"], "swish"], [E["y6000"], "hit"],
    [E["toBank"], "whoosh"], [E["tabung"], "pop"], [E["tabung"] + 0.5, "bubble"], [E["tabung"] + 1.0, "bubble"],
    [E["think"], "pop"], [E["civic"], "ding"],
    [E["toTower"], "whoosh"], [E["k15"] - 0.8, "riser3"], [E["k15"], "hit"], [E["rm273"], "stamp"],
    [E["tapi"], "boom"], [E["y41"], "stamp"],
    [E["quit"], "buzz"], [E["less"], "pop"],
    [E["back"] - 0.3, "whoosh"], [E["noSmoke"], "pop"], [E["fl5"], "zip"],
    [E["foot"], "whoosh"], [E["unit2"], "pop"], [E["racing"], "pop"], [E["ready"], "stamp"],
    [E["footB"], "swish"], [E["rm270"], "hit"],
    [E["footC"], "swish"], [E["komen"], "pop"], [E["dm"], "ding"],
    [E["cta"], "pop"], [E["outro"], "hit"], [E["outro"] + 0.1, "sparkle"],
]
tl["sfx"] = sorted([[round(b, 2), k] for b, k in sfx])
tl["totalBeats"] = E["total"]
tl["music"] = {"breakBeat": E["tapi"], "returnBeat": 4 * round(E["back"] / 4), "endBeat": E["outro"], "introBeats": 6,
               "crashBeats": [E["m500"], E["k15"], E["foot"] + 0.4]}
(P / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=2))
(P / "events.json").write_text(json.dumps(E, indent=1))

caps = []
for i, ln in enumerate(tl["lines"]):
    words = vt["lines"][i]["words"]
    chunks = ln["text"].split("|")
    counts = [len(c.replace("*", "").split()) for c in chunks]
    tot = sum(counts); cum = 0
    nxt = vt["lines"][i + 1]["start"] if i + 1 < len(vt["lines"]) else vt["lines"][i]["end"] + 0.8
    starts = []
    for k, c in enumerate(chunks):
        idx = min(len(words) - 1, round(cum / tot * len(words)))
        starts.append(vt["lines"][i]["start"] if k == 0 else words[idx]["t"] + LAG - 0.05)
        cum += counts[k]
    for k, c in enumerate(chunks):
        segs = [{"t": p[1:-1], "hl": True} if p.startswith("*") else {"t": p, "hl": False}
                for p in re.split(r"(\*[^*]+\*)", c.strip()) if p]
        caps.append({"line": i + 1, "start": round(starts[k], 3), "end": round(starts[k + 1] if k + 1 < len(chunks) else nxt, 3),
                     "hidden": bool(ln.get("captionHidden")), "segs": segs})
(P / "captions.json").write_text(json.dumps(caps, ensure_ascii=False, indent=1))
print(json.dumps(E))
