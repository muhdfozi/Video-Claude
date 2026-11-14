"""'Paper collage' graphics theme (THEME = "paper" in an edl.py).

Visual language studied from an explainer reference: cream torn-paper cards, yellow highlighter
sweep on the key word, masking-tape labels, typewriter tags, marker handwriting, red rubber stamps.
Everything is ASS (libass) so it renders in the same pass as before, in SDR or HLG (colours via C()).

Rotation note: every layer of one element shares \\org and \\frz, and elements enter with a slide
(\\move) instead of a scale pop, so the paper, highlight and text never drift apart.
"""
import os, random
from PIL import ImageFont

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
_cache = {}
def font(name, size):
    k = (name, size)
    if k not in _cache:
        _cache[k] = ImageFont.truetype(os.path.join(FONTS, name), size)
    return _cache[k]

_lscale = {}
def libass_scale(fname):
    """libass sizes a font so (winAscent + winDescent) == \\fs; PIL sizes by em. Ratio em/(asc+desc)."""
    if fname not in _lscale:
        from fontTools.ttLib import TTFont
        f = TTFont(os.path.join(FONTS, fname)); os2 = f["OS/2"]
        _lscale[fname] = f["head"].unitsPerEm / (os2.usWinAscent + os2.usWinDescent)
    return _lscale[fname]

def tw(text, fname, size):
    """Width of text as libass will draw it at \\fs=size."""
    return font(fname, max(1, round(size * libass_scale(fname)))).getlength(text)

HAND, MARKER, TYPE = "PatrickHand.ttf", "PermanentMarker.ttf", "SpecialElite.ttf"
HAND_N, MARKER_N, TYPE_N = "Patrick Hand", "Permanent Marker", "Special Elite"


def torn(w, h, seed, jag=5, step=16):
    """Paper rectangle with torn top and bottom edges, as an ASS drawing from (0,0)."""
    r = random.Random(seed)
    pts = [(0, r.uniform(0, jag))]
    x = 0
    while x < w:
        x = min(w, x + r.uniform(step * 0.6, step * 1.3)); pts.append((x, r.uniform(0, jag)))
    x = w; bot = [(w, h - r.uniform(0, jag))]
    while x > 0:
        x = max(0, x - r.uniform(step * 0.6, step * 1.3)); bot.append((x, h - r.uniform(0, jag)))
    p = pts + bot
    return "m " + " l ".join(f"{a:.0f} {b:.0f}" for a, b in p)


def rect(w, h):
    return f"m 0 0 l {w} 0 l {w} {h} l 0 {h}"


def tape(w, h, seed):
    """Masking tape strip with zig-zag short ends."""
    r = random.Random(seed)
    pts = [(0, 0), (w, 0)]
    for i in range(1, 6):
        pts.append((w - r.uniform(0, 7), h * i / 6))
    pts.append((w, h)); pts.append((0, h))
    for i in range(5, 0, -1):
        pts.append((r.uniform(0, 7), h * i / 6))
    return "m " + " l ".join(f"{a:.0f} {b:.0f}" for a, b in pts)


def arrow_down(len_=120, w=14):
    """Hand-drawn-ish downward arrow (slightly curved shaft + head)."""
    return (f"m 0 0 b {w*1.5} {len_*0.35} {-w} {len_*0.6} {w*0.4} {len_*0.82} "
            f"l {-w*2.2} {len_*0.72} l {w*0.9} {len_*1.08} l {w*2.6} {len_*0.66} l {w*1.4} {len_*0.8} "
            f"b {w*0.6} {len_*0.55} {w*2.6} {len_*0.32} {w} 0")


