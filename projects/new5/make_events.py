"""Events, SFX, muzik & kapsyen untuk video Raysha + kawan kuning, dikunci pada perkataan VO.
  python3 projects/new5/make_events.py
"""
import json, re
from pathlib import Path
P = Path(__file__).parent
vt = json.loads((P / "vo_timing.json").read_text()); tl = json.loads((P / "timeline.json").read_text())
B = 60 / tl["bpm"]; LAG = 0.12
L = lambda i: vt["lines"][i]["startBeat"]
def W(i, word, nth=0):
    hits = [w for w in vt["lines"][i]["words"] if word.lower() in w["w"].lower()]
    return round((hits[nth]["t"] + LAG) / B, 2)
E = dict(title2=W(0, "Pikachu"), malaysia=W(0, "Malaysia"), l2=L(1), berkawan=W(1, "berkawan"), anakAku=W(1, "anak"),
         l3=L(2), raysha=W(2, "Raysha"), l4=L(3), umur2=W(3, "2"), minat=W(3, "minat"),
         l5=L(4), tidur=W(4, "tidur"), l6=L(5), makan=W(5, "makan"), l7=L(6), main=W(6, "bermain"),
         l8=L(7), datang=W(7, "datang"), sekolah=W(7, "sekolah"), l9=L(8), basikal=W(8, "basikal"),
         l10=L(9), romantik=W(9, "romantik"), l11=L(10), suka=W(10, "suka"), sayang=W(10, "sayang"),
         l12=L(11), hariJadi=W(11, "Hari"), sambut=W(11, "sambut"))
E["outro"] = float(int(vt["lines"][-1]["endBeat"]) + 2); E["total"] = E["outro"] + 5
S = [[0, "pop"], [E["title2"] - 0.3, "zip"], [E["title2"], "sparkle"], [E["malaysia"], "pop"],
     [E["l2"] - 0.4, "whoosh"], [E["berkawan"], "sparkle"], [E["anakAku"], "pop"], [E["raysha"], "ding"], [E["umur2"], "pop"], [E["minat"], "sparkle"],
     [E["l5"] - 0.4, "whoosh"], [E["tidur"], "pop"], [E["l6"] - 0.4, "whoosh"], [E["makan"], "munch"],
     [E["l7"] - 0.4, "whoosh"], [E["main"], "boing"], [E["l8"] - 0.4, "whoosh"], [E["sekolah"], "ding"],
     [E["l9"] - 0.4, "whoosh"], [E["basikal"], "zip"], [E["romantik"], "sparkle"], [E["l11"] - 0.3, "whoosh"], [E["suka"], "pop"], [E["sayang"], "pop"],
     [E["l12"] - 0.4, "whoosh"], [E["hariJadi"], "hit"], [E["sambut"], "sparkle"], [E["outro"], "hit"], [E["outro"] + 0.1, "sparkle"]]
tl["sfx"] = sorted([[round(b, 2), k] for b, k in S]); tl["totalBeats"] = E["total"]
tl["music"] = {"breakBeat": E["l10"], "returnBeat": 4 * round(E["l11"] / 4), "endBeat": E["outro"], "introBeats": 6, "crashBeats": [E["l2"], E["l12"]]}
(P / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=2)); (P / "events.json").write_text(json.dumps(E, indent=1))
caps = []
for i, ln in enumerate(tl["lines"]):
    words = vt["lines"][i]["words"]; chunks = ln["text"].split("|"); counts = [len(c.replace("*", "").split()) for c in chunks]; tot = sum(counts); cum = 0
    nxt = vt["lines"][i + 1]["start"] if i + 1 < len(vt["lines"]) else vt["lines"][i]["end"] + 0.8
    starts = []
    for k, c in enumerate(chunks):
        idx = min(len(words) - 1, round(cum / tot * len(words))); starts.append(vt["lines"][i]["start"] if k == 0 else words[idx]["t"] + LAG - 0.05); cum += counts[k]
    for k, c in enumerate(chunks):
        segs = [{"t": p[1:-1], "hl": True} if p.startswith("*") else {"t": p, "hl": False} for p in re.split(r"(\*[^*]+\*)", c.strip()) if p]
        caps.append({"line": i + 1, "start": round(starts[k], 3), "end": round(starts[k + 1] if k + 1 < len(chunks) else nxt, 3), "hidden": bool(ln.get("captionHidden")), "segs": segs})
(P / "captions.json").write_text(json.dumps(caps, ensure_ascii=False, indent=1))
print(len(caps), "kapsyen; outro", E["outro"])
