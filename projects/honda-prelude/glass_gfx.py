"""'Glass' graphics theme (THEME = "glass" in an edl.py).

Studied from a minimal case-study reference (BJAK): the presenter's own footage is blurred and washed
to white to make a frosted 'glass' panel for each data chapter; crisp minimal type on top (small
letter-spaced caps labels, big semibold numbers that roll up, white rounded cards, dotted timelines);
between chapters the presenter is full screen with dark translucent pills. One accent colour.

render() writes ASS events and returns the glass windows (output seconds) that build.py uses to
blur/whiten the video frames.
"""

def ease_out(x):
    return 1 - (1 - x) ** 3


def rrect(w, h, r):
    return (f"m {r} 0 l {w-r} 0 b {w} 0 {w} 0 {w} {r} l {w} {h-r} b {w} {h} {w} {h} {w-r} {h} "
            f"l {r} {h} b 0 {h} 0 {h} 0 {h-r} l 0 {r} b 0 0 0 0 {r} 0")


def circle(r):
    k = 0.5523 * r
    return (f"m 0 {-r} b {k} {-r} {r} {-k} {r} 0 b {r} {k} {k} {r} 0 {r} "
            f"b {-k} {r} {-r} {k} {-r} 0 b {-r} {-k} {-k} {-r} 0 {-r}")


def fmt(v, prefix="RM", decimals=0):
    s = f"{v:,.{decimals}f}"
    return prefix + s


