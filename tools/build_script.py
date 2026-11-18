"""Jana captions.json, captions.srt dan skrip-vo.md daripada timeline.json.

Guna:  python3 tools/build_script.py projects/durian
"""
import json
import re
import sys
from pathlib import Path


def parse_chunk(chunk):
    """'Bau *durian* sedap' -> [{'t': 'Bau ', 'hl': False}, {'t': 'durian', 'hl': True}, ...]"""
    parts = re.split(r"(\*[^*]+\*)", chunk.strip())
    out = []
    for p in parts:
        if not p:
            continue
        if p.startswith("*") and p.endswith("*"):
            out.append({"t": p[1:-1], "hl": True})
        else:
            out.append({"t": p, "hl": False})
    return out


def plain(text):
    return text.replace("*", "").replace(" | ", " ").replace("|", " ")


def tc(sec, srt=False):
    m, s = divmod(sec, 60)
    if srt:
        h, m = divmod(int(m), 60)
        return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s % 1) * 1000)):03d}"
    return f"{int(m):d}:{s:04.1f}"


def main(proj):
    proj = Path(proj)
    tl = json.loads((proj / "timeline.json").read_text())
    beat = 60.0 / tl["bpm"]
    bpb = tl["beatsPerBar"]
    captions = []
    for i, ln in enumerate(tl["lines"]):
        s_beat = ln["bar"] * bpb
        span = ln["bars"] * bpb
        speak = span - 1.0  # sebat terakhir = ruang nafas
        chunks = [c for c in ln["text"].split("|")]
        words = [max(1, len(plain(c).split())) for c in chunks]
        total = sum(words)
        cum = 0
        for j, c in enumerate(chunks):
            start_b = s_beat + speak * cum / total
            cum += words[j]
            end_b = s_beat + speak * cum / total if j < len(chunks) - 1 else s_beat + span
            captions.append({
                "line": i + 1,
                "start": round(start_b * beat, 3),
                "end": round(end_b * beat, 3),
                "startBeat": round(start_b, 3),
                "hidden": bool(ln.get("captionHidden")),
                "segs": parse_chunk(c),
            })
    (proj / "captions.json").write_text(json.dumps(captions, ensure_ascii=False, indent=1))

    # SRT (untuk upload kapsyen ke IG/TikTok jika perlu)
    srt = []
    for k, c in enumerate(captions, 1):
        text = "".join(s["t"] for s in c["segs"]).strip()
        srt.append(f"{k}\n{tc(c['start'], True)} --> {tc(c['end'], True)}\n{text}\n")
    (proj / "captions.srt").write_text("\n".join(srt))

    # Skrip VO
    bar_s = beat * bpb
    rows = []
    has_screen = any("screen" in ln for ln in tl["lines"])
    for i, ln in enumerate(tl["lines"]):
        t0 = ln["bar"] * bar_s
        t1 = (ln["bar"] + ln["bars"]) * bar_s
        txt = re.sub(r"\*([^*]+)\*", r"**\1**", ln["text"]).replace(" | ", " ").replace("|", " ")
        n = len(plain(ln["text"]).split())
        scr = f" {ln.get('screen', '')} |" if has_screen else ""
        rows.append(f"| {i+1} | `{tc(t0)}` → `{tc(t1)}` | {ln['role']} | {txt} | {n} | {ln['tone']} |{scr}")
    total_s = tl["totalBeats"] * beat
    md = f"""# Skrip VO — {tl['title']}

**Tempo:** {tl['bpm']} BPM · 1 bar = {bar_s:.2f} s · setiap ayat masuk **tepat pada permulaan bar** (setiap {2*bar_s:.2f} s)
**Durasi:** {total_s:.1f} s + {tl['tailSeconds']} s outro muzik · **Kelajuan sasaran:** ~2 patah perkataan sesaat

> Perkataan **bold** = kata kunci. Sebut dengan tekanan sedikit, sebab perkataan tu menyala oren dalam kapsyen.

| # | Masa | Bahagian | Ayat VO | Perkataan | Nada / arahan |{" Paparan skrin |" if has_screen else ""}
|---|---|---|---|---|---|{"---|" if has_screen else ""}
{chr(10).join(rows)}

## Cara rakam

1. **Bilik senyap.** Bilik tidur yang banyak kain (langsir, tilam) lagi bagus dari bilik kosong. Matikan kipas/aircond masa rakam.
2. **Telefon 15–20 cm dari mulut**, sedikit ke tepi (elak bunyi "p" meletup). Guna app rakam suara biasa; format WAV atau M4A.
3. **Pakai earphone, main `{proj.name}_preview.mp4`**, dan baca ikut kapsyen yang muncul. Kapsyen tu adalah teleprompter kau: ia muncul tepat bila kau patut mula sebut. Ayat 1 (hook) tiada kapsyen, jadi baca tajuk besar di atas.
4. **Tak perlu sempurna timing.** Kalau terlebih/terkurang sikit, tak apa. Aku akan potong dan selaraskan setiap ayat dengan beat dan animasi.
5. Rakam **2 take penuh**. Kalau satu ayat tersasul, ulang ayat tu saja, kemudian sambung.
6. Senyum masa baca ayat 3, 9 dan 12. Senyum tu kedengaran dalam suara.

Hantar file rakaman kepada aku (letak dalam `projects/{proj.name}/vo/`), dan aku akan:
- buang bunyi bising & nafas kuat, EQ + kompres suara,
- selaraskan setiap ayat dengan animasi,
- duck muzik secara automatik bila kau bercakap,
- render video akhir.
"""
    if tl.get("facts"):
        md += "\n## Fakta & sumber\n\n" + "\n".join(f"- {f}" for f in tl["facts"]) + "\n"
    (proj / "skrip-vo.md").write_text(md)
    print(f"{len(captions)} kapsyen, durasi {total_s:.2f}s")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "projects/durian")
