"""Events, SFX, muzik & kapsyen untuk video Raysha pergi sekolah, dikunci pada perkataan VO.
  python3 projects/raysha-sekolah/make_events.py
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
E = dict(raysha=W(0, "Raysha"), l2=L(1), sekolah=W(1, "sekolah"), l3=L(2), kawan=W(2, "kawan"), basikal=W(2, "basikal"), l4=L(3), pikachu=W(3, "Pikachu"),
         l5=L(4), puting=W(4, "puting"), l6=L(5), pampers=W(5, "pampers"), l7=L(6), susu=W(6, "susu"), l8=L(7), teacher1=W(7, "teacher"),
         l9=L(8), makan=W(8, "makan"), l10=L(9), nasi=W(9, "nasi"), mi=W(9, "mi"), sayur=W(9, "vegetable"), l11=L(10), ayam=W(10, "chicken"), buah=W(10, "fruit"),
         l12=L(11), teacher2=W(11, "teacher"), l13=L(12), main=W(12, "main"), teacher3=W(12, "teacher"))
E["outro"] = float(int(vt["lines"][-1]["endBeat"]) + 2); E["total"] = E["outro"] + 5
S = [[0, "pop"], [E["raysha"], "sparkle"], [E["l2"] - 0.4, "whoosh"], [E["sekolah"], "ding"], [E["l3"] - 0.4, "whoosh"], [E["kawan"], "pop"], [E["basikal"], "zip"],
     [E["l4"] - 0.4, "whoosh"], [E["pikachu"], "sparkle"], [E["l5"] - 0.4, "whoosh"], [E["puting"], "buzz"], [E["pampers"], "buzz"], [E["susu"], "buzz"],
     [E["l8"] - 0.4, "whoosh"], [E["teacher1"], "ding"], [E["l9"] - 0.4, "whoosh"], [E["makan"], "munch"], [E["nasi"], "pop"], [E["mi"], "pop"], [E["sayur"], "pop"],
     [E["ayam"], "pop"], [E["buah"], "pop"], [E["l12"] - 0.4, "whoosh"], [E["teacher2"], "ding"], [E["l13"] - 0.4, "whoosh"], [E["main"], "boing"], [E["teacher3"], "sparkle"],
     [E["outro"], "hit"], [E["outro"] + 0.1, "sparkle"]]
tl["sfx"] = sorted([[round(b, 2), k] for b, k in S]); tl["totalBeats"] = E["total"]
tl["music"] = {"breakBeat": E["l5"], "returnBeat": 4 * round(E["l8"] / 4), "endBeat": E["outro"], "introBeats": 6, "crashBeats": [E["l2"], E["l9"], E["l13"]]}
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