def render(GLASS, OVERLAYS, src2out, add, TOTAL, C, sfx_events, FPS, accent="C8102E"):
    INK, GREY, LIGHT, WHITE, BLACK, ACC, ACC_L = (C("1D1D1F"), C("8A8580"), C("B9B4AE"), C("FFFFFF"),
                                                  C("000000"), C(accent), C("FF6B6B"))
    NUM = r"\fnInter Display SemiBold\b0"
    TXT = r"\fnInter Display SemiBold\b0"
    LAB = r"\fnInter\b0"
    FADE = r"\fad(220,200)"
    RISE = lambda x, y, dy=24: r"\move(" + f"{x:.0f},{y + dy:.0f},{x:.0f},{y:.0f},0,260" + ")"
    windows = []

    def label(t0, t1, text, y=420):
        add(t0, t1, "{" + r"\an5\pos(540," + str(y) + ")" + FADE + LAB + r"\fs36\fsp8\bord0\shad0\c" + GREY + "&}" + text.upper(), 7)
        add(t0, t1, "{" + r"\an5\pos(540," + str(y + 34) + ")" + FADE + r"\p1\bord0\shad0\c" + LIGHT + "&}" + "m 0 0 l 70 0 l 70 4 l 0 4", 7)

    def counter(t0, t1, to, frm=0, dur=1.3, y=800, lab=None, sub=None, prefix="RM", fs=170, col=None, pill=False):
        col = col or INK
        if pill:
            add(t0, t1, "{" + r"\an5\pos(540," + f"{y - 10}" + ")" + FADE + r"\p1\bord0\shad0\c" + BLACK + r"&\1a&H60&}" + rrect(700, 250, 34), 6)
        if lab:
            add(t0, t1, "{" + r"\an5\pos(540," + f"{y - 95}" + ")" + FADE + LAB + r"\fs28\fsp7\bord0\shad0\c" + (LIGHT if pill else GREY) + "&}" + lab.upper(), 7)
        n = int(dur * FPS)
        for i in range(n):
            a, b = t0 + i / FPS, t0 + (i + 1) / FPS
            v = frm + (to - frm) * ease_out((i + 1) / n)
            fa = r"\fad(150,0)" if i == 0 else ""
            add(a, b, "{" + r"\an5\pos(540," + str(y) + ")" + fa + NUM + r"\fs" + str(fs) + r"\bord0\shad0\c" + col + "&}" + fmt(v, prefix), 8)
        add(t0 + dur, t1, "{" + r"\an5\pos(540," + str(y) + r")\fad(0,200)" + NUM + r"\fs" + str(fs) + r"\bord0\shad0\c" + col + "&}" + fmt(to, prefix), 8)
        if sub:
            add(t0 + 0.3, t1, "{" + r"\an5\pos(540," + f"{y + 150}" + ")" + FADE + TXT + r"\fs46\bord0\shad" + ("2" if pill else "0")
                + r"\4a&H80&\c" + (WHITE if pill else GREY) + "&}" + sub, 8)
        sfx_events.append((t0, "click"))

    def card(t0, t1, title, rows, y=640):
        """White rounded card; rows (at, label, value[, 'total']) appear when spoken."""
        rh = 132; w = 940; x0 = 540 - w / 2
        h = 40 + rh * len(rows)
        if title: label(t0, t1, title, y - 110)
        add(t0, t1, "{" + r"\an7\pos(" + f"{x0:.0f},{y}" + ")" + FADE + r"\p1\bord0\shad8\4c" + BLACK + r"&\4a&HE6&\c" + WHITE + "&}" + rrect(w, h, 30), 6)
        for i, row in enumerate(rows):
            at, lab, val = row[:3]; total = len(row) > 3 and row[3] == "total"
            ta = max(t0, src2out(at)); yy = y + 20 + rh * i + rh / 2
            if ta >= t1: continue
            if i:
                add(t0, t1, "{" + r"\an7\pos(" + f"{x0 + 36:.0f},{yy - rh / 2:.0f}" + ")" + FADE + r"\p1\bord0\shad0\c" + LIGHT + r"&\1a&H90&}" + rect(w - 72, 2), 6)
            add(ta, t1, "{" + r"\an4" + RISE(x0 + 40, yy, 16) + FADE + TXT + r"\fs50\bord0\shad0\c" + (INK if total else GREY) + "&}" + lab, 7)
            if total and isinstance(val, (int, float)):
                n = int(1.1 * FPS)
                for j in range(n):
                    add(ta + j / FPS, ta + (j + 1) / FPS, "{" + r"\an6\pos(" + f"{x0 + w - 40:.0f},{yy:.0f}" + ")" + NUM + r"\fs76\bord0\shad0\c" + ACC + "&}" + fmt(val * ease_out((j + 1) / n)), 7)
                add(ta + 1.1, t1, "{" + r"\an6\pos(" + f"{x0 + w - 40:.0f},{yy:.0f}" + r")\fad(0,200)" + NUM + r"\fs76\bord0\shad0\c" + ACC + "&}" + fmt(val), 7)
                sfx_events.append((ta, "cash"))
            else:
                add(ta, t1, "{" + r"\an6" + RISE(x0 + w - 40, yy, 16) + FADE + NUM + r"\fs66\bord0\shad0\c" + INK + "&}" + str(val), 7)
                sfx_events.append((ta, "click"))

    def rect(w, h):
        return f"m 0 0 l {w} 0 l {w} {h} l 0 {h}"

    def timeline(t0, t1, rows, y=700, step=200, x=290):
        """Dotted vertical timeline; rows (at, text, sub[, accent_at])."""
        for i, row in enumerate(rows):
            at, text, sub = row[:3]
            ta = max(t0, src2out(at)); yy = y + step * i
            if ta >= t1: continue
            if i:
                add(ta, t1, "{" + r"\an7\pos(" + f"{x - 2},{yy - step + 30}" + ")" + FADE + r"\p1\bord0\shad0\c" + LIGHT
                    + r"&\clip(0,0,1080," + f"{yy - step + 22}" + r")\t(0,300,\clip(0,0,1080,1920))}" + rect(5, step - 60), 6)
            acc_at = row[3] if len(row) > 3 else None
            ty = max(ta, src2out(acc_at)) if acc_at else None
            for (a, b, col) in ([(ta, ty, INK), (ty, t1, ACC)] if ty and ty < t1 else [(ta, t1, INK)]):
                add(a, b, "{" + r"\an5\pos(" + f"{x},{yy}" + ")" + (FADE if a == ta else r"\fad(0,200)") + r"\p1\bord0\shad0\c" + col + "&}" + circle(15), 7)
                add(a, b, "{" + r"\an4" + (RISE(x + 44, yy, 14) if a == ta else r"\pos(" + f"{x + 44},{yy}" + ")") + (FADE if a == ta else r"\fad(0,200)")
                    + TXT + r"\fs92\bord0\shad0\c" + col + "&}" + text, 7)
            if sub:
                add(ta + 0.15, t1, "{" + r"\an4\pos(" + f"{x + 44},{yy + 66}" + ")" + FADE + LAB + r"\fs42\bord0\shad0\c" + GREY + "&}" + sub, 7)
            sfx_events.append((ta, "click"))

    def cards(t0, t1, items, y=640, gap=26):
        """Stacked numbered cards; the newest is bright, older ones fade back."""
        ch = 184; w = 940; x0 = 540 - w / 2
        times = [max(t0, src2out(it[0])) for it in items]
        for i, (at, tag, text) in enumerate(items):
            ta = times[i]; yy = y + (ch + gap) * i
            if ta >= t1: continue
            tn = times[i + 1] if i + 1 < len(items) else t1
            for (a, b, bright) in [(ta, tn, True), (tn, t1, False)]:
                if b <= a: continue
                f = FADE if a == ta else r"\fad(0,200)"
                mv = RISE(x0, yy, 30) if a == ta else r"\pos(" + f"{x0:.0f},{yy}" + ")"
                add(a, b, "{" + r"\an7" + mv + f + r"\p1\bord0\shad8\4c" + BLACK + r"&\4a&HE8&\c" + WHITE + (r"&\1a&H00&" if bright else r"&\1a&H70&") + "}" + rrect(w, ch, 26), 6)
                mv2 = lambda xx, yy2: (RISE(xx, yy2, 30) if a == ta else r"\pos(" + f"{xx:.0f},{yy2:.0f}" + ")")
                add(a, b, "{" + r"\an7" + mv2(x0 + 36, yy + 26) + f + LAB + r"\fs32\fsp6\bord0\shad0\c" + (ACC if bright else LIGHT) + "&}" + tag.upper(), 7)
                add(a, b, "{" + r"\an7" + mv2(x0 + 40, yy + 78) + f + TXT + r"\fs62\bord0\shad0\c" + (INK if bright else LIGHT) + "&}" + text, 7)
            sfx_events.append((ta, "click"))

    # ---- glass chapters
    for g in GLASS:
        a, b = src2out(g["win"][0]), src2out(g["win"][1], prefer_next=True)
        if a is None: continue
        b = TOTAL if b is None or b <= a else min(b, TOTAL)
        windows.append((a, b))
        sfx_events.append((a, "soft"))
        t0 = a + 0.25
        for it in g["items"]:
            k = it["kind"]
            st = max(t0, src2out(it["at"])) if "at" in it else t0
            if k == "label": label(st, b, it["text"], it.get("y", 420))
            elif k == "counter": counter(st, b, it["to"], it.get("frm", 0), it.get("dur", 1.3), it.get("y", 900), it.get("lab"), it.get("sub"),
                                         it.get("prefix", "RM"), it.get("fs", 170), ACC if it.get("accent") else None)
            elif k == "card": card(st, b, it.get("title"), it["rows"], it.get("y", 640))
            elif k == "timeline": timeline(st, b, it["rows"], it.get("y", 700))
            elif k == "cards": cards(st, b, it["items"], it.get("y", 640))

    # ---- overlays on the full-screen presenter
    for o in OVERLAYS:
        t0 = src2out(o["at"]); t1 = min(t0 + o.get("dur", 2.0), TOTAL)
        k = o["kind"]
        if k == "counter_pill":
            counter(t0, t1, o["to"], o.get("frm", 0), o.get("dur_roll", 1.2), o.get("y", 1430), o.get("lab"), o.get("sub"),
                    o.get("prefix", "RM"), o.get("fs", 120), WHITE, pill=True)
        elif k == "title":
            w = 620
            add(t0, t1, "{" + r"\an5\pos(540,1380)\fad(120,200)\fscx80\fscy80\t(0,200,\fscx100\fscy100)\p1\bord0\shad0\c" + INK + "&}" + rrect(w, 150, 18), 7)
            add(t0, t1, "{" + r"\an5\pos(540,1380)\fad(120,200)\fscx80\fscy80\t(0,200,\fscx100\fscy100)" + NUM + r"\fs92\bord0\shad0\c" + WHITE + "&}" + o["chip"], 8)
            add(t0 + 0.15, t1, "{" + r"\an5\pos(540,1525)\fad(120,200)" + NUM + r"\fs72\bord3\3c" + BLACK + r"&\3a&H90&\shad0\c" + ACC_L + "&}" + o["accent"], 8)
            sfx_events.append((t0, "pop"))
        elif k == "pill":
            parts = o["text"].split("*")
            body = "".join((r"{\c" + ACC_L + "&}" + p + r"{\c" + WHITE + "&}") if i % 2 else p for i, p in enumerate(parts))
            from PIL import ImageFont
            fnt = ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf", 56)
            w = fnt.getlength(o["text"].replace("*", "")) * 0.78 + 90
            y = o.get("y", 1470)
            add(t0, t1, "{" + r"\an5\pos(540," + str(y) + r")\fad(160,200)\p1\bord0\shad0\c" + BLACK + r"&\1a&H60&}" + rrect(w, 100, 50), 7)
            add(t0, t1, "{" + r"\an5" + RISE(540, y, 12) + r"\fad(160,200)" + TXT + r"\fs56\bord0\shad0\c" + WHITE + "&}" + body, 8)
            sfx_events.append((t0, "click"))
    return windows
