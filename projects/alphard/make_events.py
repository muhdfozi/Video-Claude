"""Jana events.json (untuk animasi) + sfx/music/totalBeats dalam timeline.json,
semuanya dikunci pada perkataan dalam VO (vo_timing.json).

  python3 projects/alphard/make_events.py
"""
import json
from pathlib import Path

P = Path(__file__).parent
vt = json.loads((P / "vo_timing.json").read_text())
tl = json.loads((P / "timeline.json").read_text())
B = 60 / tl["bpm"]
LAG = 0.12  # Whisper cenderung awal sedikit


def L(i):
    return vt["lines"][i]["startBeat"]


def W(i, word, nth=0):
    hits = [w for w in vt["lines"][i]["words"] if word.lower() in w["w"].lower()]
    return round((hits[nth]["t"] + LAG) / B, 2)


E = {
    "title2": W(0, "Alphard"),
    "carIn": 0.4,
    "toBoard": L(1) - 0.6,
    "jpj": W(1, "JPJ"),
    "countStart": W(1, "catat"),
    "countEnd": W(1, "lebih"),
    "clock": L(2) - 0.3,
    "d48": W(2, "48"),
    "perHour": W(2, "dua"),
    "toChart": L(3) - 0.7,
    "y2017": W(3, "2017"),
    "v2017": W(3, "2"),
    "l5": L(4),
    "jump": W(4, "melompat"),
    "x2": W(4, "dua"),
    "y2023": W(5, "setiap"),
    "y2024": W(5, "tahun"),
    "y2025": W(5, "terus"),
    "naik": W(5, "menaik"),
    "toRank": L(6) - 0.7,
    "rankAlph": W(6, "Alphard"),
    "n13": W(6, "13"),
    "civic": W(7, "Civic"),
    "s70": W(7, "S70"),
    "tapi": L(8),
    "hampir": W(8, "hampir"),
    "duaWarna": W(8, "dua"),
    "back": L(9),
    "putih": W(9, "putih"),
    "hitam": W(9, "hitam"),
    "toRoad": L(10) - 0.7,
    "ans": W(10, "Tujuh"),
    "ytd": W(10, "14"),
    "q": L(11),
    "qPutih": W(11, "putih"),
    "qHitam": W(11, "hitam"),
}
end_line = vt["lines"][-1]["endBeat"]
E["outro"] = float(int(end_line) + 2)            # pukulan akhir: beat penuh selepas ayat terakhir
E["comment"] = round(E["qHitam"] + 1.2, 2)
E["total"] = E["outro"] + 4

sfx = [
    [0, "pop"], [E["title2"], "pop"], [E["carIn"], "zip"],
    [E["toBoard"], "whoosh"], [E["jpj"], "pop"], [E["countStart"], "riser3"], [E["countEnd"], "hit"],
    [E["clock"], "pop"], [E["d48"], "ding"], [E["perHour"], "pop"], [E["perHour"] + 0.5, "pop"],
    [E["toChart"], "whoosh"], [E["y2017"], "pop"], [E["v2017"], "pop"],
    [E["l5"] + 0.5, "bubble"], [E["l5"] + 1.0, "bubble"], [E["l5"] + 1.5, "bubble"], [E["l5"] + 2.0, "bubble"],
    [E["jump"], "boing"], [E["x2"], "stamp"],
    [E["y2023"], "pop"], [E["y2024"], "pop"], [E["y2025"], "pop"], [E["naik"], "sparkle"],
    [E["toRank"], "whoosh"], [E["rankAlph"], "ding"], [E["n13"], "stamp"],
    [E["civic"] - 0.4, "swish"], [E["civic"], "pop"], [E["s70"] - 0.6, "swish"], [E["s70"], "hit"],
    [E["tapi"], "boom"], [E["hampir"], "swish"], [E["duaWarna"], "pop"],
    [E["putih"], "sparkle"], [E["hitam"], "pop"],
    [E["toRoad"], "whoosh"], [E["ans"], "hit"], [E["ytd"], "pop"],
    [E["q"], "swish"], [E["q"] + 0.4, "pop"], [E["qPutih"], "pop"], [E["qHitam"], "pop"], [E["comment"], "pop"],
    [E["outro"], "hit"], [E["outro"] + 0.1, "sparkle"],
]
tl["sfx"] = sorted([[round(b, 2), k] for b, k in sfx])
tl["totalBeats"] = E["total"]
tl["music"] = {"breakBeat": E["tapi"], "returnBeat": 4 * round(E["putih"] / 4), "endBeat": E["outro"], "introBeats": 6, "crashBeats": [E["countEnd"], E["jump"]]}
(P / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=2))
(P / "events.json").write_text(json.dumps(E, indent=1))

# ---- kapsyen ikut masa perkataan sebenar
import re
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
