"""Events, SFX, muzik & kapsyen untuk video keluarga (Hari Kanak-Kanak), dikunci pada perkataan VO.
  python3 projects/keluarga/make_events.py
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
E = dict(sedunia=W(0, "sedunia"), l2=L(1), raysha=W(1, "Raysha"), psn=W(1, "Pusat"), l3=L(2), bapa=W(2, "bapa"), ibu=W(2, "ibu"),
         l4=L(3), kereta=W(3, "kereta"), l5=L(4), sampai=W(4, "Sampai"), mainSemua=W(4, "main"), l6=L(5), playground=W(5, "playground"), didi=W(5, "Didi"), toys=W(5, "main", 1),
         l7=L(6), lari=W(6, "lari"), lompat=W(6, "lompat"), macam=W(6, "macam"), l8=L(7), balik=W(7, "balik"), dapur=W(7, "dapur"), l9=L(8), shopping=W(8, "shopping"),
         l10=L(9), happy=W(9, "happy"), makanan=W(9, "makanan"), pilih=W(9, "pilih"), l11=L(10), jumpa=W(10, "terjumpa"), pika=W(10, "Pikachu"),
         l12=L(11), pika2=W(11, "Pikachu"), didi2=W(11, "Didi"), rumah=W(11, "rumah"))
E["outro"] = float(int(vt["lines"][-1]["endBeat"]) + 2); E["total"] = E["outro"] + 5
S = [[0, "pop"], [E["sedunia"], "sparkle"], [E["l2"] - 0.4, "whoosh"], [E["psn"], "ding"], [E["bapa"], "pop"], [E["ibu"], "pop"],
     [E["l4"] - 0.4, "whoosh"], [E["kereta"], "zip"], [E["l5"] - 0.4, "whoosh"], [E["mainSemua"], "sparkle"], [E["l6"] - 0.4, "whoosh"], [E["playground"], "boing"],
     [E["didi"], "ding"], [E["toys"], "pop"], [E["l7"] - 0.4, "whoosh"], [E["lari"], "zip"], [E["lompat"], "boing"], [E["lompat"] + 1, "boing"],
     [E["l8"] - 0.4, "whoosh"], [E["dapur"], "pop"], [E["shopping"], "pop"], [E["happy"], "sparkle"], [E["makanan"], "pop"], [E["pilih"], "ding"],
     [E["l11"] - 0.4, "whoosh"], [E["pika"], "sparkle"], [E["l12"] - 0.4, "whoosh"], [E["pika2"], "pop"], [E["didi2"], "pop"], [E["rumah"], "ding"],
     [E["outro"], "hit"], [E["outro"] + 0.1, "sparkle"]]
tl["sfx"] = sorted([[round(b, 2), k] for b, k in S]); tl["totalBeats"] = E["total"]
tl["music"] = {"breakBeat": E["l11"] - 0.5, "returnBeat": 4 * round(E["l12"] / 4), "endBeat": E["outro"], "introBeats": 6, "crashBeats": [E["l2"], E["l5"], E["l8"]]}
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