def render(GRAPHICS, KEYPOINTS, src2out, add, TOTAL, C, sfx_events, KEYPOINTS_ON=True):
    PAPER, INK, HILITE, TAG, RED, TAPE, GREY = (C("FCFAF4"), C("1C1B19"), C("FFE14D"), C("F7D84A"),
                                                 C("D23A2C"), C("E9DDC1"), C("5B5750"))
    SH = r"\shad7\4c&H000000&\4a&HA8&"             # soft paper shadow

    def slide(x, y, dy=36, ms=180):
        return r"\move(" + f"{x:.0f},{y + dy:.0f},{x:.0f},{y:.0f},0,{ms}" + ")"

    def paper_note(t0, t1, cx, cy, parts, fs, fname, fn_name, ink, rot, seed, hl=True, bg=None, sfx="paper"):
        """Torn paper strip with one line of text; *word* gets a highlighter sweep."""
        plain = "".join(parts)
        w = tw(plain, fname, fs) + 64; h = fs * 1.45
        x0, y0 = cx - w / 2, cy - h / 2
        org = r"\org(" + f"{cx:.0f},{cy:.0f}" + ")"
        common = org + r"\frz" + f"{rot}" + r"\fad(90,140)"
        add(t0, t1, "{" + r"\an7" + slide(x0, y0) + common + r"\p1\bord0" + SH + r"\c" + (bg or PAPER) + "&}" + torn(w, h, seed), 5)
        # highlighter behind the keyword
        if hl:
            xa = x0 + 32
            for i, p in enumerate(parts):
                if i % 2 == 1:
                    kw = tw(p, fname, fs)
                    hx, hy, hh = xa - 6, cy - fs * 0.22, fs * 0.46
                    ta, tb = 220, 520
                    clip0 = r"\clip(" + f"{hx - 40:.0f},{cy - h:.0f},{hx - 40:.0f},{cy + h:.0f}" + ")"
                    clip1 = r"\clip(" + f"{hx - 40:.0f},{cy - h:.0f},{hx + kw + 52:.0f},{cy + h:.0f}" + ")"
                    add(t0, t1, "{" + r"\an7" + slide(hx, hy) + common + clip0 + r"\t(" + f"{ta},{tb}," + clip1 + ")"
                        + r"\p1\bord0\shad0\c" + HILITE + r"&\1a&H20&}" + rect(kw + 12, hh), 6)
                xa += tw(p, fname, fs)
        add(t0, t1, "{" + r"\an4" + slide(x0 + 32, cy) + common + r"\bord0\shad0\fn" + fn_name + r"\fs" + str(fs)
            + r"\c" + ink + "&}" + plain, 7)
        # small piece of tape on the top-left corner
        add(t0, t1, "{" + r"\an5" + slide(x0 + 26, y0 + 4) + org + r"\frz" + f"{rot - 32}" + r"\fad(90,140)\p1\bord0\shad0\c"
            + TAPE + r"&\1a&H40&}" + tape(70, 26, seed + 7), 8)
        if sfx: sfx_events.append((t0, sfx))
        return w, h

    def stamp(t0, t1, cx, cy, text, fs=78, rot=-8, sfx="thump"):
        w = tw(text, "Montserrat-900.ttf", fs) * 1.04 + 6 * len(text) + 70
        h = fs * 1.55
        slam = r"\fscx165\fscy165\alpha&HFF&\t(0,70,\alpha&H18&)\t(0,110,\fscx96\fscy96)\t(110,170,\fscx100\fscy100)"
        base = r"\an5\pos(" + f"{cx:.0f},{cy:.0f}" + r")\frz" + f"{rot}" + r"\fad(0,150)" + slam
        add(t0, t1, "{" + base + r"\p1\bord7\shad0\3c" + RED + r"&\1a&HFF&}" + f"m 0 0 l {w:.0f} 0 l {w:.0f} {h:.0f} l 0 {h:.0f}", 9)
        add(t0, t1, "{" + base + r"\bord0\shad0\fnMontserrat Black\fsp6\fs" + str(fs) + r"\c" + RED + "&}" + text, 9)
        if sfx: sfx_events.append((t0, sfx))

    seed = 11
    for g in GRAPHICS:
        t0 = src2out(g["at"])
        if t0 is None: continue
        t1 = min(t0 + g.get("dur", 0), TOTAL)
        k = g["kind"]; seed += 13
        if k == "sfx":
            sfx_events.append((t0, g["sfx"])); continue
        if g.get("sfx"): sfx_events.append((t0, g["sfx"]))
        if k == "hooktext":
            lines = g["lines"]
            y = g.get("y", 450)
            fs_list = [fs for _, fs, _ in lines]
            fonts = [(MARKER, MARKER_N) if fs >= 90 else (HAND, HAND_N) for fs in fs_list]
            w = max(tw(txt, f[0], fs) for (txt, fs, _), f in zip(lines, fonts)) + 90
            h = sum(fs * 1.12 for fs in fs_list) + 40
            cx = 540; x0 = cx - w / 2
            org = r"\org(" + f"{cx},{y + h / 2:.0f}" + ")"
            common = org + r"\frz-2\fad(0,140)"
            add(t0, t1, "{" + r"\an7" + slide(x0, y, 50, 200) + common + r"\p1\bord0" + SH + r"\c" + PAPER + "&}" + torn(w, h, seed, 7, 20), 7)
            yy = y + 20
            for (txt, fs, red), (fname, fn) in zip(lines, fonts):
                yy += fs * 0.56
                add(t0, t1, "{" + r"\an5" + slide(cx, yy, 50, 200) + common + r"\bord0\shad0\fn" + fn + r"\fs" + str(fs)
                    + r"\c" + (RED if red else INK) + "&}" + txt, 8)
                yy += fs * 0.56
            sfx_events.append((t0, "paper"))
        elif k == "price":
            y = g.get("y", 560)
            paper_note(t0, t1, 540, y, [g["text"]], 175, MARKER, MARKER_N, INK, -2, seed, hl=False, sfx="paper")
            stamp(t0 + 0.35, t1, 700, y + 120, g["sub"], fs=46, rot=-9)
        elif k == "spec":
            y = g.get("y0", 620) + 150 * g.get("slot", 0)
            label, val = g["rows"][0]
            lw, vw = tw(label, TYPE, 40), tw(val, MARKER, 96)
            w, h, xr = lw + vw + 110, 112, 1040
            x0 = xr - w
            mv = lambda x, yy: r"\move(" + f"{x + 460:.0f},{yy:.0f},{x:.0f},{yy:.0f},0,220" + ")"
            add(t0, t1, "{" + r"\an7" + mv(x0, y - h / 2) + r"\p1\bord0" + SH + r"\c" + PAPER + r"&\fad(60,150)}" + torn(w, h, seed, 4, 14), 6)
            add(t0, t1, "{" + r"\an4" + mv(x0 + 30, y) + r"\bord0\shad0\fn" + TYPE_N + r"\fs40\c" + GREY + r"&\fad(60,150)}" + label, 7)
            add(t0, t1, "{" + r"\an6" + mv(xr - 30, y - 4) + r"\bord0\shad0\fn" + MARKER_N + r"\fs96\c" + INK + r"&\fad(60,150)}" + val, 7)
        elif k == "chip":
            cy = g.get("y", 300)
            text = g["text"]
            w = tw(text, TYPE, 50) + 90
            org = r"\org(" + f"540,{cy}" + ")"
            add(t0, t1, "{" + r"\an5" + slide(540, cy, 0, 1) + org + r"\frz-3\fad(60,150)\p1\bord0\shad3\4a&HC0&\c" + TAPE
                + r"&\1a&H18&\clip(0,0,0,1920)\t(0,220,\clip(0,0,1080,1920))}" + tape(w, 84, seed), 6)
            add(t0, t1, "{" + r"\an5\pos(540," + f"{cy + 2}" + ")" + org + r"\frz-3\fad(120,150)\bord0\shad0\fn" + TYPE_N
                + r"\fs50\fsp3\c" + INK + "&}" + text, 7)
        elif k in ("stamp", "oops"):
            stamp(t0, t1, g.get("x", 540), g.get("y", 640), g["text"], fs=g.get("fs", 84), rot=g.get("rot", -8),
                  sfx=None if g.get("sfx") else "thump")
        elif k == "name":
            paper_note(t0, t1, 540, g.get("y", 1150), [g["text"]], 64, TYPE, TYPE_N, INK, 2, seed, hl=False, bg=TAG)
        elif k == "tape":
            add(t0, t1, "{" + r"\an5\pos(" + f"{g['x']},{g['y']}" + r")\frz" + str(g.get("rot", 30)) + r"\p1\bord0\shad2\4a&HC8&\c" + TAPE
                + r"&\1a&H28&}" + tape(g.get("w", 150), g.get("h", 44), seed), 9)
        elif k == "receipt":
            # paper form that fills in row by row as the numbers are spoken
            y0 = g.get("y", 1000); rows = g["rows"]; rh = g.get("rh", 80)
            t_end = min(src2out(g["until"]) if g.get("until") else TOTAL, TOTAL)
            w = g.get("w", 880); x0 = 540 - w / 2
            h = 120 + rh * len(rows) + 20
            org = r"\org(" + f"540,{y0 + h / 2:.0f}" + ")"
            common = org + r"\frz" + str(g.get("rot", -1.5))
            add(t0, t_end, "{" + r"\an7" + slide(x0, y0, 40, 200) + common + r"\fad(0,160)\p1\bord0" + SH + r"\c" + PAPER + "&}" + torn(w, h, seed, 6, 18), 5)
            add(t0, t_end, "{" + r"\an4" + slide(x0 + 40, y0 + 62, 40, 200) + common + r"\fad(0,160)\bord0\shad0\fn" + MARKER_N + r"\fs74\c" + INK + "&}" + g["title"], 7)
            add(t0, t_end, "{" + r"\an5" + slide(x0 + w - 60, y0 + 8, 40, 200) + org + r"\frz20\fad(0,160)\p1\bord0\shad0\c" + TAPE + r"&\1a&H40&}" + tape(110, 30, seed + 3), 8)
            for i, row in enumerate(rows):
                at, label, val = row[:3]; style = row[3] if len(row) > 3 else ""
                ta = max(t0, src2out(at)); yy = y0 + 120 + rh * i + rh / 2
                if ta >= t_end: continue
                # faint ruled line under every row from the start (a form waiting to be filled)
                add(t0, t_end, "{" + r"\an7\pos(" + f"{x0 + 36:.0f},{yy + rh / 2 - 6:.0f}" + ")" + common + r"\fad(0,160)\p1\bord0\shad0\c" + GREY
                    + (r"&\1a&H60&}" if style != "total" else r"&\1a&H10&}") + rect(w - 72, 3 if style != "total" else 5), 6)
                fx = r"\fad(120,160)\move(" + "{X}," + f"{yy + 18:.0f}" + ",{X}," + f"{yy:.0f}" + ",0,160)"
                add(ta, t_end, "{" + r"\an4" + fx.replace("{X}", f"{x0 + 40:.0f}") + common + r"\bord0\shad0\fn" + TYPE_N
                    + r"\fs40\c" + (INK if style == "total" else GREY) + "&}" + label, 7)
                if style == "total":
                    vw = tw(val, MARKER, 84)
                    hx = x0 + w - 40 - vw - 8
                    add(ta, t_end, "{" + r"\an7\pos(" + f"{hx:.0f},{yy - 22:.0f}" + ")" + common + r"\clip(" + f"{hx - 10:.0f},0,{hx - 10:.0f},1920)"
                        + r"\t(150,450,\clip(" + f"{hx - 10:.0f},0,{hx + vw + 30:.0f},1920))" + r"\fad(0,160)\p1\bord0\shad0\c" + HILITE + r"&\1a&H20&}" + rect(vw + 16, 46), 6)
                add(ta, t_end, "{" + r"\an6" + fx.replace("{X}", f"{x0 + w - 40:.0f}") + common + r"\bord0\shad0\fn" + MARKER_N
                    + r"\fs" + ("84" if style == "total" else "72") + r"\c" + (RED if style == "total" else INK) + "&}" + val, 7)
                sfx_events.append((ta, "cash" if style == "total" else "click"))
            sfx_events.append((t0, "paper"))
        elif k == "cta":
            ty = g.get("y", 470)
            w, h = paper_note(t0, t1, 540, ty, ["", g["text"], ""], 84, HAND, HAND_N, INK, -2, seed, bg=TAG, sfx="paper")
            add(t0 + 0.3, t1, "{" + r"\an8\pos(" + f"{540 + w / 2 + 40:.0f},{ty - 20:.0f}" + r")\frz-25\fad(150,0)\p1\bord0\shad0\c" + RED
                + r"&\clip(0,0,1080," + f"{ty - 20:.0f}" + r")\t(0,350,\clip(0,0,1080,1920))}" + arrow_down(130, 13), 8)

    if KEYPOINTS_ON:
        for n, (at, dur, txt) in enumerate(KEYPOINTS):
            t0 = src2out(at)
            if t0 is None: continue
            t1 = min(t0 + dur, TOTAL)
            parts = txt.split("*")
            paper_note(t0, t1, 540, 1270, parts, 96, HAND, HAND_N, INK, (-2.5, 2.0)[n % 2], 100 + n * 17)
