"""'Rentak' graphics theme (THEME = "rentak") — the user's own style, inspired by (not copied from)
four TikTok references studied frame by frame.

Identity
- Speed rule: everything lands ON THE BEAT of a 110 BPM grid (0.545 s). build.py time-stretches the
  music to 110 BPM, picks the beat phase that best matches the speech cuts and passes BEATS here.
- Palette: charcoal ink + warm cream + one signature accent: orange (#FF5A1F).
- Type: Anton (condensed caps) for kinetic words, Instrument Serif Italic for the one emotional/accent
  word, JetBrains Mono for HUD/ledger numbers, Inter Display for sentences.
- Signature pieces: HUD (REC dot, chapter index, segmented progress bar), word SLAM panels (one word per
  beat), mono LEDGER cards that type in row by row, rolling mono COUNTER with an orange bar, orange
  viewfinder BRACKETS, beat FLASH, TAG pills with an orange edge.
"""
import os
from PIL import ImageFont

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
SYS = "/usr/share/fonts"
_F = {
    "anton": os.path.join(FONTS, "Anton.ttf"),
    "serif": os.path.join(FONTS, "InstrumentSerifItalic.ttf"),
    "mono": "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-ExtraBold.ttf",
    "sans": "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf",
}
_cache, _scale = {}, {}


def _ls(path):
    if path not in _scale:
        from fontTools.ttLib import TTFont
        f = TTFont(path); o = f["OS/2"]
        _scale[path] = f["head"].unitsPerEm / (o.usWinAscent + o.usWinDescent)
    return _scale[path]


def tw(text, key, fs):
    path = _F[key]
    if not os.path.exists(path):
        path = _F["sans"]
    k = (path, round(fs * _ls(path)))
    if k not in _cache:
        _cache[k] = ImageFont.truetype(path, k[1])
    return _cache[k].getlength(text)


def rrect(w, h, r):
    return (f"m {r} 0 l {w-r} 0 b {w} 0 {w} 0 {w} {r} l {w} {h-r} b {w} {h} {w} {h} {w-r} {h} "
            f"l {r} {h} b 0 {h} 0 {h} 0 {h-r} l 0 {r} b 0 0 0 0 {r} 0")


def rect(w, h):
    return f"m 0 0 l {w} 0 l {w} {h} l 0 {h}"


def ease_out(x):
    return 1 - (1 - x) ** 3


def money(v, prefix="RM"):
    return prefix + f"{v:,.0f}"


