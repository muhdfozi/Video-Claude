"""'Showroom' graphics theme (THEME = "showroom") — the user's style inspired by (not copied from) a
TikTok car explainer (ECW GLA35) studied frame by frame.

Ideas taken (structure only): full-screen data CARDS cut in between presenter footage (~40% of the run),
a huge faint background word, a glowing headline over a small letter-spaced kicker, value tiles, line
icons that animate, typewriter kickers, check-lists, framed photos, big lower-third words on footage.

Own identity (different look): night-showroom black with an overhead SPOTLIGHT and a glossy FLOOR with
a horizon line (no red gradient, no neon grid); ONE champagne accent (#E6C07B) + white; Montserrat Black
upright (not italic); OUTLINED Anton ghost word that drifts; a specular LIGHT SWEEP across photos;
champagne corner-tick frames; own icons: segmented loan ring (one segment per year), 1/3 salary ring,
mono odometer, check-list that stamps in. Cards cut in with a short champagne flash + whoosh.

render() writes ASS events and returns (cards, scrims) in output seconds; build.py composites the card
background/photo and the footage scrim (numpy) under the ASS layer.
"""
import math, os
from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
_F = {"mont": os.path.join(HERE, "fonts", "Montserrat-900.ttf"),
      "anton": os.path.join(HERE, "fonts", "Anton.ttf"),
      "mono": "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-ExtraBold.ttf",
      "sans": "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf"}
_cache, _scale = {}, {}


def _ls(path):
    if path not in _scale:
        from fontTools.ttLib import TTFont
        f = TTFont(path); o = f["OS/2"]
        _scale[path] = f["head"].unitsPerEm / (o.usWinAscent + o.usWinDescent)
    return _scale[path]


def tw(text, key, fs, fsp=0):
    path = _F[key]
    k = (path, max(1, round(fs * _ls(path))))
    if k not in _cache: _cache[k] = ImageFont.truetype(path, k[1])
    return _cache[k].getlength(text) + fsp * len(text)


def rrect(w, h, r):
    return (f"m {r} 0 l {w-r} 0 b {w} 0 {w} 0 {w} {r} l {w} {h-r} b {w} {h} {w} {h} {w-r} {h} "
            f"l {r} {h} b 0 {h} 0 {h} 0 {h-r} l 0 {r} b 0 0 0 0 {r} 0")


def rect(x, y, w, h):
    return f"m {x:.1f} {y:.1f} l {x+w:.1f} {y:.1f} l {x+w:.1f} {y+h:.1f} l {x:.1f} {y+h:.1f}"


