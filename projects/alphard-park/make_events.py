"""Events, SFX, muzik & kapsyen untuk Park Assist Alphard, dikunci pada perkataan VO.
  python3 projects/alphard-park/make_events.py
"""
import json, re
from pathlib import Path

P = Path(__file__).parent
vt = json.loads((P / "vo_timing.json").read_text())
tl = json.loads((P / "timeline.json").read_text())
B = 60 / tl["bpm"]; LAG = 0.12
L = lambda i: vt["lines"][i]["startBeat"]
def W(i, word, nth=0):
    hits = [w for w in vt["lines"][i]["words"] if word.lower() in w["w"].lower()]
    return round((hits[nth]["t"] + LAG) / B, 2)

E = dict(
    title2=W(0, "penting"), sentuh=W(1, "sentuh"), l2=L(1),
    lebihCard=W(2, "kelebihan"), kurangCard=W(2, "kekurangan"), l3=L(2),
    ap=W(3, "Advanced"), sendiri=W(3, "sendiri"), l4=L(3),
    l5=L(4), kamera=W(4, "kamera"), sonar=W(4, "sonar"),
    l6=L(5), steer=W(5, "Steering"), minyak=W(5, "minyak"), brake=W(5, "brake"), control=W(5, "control"),
    l7=L(6), petrol=W(6, "petrol"), gear=W(6, "gear"),
    l8=L(7), senang=W(7, "senang"),
    berhenti=W(8, "Berhenti"), tekan=W(8, "tekan"), screen=W(8, "screen"),
    l10=L(9), depan=W(9, "depan"), undur=W(9, "mengundur"), keluar=W(9, "keluar"),
    l11=L(10), agh=W(10, "AGH40"), pilihan=W(11, "pilihan"), kilang=W(11, "kilang"), l13=L(12), bukan=W(12, "bukan"),
    l14=L(13), m5=W(13, "5"), m48=W(14, "4"), cm32=W(14, "32"),
    l16=L(15), m6=W(15, "6"), semeter=W(15, "semeter"),
    tapi=L(16), kelemahan=W(16, "kelemahan"), l18=L(17), perlahan=W(17, "perlahan"),
    l19=L(18), sabar=W(18, "sabar"), hon=W(18, "hon"),
    l20=L(19), pudar=W(19, "pudar"), takKesan=W(19, "kesan"),
    l21=L(20), sekeliling=W(20, "sekeliling"), tekanBrake=W(20, "brake"), terlanggar=W(20, "terlanggar"), tiang=W(20, "tiang"),
    l22=L(21), l23=L(22), sempit=W(22, "sempit"), selari2=W(22, "selari"), membantu=W(22, "membantu"),
    l24=L(23), mpv=W(23, "MPV"), confident=W(23, "confident"),
    l25=L(24), cekap=W(24, "cekap"), bonus=W(24, "bonus"),
    sales=L(25), apSales=W(25, "Advanced"), y2024=W(25, "2024"), rm262=W(25, "RM262"),
    l27=L(26), komen=W(26, "komen"), dm=W(26, "DM"),
)
E["outro"] = float(int(vt["lines"][-1]["endBeat"]) + 2)
E["total"] = E["outro"] + 5
S = [[0, "pop"], [E["title2"], "pop"], [E["sentuh"], "pop"], [E["lebihCard"], "pop"], [E["kurangCard"], "pop"],
     [E["ap"], "ding"], [E["sendiri"], "zip"], [E["kamera"], "pop"], [E["sonar"], "bubble"],
     [E["steer"], "pop"], [E["minyak"], "pop"], [E["brake"], "pop"], [E["control"], "ding"], [E["gear"], "stamp"],
     [E["berhenti"], "thud"], [E["tekan"], "pop"], [E["screen"], "ding"], [E["depan"], "pop"], [E["undur"], "pop"], [E["keluar"], "zip"],
     [E["l11"] - 0.4, "whoosh"], [E["pilihan"], "stamp"], [E["bukan"], "pop"],
     [E["l14"] - 0.4, "whoosh"], [E["m5"], "pop"], [E["m48"], "pop"], [E["cm32"], "ding"], [E["l16"] - 0.4, "whoosh"], [E["m6"], "pop"], [E["semeter"], "ding"],
     [E["tapi"], "boom"], [E["perlahan"], "boing"], [E["hon"], "buzz"], [E["takKesan"], "buzz"],
     [E["sekeliling"], "pop"], [E["tekanBrake"], "stamp"], [E["tiang"], "hit"],
     [E["l22"], "swish"], [E["membantu"], "ding"], [E["confident"], "sparkle"], [E["bonus"], "hit"],
     [E["sales"] - 0.4, "whoosh"], [E["apSales"], "pop"], [E["y2024"], "pop"], [E["rm262"], "hit"],
     [E["komen"], "pop"], [E["dm"], "ding"], [E["outro"], "hit"], [E["outro"] + 0.1, "sparkle"]]
tl["sfx"] = sorted([[round(b, 2), k] for b, k in S])
tl["totalBeats"] = E["total"]
tl["music"] = {"breakBeat": E["tapi"], "returnBeat": 4 * round(E["l19"] / 4), "endBeat": E["outro"], "introBeats": 6,
               "crashBeats": [E["l14"], E["l22"], E["sales"]]}
(P / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=2))
(P / "events.json").write_text(json.dumps(E, indent=1))

caps = []
for i, ln in enumerate(tl["lines"]):
    words = vt["lines"][i]["words"]; chunks = ln["text"].split("|")
    counts = [len(c.replace("*", "").split()) for c in chunks]; tot = sum(counts); cum = 0
    nxt = vt["lines"][i + 1]["start"] if i + 1 < len(vt["lines"]) else vt["lines"][i]["end"] + 0.8
    starts = []
    for k, c in enumerate(chunks):
        idx = min(len(words) - 1, round(cum / tot * len(words)))
        starts.append(vt["lines"][i]["start"] if k == 0 else words[idx]["t"] + LAG - 0.05); cum += counts[k]
    for k, c in enumerate(chunks):
        segs = [{"t": p[1:-1], "hl": True} if p.startswith("*") else {"t": p, "hl": False} for p in re.split(r"(\*[^*]+\*)", c.strip()) if p]
        caps.append({"line": i + 1, "start": round(starts[k], 3), "end": round(starts[k + 1] if k + 1 < len(chunks) else nxt, 3),
                     "hidden": bool(ln.get("captionHidden")), "segs": segs})
(P / "captions.json").write_text(json.dumps(caps, ensure_ascii=False, indent=1))
print(len(caps), "kapsyen; outro", E["outro"])