def render(R, src2out, add, TOTAL, C, sfx_events, FPS, BEATS, accent="FF5A1F"):
    INK, CREAM, ACC, GREY, WHITE, BLACK, RED = (C("111113"), C("F3EFE6"), C(accent), C("9A968E"), C("FFFFFF"),
                                                C("000000"), C("FF3B30"))
    ANTON, SERIF, MONO, SANS = r"\fnAnton", r"\fnInstrument Serif Italic", r"\fnJetBrains Mono ExtraBold", r"\fnInter Display SemiBold"
    SH = r"\shad3\4c&H000000&\4a&H70&"
    beat = 60.0 / R.get("bpm", 110)

    def snap(t, tol=0.22):
        if not BEATS: return t
        b = min(BEATS, key=lambda x: abs(x - t))
        return b if abs(b - t) <= tol else t

    def next_beats(t, n):
        out = [b for b in BEATS if b >= t - 1e-3][:n]
        while len(out) < n:
            out.append((out[-1] if out else t) + beat)
        return out

    def T(src, tol=0.22):
        v = src2out(src)
        return None if v is None else snap(v, tol)

    # ---------------------------------------------------------------- HUD (REC dot, chapter, progress)
    ch = [(T(a), name) for a, name in R.get("chapters", [])]
    ch = [(t, n) for t, n in ch if t is not None]
    if ch:
        n = len(ch); x0, x1, y = 60, 1020, 292; gap = 10
        segw = (x1 - x0 - gap * (n - 1)) / n
        t_hud = 0.0
        blink = "".join(r"\t(%d,%d,\alpha&HFF&)\t(%d,%d,\alpha&H00&)" % (i * 1090 + 545, i * 1090 + 546, i * 1090 + 1090, i * 1090 + 1091)
                        for i in range(int(TOTAL / 1.09) + 1))
        add(t_hud, TOTAL, "{" + r"\an4\pos(62,252)\p1\bord0" + SH + r"\c" + RED + "&" + blink + "}" + "m 0 -9 b 5 -9 9 -5 9 0 b 9 5 5 9 0 9 b -5 9 -9 5 -9 0 b -9 -5 -5 -9 0 -9", 9)
        add(t_hud, TOTAL, "{" + r"\an4\pos(84,252)" + MONO + r"\fs30\fsp2\bord0" + SH + r"\c" + WHITE + "&}REC", 9)
        for i, (t0, name) in enumerate(ch):
            t1 = ch[i + 1][0] if i + 1 < n else TOTAL
            sx = x0 + i * (segw + gap)
            add(0, TOTAL, "{" + r"\an7\pos(" + f"{sx:.0f},{y}" + r")\p1\bord0\shad0\c" + WHITE + r"&\1a&H90&}" + rect(segw, 6), 8)
            add(t0, TOTAL, "{" + r"\an7\pos(" + f"{sx:.0f},{y}" + r")\p1\bord0\shad0\c" + ACC + r"&\clip(" + f"{sx:.0f},0,{sx:.0f},1920)"
                + r"\t(0," + f"{int((t1 - t0) * 1000)}" + r",\clip(" + f"{sx:.0f},0,{sx + segw:.0f},1920))" + "}" + rect(segw, 6), 9)
            add(t0, t1, "{" + r"\an4\pos(176,252)" + MONO + r"\fs30\fsp2\bord0" + SH + r"\c" + WHITE + r"&\fad(80,0)}" + f"{i + 1:02d}/{n:02d} · " + "{\\c" + ACC + "&}" + name.upper(), 9)

    # ---------------------------------------------------------------- elements
    for g in R.get("items", []):
        k = g["kind"]
        t0 = T(g["at"])
        if t0 is None: continue
        tu = T(g["until"]) if g.get("until") else None
        t1 = min((tu if tu is not None else TOTAL) if g.get("until") else t0 + g.get("dur", 2.0), TOTAL)

        if k == "slam":
            # panel wipes in on the beat; one word per beat; accent word(s) in serif italic orange
            words = g["words"]; acc = set(g.get("acc", [len(words) - 1]))
            bts = next_beats(t0, len(words) + g.get("hold", 2))
            t_end = min(bts[-1] + 0.05, TOTAL) if not g.get("until") else t1
            pa = g.get("alpha", "18")
            add(t0, t_end, "{" + r"\an7\move(1180,0,0,0,0,130)\p1\bord0\shad0\c" + INK + r"&\1a&H" + pa + r"&\fad(0,120)}"
                + "m 160 0 l 1240 0 l 1080 1920 l -160 1920", 6)
            fs = g.get("fs", 190)
            lh = fs * 1.02
            y0 = g.get("y", 960) - lh * (len(words) - 1) / 2
            for i, w in enumerate(words):
                ta = bts[i]
                is_acc = i in acc
                f = (SERIF + r"\fs" + str(int(fs * 1.12)) + r"\c" + ACC) if is_acc else (ANTON + r"\fs" + str(fs) + r"\c" + CREAM)
                add(ta, t_end, "{" + r"\an5\pos(540," + f"{y0 + lh * i:.0f}" + r")\fscx130\fscy130\t(0,90,\fscx100\fscy100)\fad(0,120)\bord0\shad0" + f + "&}" + w, 7)
                sfx_events.append((ta, "click"))
            sfx_events.append((t0, "soft"))

        elif k == "tag":
            parts = g["text"].split("*")
            plain = "".join(parts)
            w = tw(plain, "sans", 58) + 150 + (60 if g.get("idx") else 0); h = 104
            y = g.get("y", 1400); x0 = 540 - w / 2
            mv = lambda x, yy: r"\move(" + f"{x - 60:.0f},{yy:.0f},{x:.0f},{yy:.0f},0,150" + ")"
            add(t0, t1, "{" + r"\an7" + mv(x0, y - h / 2) + r"\fad(0,140)\p1\bord0\shad0\c" + INK + r"&\1a&H18&}" + rrect(w, h, 16), 7)
            add(t0, t1, "{" + r"\an7" + mv(x0, y - h / 2) + r"\fad(0,140)\p1\bord0\shad0\c" + ACC + "&}" + rrect(12, h, 6), 8)
            tx = x0 + 44
            if g.get("idx"):
                add(t0, t1, "{" + r"\an4" + mv(tx, y) + r"\fad(0,140)" + MONO + r"\fs34\bord0\shad0\c" + ACC + "&}" + g["idx"], 8)
                tx += 70
            body = "".join(("{\\c" + ACC + "&}" + p + "{\\c" + CREAM + "&}") if i % 2 else p for i, p in enumerate(parts))
            add(t0, t1, "{" + r"\an4" + mv(tx, y) + r"\fad(0,140)" + SANS + r"\fs58\bord0\shad0\c" + CREAM + "&}" + body, 8)
            sfx_events.append((t0, "click"))

        elif k == "counter":
            y = g.get("y", 1400); w, h = 900, 300; x0 = 540 - w / 2
            add(t0, t1, "{" + r"\an7\pos(" + f"{x0:.0f},{y - h / 2:.0f}" + r")\fad(100,160)\p1\bord0\shad0\c" + INK + r"&\1a&H12&}" + rrect(w, h, 22), 7)
            add(t0, t1, "{" + r"\an7\pos(" + f"{x0 + 40:.0f},{y - h / 2 + 30:.0f}" + r")\fad(100,160)" + MONO + r"\fs28\fsp4\bord0\shad0\c" + GREY + "&}" + g.get("label", "").upper(), 8)
            roll = g.get("roll", 1.1); nfr = max(1, int(roll * FPS)); frm = g.get("frm", 0); to = g["to"]; pre = g.get("prefix", "RM")
            for j in range(nfr):
                a = t0 + j / FPS
                add(a, a + 1 / FPS, "{" + r"\an5\pos(540," + f"{y + 6:.0f}" + ")" + MONO + r"\fs118\bord0\shad0\c" + CREAM + "&}" + money(frm + (to - frm) * ease_out((j + 1) / nfr), pre), 8)
            add(t0 + roll, t1, "{" + r"\an5\pos(540," + f"{y + 6:.0f}" + r")\fad(0,160)" + MONO + r"\fs118\bord0\shad0\c" + (ACC if g.get("accent") else CREAM) + "&}" + money(to, pre), 8)
            add(t0, t1, "{" + r"\an7\pos(" + f"{x0 + 40:.0f},{y + h / 2 - 54:.0f}" + r")\fad(100,160)\p1\bord0\shad0\c" + ACC + r"&\clip(" + f"{x0 + 40:.0f},0,{x0 + 40:.0f},1920)"
                + r"\t(0," + f"{int(roll * 1000)}" + r",\clip(" + f"{x0 + 40:.0f},0,{x0 + w - 40:.0f},1920))" + "}" + rect(w - 80, 8), 8)
            if g.get("sub"):
                add(t0 + roll * 0.6, t1, "{" + r"\an5\pos(540," + f"{y + h / 2 + 50:.0f}" + r")\fad(120,160)" + SANS + r"\fs42\bord0" + SH + r"\c" + WHITE + "&}" + g["sub"], 8)
            sfx_events.append((t0, "click")); sfx_events.append((t0 + roll, "cash" if g.get("accent") else "pop"))
            if g.get("flash"):
                add(t0 + roll, t0 + roll + 2 / FPS, "{" + r"\an7\pos(0,0)\p1\bord0\shad0\c" + CREAM + r"&\1a&H70&}" + rect(1080, 1920), 9)

        elif k == "ledger":
            rows = g["rows"]; y = g.get("y", 1060); w = 920; x0 = 540 - w / 2; rh = 92
            h = 130 + rh * len(rows) + 30
            add(t0, t1, "{" + r"\an7\move(" + f"{x0:.0f},{y + 40},{x0:.0f},{y}" + r",0,160)\fad(100,160)\p1\bord0\shad0\c" + INK + r"&\1a&H12&}" + rrect(w, h, 22), 7)
            add(t0, t1, "{" + r"\an7\move(" + f"{x0 + 40:.0f},{y + 76},{x0 + 40:.0f},{y + 36}" + r",0,160)\fad(100,160)\p1\bord0\shad0\c" + ACC + "&}" + rect(26, 26), 8)
            add(t0, t1, "{" + r"\an4\move(" + f"{x0 + 86:.0f},{y + 89},{x0 + 86:.0f},{y + 49}" + r",0,160)\fad(100,160)" + ANTON + r"\fs64\bord0\shad0\c" + CREAM + "&}" + g["title"].upper(), 8)
            for i, row in enumerate(rows):
                at, lab, val = row[:3]; total = len(row) > 3 and row[3] == "total"
                ta = max(t0, T(at)); yy = y + 130 + rh * i + rh / 2
                if ta >= t1: continue
                if total:
                    add(ta, t1, "{" + r"\an7\pos(" + f"{x0 + 40:.0f},{yy - rh / 2:.0f}" + r")\fad(0,160)\p1\bord0\shad0\c" + ACC + "&}" + rect(w - 80, 3), 8)
                sweep = r"\clip(" + f"{x0:.0f},0,{x0:.0f},1920)" + r"\t(0,220,\clip(" + f"{x0:.0f},0,{x0 + w:.0f},1920))"
                add(ta, t1, "{" + r"\an4\pos(" + f"{x0 + 40:.0f},{yy:.0f}" + ")" + sweep + r"\fad(0,160)" + MONO + r"\fs38\bord0\shad0\c" + (CREAM if total else GREY) + "&}" + lab, 8)
                add(ta, t1, "{" + r"\an6\pos(" + f"{x0 + w - 40:.0f},{yy:.0f}" + ")" + sweep + r"\fad(0,160)" + MONO + r"\fs" + ("56" if total else "46")
                    + r"\bord0\shad0\c" + (ACC if total else CREAM) + "&}" + val, 8)
                sfx_events.append((ta, "cash" if total else "click"))
            sfx_events.append((t0, "soft"))

        elif k == "brackets":
            x, y, w, h = g.get("box", (190, 420, 700, 760)); L = 90; th = 9
            snapin = r"\fscx118\fscy118\t(0,110,\fscx100\fscy100)\fad(60,160)"
            cx, cy = x + w / 2, y + h / 2
            corners = [(x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)]
            for (px, py, sx, sy) in corners:
                d = (f"m 0 0 l {L * sx} 0 l {L * sx} {th * sy} l {th * sx} {th * sy} l {th * sx} {L * sy} l 0 {L * sy}")
                add(t0, t1, "{" + r"\an7\pos(" + f"{px:.0f},{py:.0f}" + r")\org(" + f"{cx:.0f},{cy:.0f}" + ")" + snapin + r"\p1\bord0" + SH + r"\c" + ACC + "&}" + d, 9)
            if g.get("label"):
                add(t0, t1, "{" + r"\an1\pos(" + f"{x + 4:.0f},{y - 14:.0f}" + r")\fad(60,160)" + MONO + r"\fs26\fsp3\bord0" + SH + r"\c" + ACC + "&}" + g["label"].upper(), 9)
            sfx_events.append((t0, "click"))

        elif k == "flash":
            add(t0, t0 + 2 / FPS, "{" + r"\an7\pos(0,0)\p1\bord0\shad0\c" + CREAM + r"&\1a&H60&}" + rect(1080, 1920), 9)