def arc(cx, cy, r0, r1, a0, a1, steps=None):
    """Filled ring segment between angles a0..a1 (degrees, 0 = top, clockwise)."""
    steps = steps or max(4, int(abs(a1 - a0) / 3))
    pts = []
    for i in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        pts.append((cx + r1 * math.sin(a), cy - r1 * math.cos(a)))
    for i in range(steps, -1, -1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        pts.append((cx + r0 * math.sin(a), cy - r0 * math.cos(a)))
    return "m " + " l ".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def ease_out(x):
    return 1 - (1 - max(0.0, min(1.0, x))) ** 3


def money(v, prefix="RM"):
    return prefix + f"{v:,.0f}"


def render(SR, src2out, add, TOTAL, C, sfx_events, FPS, accent="E6C07B"):
    ACC, WHITE, GREY, DIM, BLACK, INK = C(accent), C("F5F3EE"), C("A7A39B"), C("4A4844"), C("000000"), C("0B0B0E")
    MONT, ANTON, MONO, SANS = r"\fnMontserrat Black", r"\fnAnton", r"\fnJetBrains Mono ExtraBold", r"\fnInter Display SemiBold"
    A7 = r"\an7\pos(0,0)"
    cards, scrims = [], []

    def T(x):
        return src2out(x) if x is not None else None

    def T_end(x):
        """End of a window given in source time: map a point just inside it (a segment end can map elsewhere)."""
        v = src2out(x - 0.04)
        return None if v is None else v + 0.04

    # ------------------------------------------------------------ atoms
    def typewriter(t0, t1, text, x, y, fs=34, fsp=9, col=None, an=5, layer=8, cps=38):
        col = col or ACC
        n = len(text); dt = 1.0 / cps
        for i in range(n):
            a = t0 + i * dt; b = t0 + (i + 1) * dt if i < n - 1 else t1
            if a >= t1: break
            cur = "" if i == n - 1 else r"{\alpha&H40&}▍"
            add(a, min(b, t1), "{" + rf"\an{an}\pos({x:.0f},{y:.0f})" + (r"\fad(0,180)" if i == n - 1 else "") + MONO
                + rf"\fs{fs}\fsp{fsp}\bord0\shad0\c{col}&" + "}" + text[:i + 1] + cur, layer)

    def headline(t0, t1, text, y, fs=150, x=540, an=5, col=None, glow=True, layer=8):
        """Montserrat Black; rises 28px out of a blur; soft champagne glow behind."""
        col = col or WHITE
        parts = text.split("*")
        body = "".join((r"{\c" + ACC + "&}" + p + r"{\c" + col + "&}") if i % 2 else p for i, p in enumerate(parts))
        plain = text.replace("*", "")
        fs = int(min(fs, fs * 960 / max(1, tw(plain, "mont", fs))))          # auto-fit to 960 px
        mv = rf"\move({x:.0f},{y + 28:.0f},{x:.0f},{y:.0f},0,260)"
        if glow:
            add(t0, t1, "{" + rf"\an{an}{mv}\fad(120,180)" + MONT + rf"\fs{fs}\bord10\blur18\shad0\c{ACC}&\3c{ACC}&\alpha&HC8&" + "}" + plain, layer - 1)
        add(t0, t1, "{" + rf"\an{an}{mv}\fad(120,180)\blur6\t(0,220,\blur0)" + MONT + rf"\fs{fs}\bord0\shad0\c{col}&" + "}" + body, layer)

    def underline(t0, t1, y, w=120, x=540):
        add(t0 + 0.15, t1, "{" + A7 + rf"\fad(0,180)\clip({x - w/2:.0f},0,{x - w/2:.0f},1920)\t(0,260,\clip({x - w/2:.0f},0,{x + w/2:.0f},1920))"
            + rf"\p1\bord0\shad0\c{ACC}&" + "}" + rect(x - w / 2, y, w, 6), 8)

    def ghost(t0, t1, word, y=520):
        d = max(0.5, t1 - t0)
        add(t0, t1, "{" + rf"\an5\move(600,{y},470,{y},0,{int(d*1000)})\fad(300,200)" + ANTON
            + rf"\fs470\fsp6\1a&HFF&\bord2.5\3c{ACC}&\3a&HC4&\shad0" + "}" + word.upper(), 3)

    def flash(t0):
        add(t0, t0 + 0.2, "{" + A7 + rf"\p1\bord0\shad0\c{C('FFF3DC')}&\1a&H60&\t(0,180,\1a&HFF&)" + "}" + rect(0, 0, 1080, 1920), 9)

    def counter(t0, t1, to, y, fs=190, dur=1.2, prefix="RM", col=None, x=540, an=5, glow=True, sfx="cash", pre=""):
        col = col or ACC
        n = max(1, int(dur * FPS))
        for i in range(n):
            a, b = t0 + i / FPS, t0 + (i + 1) / FPS
            if a >= t1: break
            v = to * ease_out((i + 1) / n)
            add(a, min(b, t1), "{" + rf"\an{an}\pos({x:.0f},{y:.0f})" + (r"\fad(120,0)" if i == 0 else "") + MONT
                + rf"\fs{fs}\bord0\shad0\c{col}&" + "}" + pre + money(v, prefix), 8)
        if t0 + dur < t1:
            if glow:
                add(t0 + dur, t1, "{" + rf"\an{an}\pos({x:.0f},{y:.0f})\fad(0,180)" + MONT
                    + rf"\fs{fs}\bord8\blur20\shad0\c{col}&\3c{col}&\alpha&HB4&\t(0,250,\alpha&HD8&)" + "}" + pre + money(to, prefix), 7)
            add(t0 + dur, t1, "{" + rf"\an{an}\pos({x:.0f},{y:.0f})\fad(0,180)" + MONT + rf"\fs{fs}\bord0\shad0\c{col}&" + "}" + pre + money(to, prefix), 8)
        if sfx: sfx_events.append((t0, sfx))

    def ticks(t0, t1, x, y, w, h, L=44, th=5, layer=8):
        """Champagne corner ticks around a box (they 'snap' in from 14px outside)."""
        for (cx, cy, sx, sy) in [(x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)]:
            d = 14
            for (rx, ry, rw, rh) in [(0, 0, L, th), (0, 0, th, L)]:
                px = cx + (rx if sx > 0 else -rx - rw) - sx * d
                py = cy + (ry if sy > 0 else -ry - rh) - sy * d
                add(t0, t1, "{" + rf"\an7\move({px:.0f},{py:.0f},{px + sx*d:.0f},{py + sy*d:.0f},0,220)\fad(100,180)\p1\bord0\shad0\c{ACC}&" + "}"
                    + rect(0, 0, rw, rh), layer)

    def frame_line(t0, t1, x, y, w, h):
        add(t0, t1, "{" + A7 + rf"\fad(150,180)\p1\1a&HFF&\bord1.5\3c{ACC}&\3a&H70&\shad0" + "}" + rect(x, y, w, h), 7)

    def chip(t0, t1, text, x, y, an=5, solid=False, fs=38, layer=8):
        w = tw(text, "mono", fs, 4) * 1.02 + 56; h = fs + 34
        x0 = {4: x, 5: x - w / 2, 6: x - w}[an]
        pop = r"\fscx85\fscy85\t(0,160,\fscx100\fscy100)"
        add(t0, t1, "{" + rf"\an5\pos({x0 + w/2:.0f},{y:.0f})\fad(100,180){pop}\p1\shad0"
            + (rf"\bord0\c{ACC}&" if solid else rf"\bord2\c{BLACK}&\1a&H70&\3c{ACC}&") + "}" + rrect(w, h, h / 2), layer)
        add(t0, t1, "{" + rf"\an5\pos({x0 + w/2:.0f},{y + 1:.0f})\fad(100,180){pop}" + MONO
            + rf"\fs{fs}\fsp4\bord0\shad0\c{INK if solid else ACC}&" + "}" + text, layer + 1)
        return w

    def tile(t0, t1, x, y, w, h, lab, val):
        add(t0, t1, "{" + rf"\an7\move({x:.0f},{y + 24:.0f},{x:.0f},{y:.0f},0,240)\fad(140,180)\p1\bord1.5\3c{ACC}&\3a&HA0&\c{C('17171B')}&\1a&H20&\shad0" + "}"
            + rrect(w, h, 18), 6)
        add(t0, t1, "{" + rf"\an7\move({x + 30:.0f},{y + 46:.0f},{x + 30:.0f},{y + 22:.0f},0,240)\fad(140,180)" + MONO + rf"\fs26\fsp6\bord0\shad0\c{GREY}&" + "}" + lab.upper(), 7)
        add(t0, t1, "{" + rf"\an1\move({x + 28:.0f},{y + h - 4:.0f},{x + 28:.0f},{y + h - 28:.0f},0,240)\fad(140,180)" + MONT + rf"\fs62\bord0\shad0\c{WHITE}&" + "}" + val, 7)
        sfx_events.append((t0, "click"))

    def ledger(t0, t1, rows, x, y, w, rh=118, fs_v=66, total=None):
        for i, row in enumerate(rows):
            at, lab, val = row[:3]
            ta = max(t0, T(at)); yy = y + rh * i
            if ta >= t1: continue
            add(t0, t1, "{" + A7 + rf"\fad(150,180)\p1\bord0\shad0\c{ACC}&\1a&HB8&" + "}" + rect(x, yy + rh, w, 2), 6)
            add(ta, t1, "{" + rf"\an4\move({x + 40:.0f},{yy + rh/2:.0f},{x:.0f},{yy + rh/2:.0f},0,220)\fad(120,180)" + SANS + rf"\fs46\bord0\shad0\c{GREY}&" + "}" + lab, 7)
            add(ta, t1, "{" + rf"\an6\move({x + w + 40:.0f},{yy + rh/2:.0f},{x + w:.0f},{yy + rh/2:.0f},0,220)\fad(120,180)" + MONT + rf"\fs{fs_v}\bord0\shad0\c{WHITE}&" + "}" + val, 7)
            sfx_events.append((ta, "click"))

    def ring_segments(t0, t1, cx, cy, n, r0=150, r1=190, step=0.11, lit=None):
        gap = 6
        for i in range(n):
            a0 = i * 360 / n + gap / 2; a1 = (i + 1) * 360 / n - gap / 2
            add(t0, t1, "{" + A7 + rf"\fad(150,180)\p1\bord0\shad0\c{DIM}&" + "}" + arc(cx, cy, r0, r1, a0, a1), 6)
            ta = t0 + 0.25 + i * step
            if ta < t1:
                add(ta, t1, "{" + A7 + rf"\fad(60,180)\p1\bord0\shad0\c{ACC}&" + "}" + arc(cx, cy, r0, r1, a0, a1), 7)
                add(ta, t1, "{" + A7 + rf"\fad(60,180)\p1\bord6\blur10\3c{ACC}&\c{ACC}&\alpha&HD0&\shad0" + "}" + arc(cx, cy, r0, r1, a0, a1), 6)
        sfx_events.append((t0 + 0.25, "riser"))

    def ring_fraction(t0, t1, cx, cy, frac, r0=170, r1=200, dur=0.9):
        add(t0, t1, "{" + A7 + rf"\fad(150,180)\p1\bord0\shad0\c{DIM}&" + "}" + arc(cx, cy, r0, r1, 0, 360, 120), 6)
        n = max(1, int(dur * FPS))
        for i in range(n):
            a, b = t0 + 0.2 + i / FPS, (t0 + 0.2 + (i + 1) / FPS) if i < n - 1 else t1
            if a >= t1: break
            ang = 360 * frac * ease_out((i + 1) / n)
            add(a, min(b, t1), "{" + A7 + (r"\fad(0,180)" if i == n - 1 else "") + rf"\p1\bord0\shad0\c{ACC}&" + "}" + arc(cx, cy, r0 - 6, r1 + 6, 0, ang), 7)
        sfx_events.append((t0 + 0.2, "riser"))

    def checklist(t0, t1, items, x, y, step=132):
        for i, (at, text) in enumerate(items):
            ta = max(t0 + 0.1 * i, T(at)); yy = y + step * i
            if ta >= t1: continue
            add(t0 + 0.06 * i, t1, "{" + rf"\an7\pos({x:.0f},{yy:.0f})\fad(150,180)\p1\bord2.5\3c{GREY}&\1a&HFF&\shad0" + "}" + rrect(64, 64, 12), 6)
            add(t0 + 0.06 * i, ta, "{" + rf"\an4\pos({x + 100:.0f},{yy + 33:.0f})\fad(150,0)" + MONT + rf"\fs60\bord0\shad0\c{DIM}&" + "}" + text, 7)
            add(ta, t1, "{" + rf"\an7\pos({x:.0f},{yy:.0f})\fad(60,180)\p1\bord0\shad0\c{ACC}&" + "}" + rrect(64, 64, 12), 7)
            add(ta, t1, "{" + rf"\an5\pos({x + 32:.0f},{yy + 33:.0f})\fad(0,180)\fscx40\fscy40\t(0,140,\fscx115\fscy115)\t(140,220,\fscx100\fscy100)"
                + rf"\fnDejaVu Sans\b1\fs54\bord0\shad0\c{INK}&" + "}✓", 8)
            add(ta, t1, "{" + rf"\an4\pos({x + 100:.0f},{yy + 33:.0f})\fad(0,180)" + MONT + rf"\fs60\bord0\shad0\c{WHITE}&" + "}" + text, 8)
            sfx_events.append((ta, "ding"))

    def odometer(t0, t1, to, y, suffix="KM", x=540, fs=96, dur=1.0):
        digits = f"{to:,}"
        cw, ch = fs * 0.72, fs * 1.25
        totw = sum(cw if c.isdigit() else cw * 0.45 for c in digits)
        sw = tw(" " + suffix, "mono", 48, 4)
        xx = x - (totw + sw + 20) / 2
        n = max(1, int(dur * FPS))
        for c_i, c in enumerate(digits):
            w = cw if c.isdigit() else cw * 0.45
            if c.isdigit():
                add(t0, t1, "{" + rf"\an7\pos({xx:.0f},{y - ch/2:.0f})\fad(120,180)\p1\bord1.5\3c{ACC}&\3a&H90&\c{C('121215')}&\1a&H30&\shad0" + "}" + rrect(w - 8, ch, 10), 6)
                for i in range(n):
                    a, b = t0 + i / FPS, (t0 + (i + 1) / FPS) if i < n - 1 else t1
                    if a >= t1: break
                    k = len(digits) - c_i
                    d = int(c) if i == n - 1 else (int(c) + (n - i) * (k + 2)) % 10
                    add(a, min(b, t1), "{" + rf"\an5\pos({xx + (w - 8)/2:.0f},{y:.0f})" + (r"\fad(0,180)" if i == n - 1 else "") + MONO
                        + rf"\fs{fs}\bord0\shad0\c{WHITE}&" + "}" + str(d), 7)
            else:
                add(t0, t1, "{" + rf"\an5\pos({xx + w/2 - 4:.0f},{y + fs*0.25:.0f})\fad(120,180)" + MONO + rf"\fs{fs}\bord0\shad0\c{WHITE}&" + "}" + c, 7)
            xx += w
        add(t0, t1, "{" + rf"\an4\pos({xx + 16:.0f},{y + 8:.0f})\fad(120,180)" + MONO + rf"\fs48\fsp4\bord0\shad0\c{ACC}&" + "}" + suffix, 7)
        sfx_events.append((t0, "riser"))

    # ------------------------------------------------------------ full-screen cards
    for cd in SR.get("cards", []):
        a = T(cd["win"][0]); b = T_end(cd["win"][1])
        if a is None: continue
        b = TOTAL if b is None or b <= a else min(b, TOTAL)
        card = dict(a=a, b=b, photo=cd.get("photo"), box=cd.get("box"))
        cards.append(card)
        flash(a); sfx_events.append((a, "whoosh"))
        if cd.get("ghost"): ghost(a, b, cd["ghost"], cd.get("ghost_y", 470))
        ky, hy = cd.get("kicker_y", 230), cd.get("head_y", 330)
        if cd.get("kicker"): typewriter(a + 0.05, b, cd["kicker"].upper(), 540, ky)
        if cd.get("heading"):
            headline(a + 0.12, b, cd["heading"], hy, cd.get("head_fs", 140)); underline(a + 0.12, b, hy + cd.get("head_fs", 140) * 0.55)
            sfx_events.append((a + 0.12, "thump"))
        if cd.get("box"):
            x, y, w, h = cd["box"]
            frame_line(a + 0.2, b, x, y, w, h); ticks(a + 0.2, b, x, y, w, h)
            if cd.get("box_label"): chip(a + 0.5, b, cd["box_label"], x + 30, y + h, an=4, solid=True, fs=30)
        for it in cd.get("items", []):
            k = it["kind"]; st = max(a + 0.2, T(it["at"])) if "at" in it else a + 0.35
            if st >= b: continue
            if k == "counter":
                if it.get("lab"): typewriter(st - 0.15 if st - 0.15 > a else st, b, it["lab"].upper(), 540, it["y"] - it.get("fs", 190) * 0.62 - 30, fs=30, col=GREY)
                counter(st, b, it["to"], it["y"], it.get("fs", 190), it.get("dur", 1.2), pre=it.get("pre", ""))
                if it.get("sub"):
                    add(st + 0.35, b, "{" + rf"\an5\move(540,{it['y'] + it.get('fs', 190)*0.62 + 30:.0f},540,{it['y'] + it.get('fs', 190)*0.62 + 14:.0f},0,220)\fad(150,180)" + MONO
                        + rf"\fs34\fsp3\bord0\shad0\c{GREY}&" + "}" + it["sub"], 8)
            elif k == "tiles":
                for j, (at2, lab, val) in enumerate(it["tiles"]):
                    tt = max(st, T(at2)); col, row = j % 2, j // 2
                    tile(tt, b, 70 + col * 480, it["y"] + row * 190, 460, 170, lab, val)
            elif k == "ledger":
                ledger(st, b, it["rows"], 90, it["y"], 900)
            elif k == "ring":
                ring_segments(st, b, 540, it["y"], it["n"])
                add(st + 0.2, b, "{" + rf"\an5\pos(540,{it['y'] - 14})\fad(150,180)" + MONT + rf"\fs120\bord0\shad0\c{WHITE}&" + "}" + str(it["n"]), 8)
                add(st + 0.3, b, "{" + rf"\an5\pos(540,{it['y'] + 66})\fad(150,180)" + MONO + rf"\fs30\fsp8\bord0\shad0\c{ACC}&" + "}" + it.get("unit", "TAHUN"), 8)
            elif k == "fraction":
                ring_fraction(st, b, 540, it["y"], it["frac"])
                add(st + 0.25, b, "{" + rf"\an5\pos(540,{it['y'] - 10})\fad(150,180)" + MONT + rf"\fs110\bord0\shad0\c{WHITE}&" + "}" + it["text"], 8)
                add(st + 0.35, b, "{" + rf"\an5\pos(540,{it['y'] + 70})\fad(150,180)" + MONO + rf"\fs28\fsp7\bord0\shad0\c{ACC}&" + "}" + it.get("unit", "GAJI"), 8)
            elif k == "chip":
                chip(st, b, it["text"], 540, it["y"], solid=it.get("solid", False), fs=it.get("fs", 38)); sfx_events.append((st, "pop"))
            elif k == "checklist":
                checklist(st, b, it["items"], it.get("x", 150), it["y"])
            elif k == "text":
                add(st, b, "{" + rf"\an5\move(540,{it['y'] + 20},540,{it['y']},0,220)\fad(150,180)" + (MONT if it.get("bold") else SANS)
                    + rf"\fs{it.get('fs', 50)}\bord0\shad0\c{ACC if it.get('accent') else WHITE}&" + "}" + it["text"], 8)
        if cd.get("footer"):
            add(a + 0.3, b, "{" + rf"\an5\pos(540,1790)\fad(150,180)" + MONO + rf"\fs22\fsp5\bord0\shad0\c{DIM}&" + "}" + cd["footer"].upper(), 8)

    # ------------------------------------------------------------ lower-thirds on footage
    LO = sorted(SR.get("lowers", []), key=lambda o: T(o["at"]) or 0)
    for i, lo in enumerate(LO):
        t0 = T(lo["at"])
        if t0 is None: continue
        t1 = T_end(lo["until"]) if lo.get("until") else t0 + lo.get("dur", 2.0)
        t1 = t1 if t1 and t1 > t0 else t0 + lo.get("dur", 2.0)
        if i + 1 < len(LO) and not lo.get("keep"):
            nx = T(LO[i + 1]["at"])
            if nx is not None and nx > t0: t1 = min(t1, nx - 0.02)
        t1 = min(t1, TOTAL)
        if t1 <= t0: continue
        scrims.append((t0, t1))
        y = lo.get("y", 1500)
        if lo.get("kicker"): typewriter(t0, t1, lo["kicker"].upper(), 540, y - lo.get("fs", 124) * 0.5 - 52, fs=32)
        if lo.get("big"):
            headline(t0 + 0.08, t1, lo["big"], y, lo.get("fs", 124)); sfx_events.append((t0 + 0.08, "thump" if lo.get("thump") else "click"))
        if lo.get("counter"):
            cdef = lo["counter"]
            counter(t0 + 0.08, t1, cdef["to"], y, lo.get("fs", 150), cdef.get("dur", 1.2))
        if lo.get("odometer"):
            odometer(t0 + 0.1, t1, lo["odometer"], y, lo.get("suffix", "KM"))
        cy = y + lo.get("fs", 124) * 0.5 + 64
        # chips: one centred row under the big word
        chs = [(c if isinstance(c, tuple) else (None, c, False)) for c in lo.get("chips", [])]
        if chs:
            ws = [tw(c[1], "mono", 36, 4) * 1.02 + 56 for c in chs]; gap = 22
            x = 540 - (sum(ws) + gap * (len(ws) - 1)) / 2
            for j, (at2, txt, solid) in enumerate(chs):
                tt = max(t0 + 0.25 + 0.12 * j, T(at2) if at2 else 0)
                if tt < t1:
                    chip(tt, t1, txt, x, cy, an=4, solid=solid, fs=36); sfx_events.append((tt, "pop"))
                x += ws[j] + gap
        if lo.get("box"):                     # ledger box on footage
            bx, by, bw, bh = 70, y - 90, 940, lo["box_h"]
            add(t0, t1, "{" + rf"\an7\pos({bx},{by})\fad(160,180)\p1\bord0\shad0\c{C('0C0C0F')}&\1a&H38&" + "}" + rrect(bw, bh, 22), 5)
            frame_line(t0, t1, bx, by, bw, bh); ticks(t0, t1, bx, by, bw, bh, L=36, th=4)
            typewriter(t0 + 0.05, t1, lo["box"].upper(), 540, by + 52, fs=30)
            ledger(t0 + 0.2, t1, lo["rows"], bx + 50, by + 96, bw - 100, rh=lo.get("rh", 108), fs_v=60)
    return cards, scrims
