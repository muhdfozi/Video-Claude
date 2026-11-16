#!/usr/bin/env python3
"""Neon line-art scene library for the "Alphard Bukan Untuk Orang Kaya Je" video.

Look: black background, fluorescent-green (#39FF14) glowing line art, white
captions with green keywords, Formula1 font. Every scene is a function of local
progress p (0..1) so the same code renders storyboard stills and the final
animation.

Storyboard:  python3 neon_scenes.py --font F1.ttf --raw RAW.mov --outdir DIR
"""
import argparse
import math
import os
import subprocess

import cairo
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
GREEN = np.array([57, 255, 20], np.float32)        # #39FF14
CORE = np.array([225, 255, 215], np.float32)       # hot core of the neon tube
BG = np.array([10, 10, 10], np.float32)            # #0A0A0A
WHITE = (255, 255, 255)
GREEN_T = (57, 255, 20)

HEADER_LABEL = "ALPHARD Z 2024"
HEADER_TITLE = "Bukan Untuk Orang Kaya Je"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def seg(p, a, b):
    """local 0..1 progress of p inside [a, b]"""
    return clamp((p - a) / (b - a)) if b > a else float(p >= a)


def ease(x):
    return 1 - (1 - x) ** 3


def ease_io(x):
    return x * x * (3 - 2 * x)


class Neon:
    """Cairo surface that collects line art as an intensity mask."""

    def __init__(self):
        self.surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        self.c = cairo.Context(self.surf)
        self.c.set_line_cap(cairo.LINE_CAP_ROUND)
        self.c.set_line_join(cairo.LINE_JOIN_ROUND)
        self.c.select_font_face("Formula1", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)

    def stroke(self, a=1.0, w=6):
        self.c.set_source_rgba(1, 1, 1, clamp(a))
        self.c.set_line_width(w)
        self.c.stroke()

    def fill(self, a=1.0):
        self.c.set_source_rgba(1, 1, 1, clamp(a))
        self.c.fill()

    def mask(self):
        buf = np.ndarray((H, W, 4), np.uint8, self.surf.get_data())
        return buf[..., 3].astype(np.float32) / 255.0


def glow(mask):
    """mask (H,W) 0..1 -> RGB float neon (additive layer)."""
    small = cv2.resize(mask, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    g1 = cv2.GaussianBlur(mask, (0, 0), 5)
    g2 = cv2.resize(cv2.GaussianBlur(small, (0, 0), 5), (W, H))
    g3 = cv2.resize(cv2.GaussianBlur(small, (0, 0), 14), (W, H))
    halo = np.clip(g1 * 1.1 + g2 * 0.9 + g3 * 0.7, 0, 1.5)
    core = np.clip(mask * 1.2, 0, 1)
    return halo[..., None] * GREEN * 0.85 + core[..., None] * CORE


_BG_CACHE = {}


def background(seed=3):
    if seed in _BG_CACHE:
        return _BG_CACHE[seed].copy()
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.47) / H) ** 2)
    v = np.clip(1 - d * 1.6, 0, 1) ** 2
    img = BG[None, None, :] + v[..., None] * np.array([6, 16, 6], np.float32)
    _BG_CACHE[seed] = img
    return img.copy()


def particles(n, t, seed=11, a=0.5):
    """Slow-drifting green dust: list of (x, y, r, alpha)."""
    rng = np.random.default_rng(seed)
    xs, ys = rng.uniform(0, W, n), rng.uniform(0, H, n)
    sp, ph = rng.uniform(8, 25, n), rng.uniform(0, 6.28, n)
    out = []
    for i in range(n):
        y = (ys[i] - sp[i] * t) % H
        x = xs[i] + 10 * math.sin(t * 0.6 + ph[i])
        out.append((x, y, rng.uniform(1.2, 2.6), a * (0.5 + 0.5 * math.sin(t * 2 + ph[i]))))
    return out


# ---------------------------------------------------------------------------
# primitives (y-down cairo coordinates)
# ---------------------------------------------------------------------------
def car(n, cx, gy, s=1.0, a=1.0, door=0.0, seats=0.0, wheel_rot=0.0, draw=1.0):
    """Stylised MPV side profile facing right. cx = centre x, gy = ground y.
    door: sliding-door opening 0..1, seats: interior seat glow 0..1,
    draw: 0..1 line-reveal (dash offset trick)."""
    c = n.c
    L = 780
    ox = cx - L * s / 2

    def P(x, h):
        return ox + x * s, gy - h * s

    lw = 6 * s
    # body outline (with wheel arches)
    c.new_path()
    c.move_to(*P(70, 38))
    c.line_to(*P(80, 38))
    c.arc_negative(*P(165, 70), 88 * s, math.radians(165), math.radians(15))
    c.line_to(*P(250, 38))
    c.line_to(*P(540, 38))
    c.arc_negative(*P(625, 70), 88 * s, math.radians(165), math.radians(15))
    c.line_to(*P(745, 38))
    c.curve_to(*P(770, 40), *P(776, 60), *P(776, 95))     # front bumper
    c.line_to(*P(772, 170))
    c.curve_to(*P(770, 195), *P(755, 205), *P(735, 210))   # nose
    c.line_to(*P(668, 228))                                # short hood
    c.curve_to(*P(640, 236), *P(625, 250), *P(612, 270))   # windscreen base
    c.line_to(*P(548, 345))                                # windscreen
    c.curve_to(*P(538, 356), *P(525, 358), *P(505, 358))
    c.line_to(*P(70, 352))                                 # roof
    c.curve_to(*P(40, 350), *P(26, 335), *P(24, 300))      # rear roof corner
    c.line_to(*P(20, 120))                                 # tailgate
    c.curve_to(*P(19, 70), *P(30, 40), *P(70, 38))
    c.close_path()
    _reveal_stroke(n, a, lw, draw)

    # glasshouse
    c.new_path()
    c.move_to(*P(44, 240))
    c.line_to(*P(44, 312))
    c.curve_to(*P(44, 330), *P(56, 336), *P(76, 336))
    c.line_to(*P(500, 340))
    c.line_to(*P(588, 250))
    c.line_to(*P(588, 240))
    c.close_path()
    _reveal_stroke(n, a * 0.9, lw * 0.8, draw)
    # pillars
    for x in (250, 452):
        c.new_path()
        c.move_to(*P(x, 240))
        c.line_to(*P(x, 338))
        _reveal_stroke(n, a * 0.9, lw * 0.8, draw)

    # character line + front door seam + headlight + grille
    c.new_path()
    c.move_to(*P(40, 170))
    c.curve_to(*P(300, 178), *P(560, 182), *P(740, 176))
    _reveal_stroke(n, a * 0.55, lw * 0.6, draw)
    c.new_path()
    c.move_to(*P(452, 240))
    c.line_to(*P(456, 70))
    _reveal_stroke(n, a * 0.7, lw * 0.6, draw)
    c.new_path()
    c.move_to(*P(700, 200))
    c.line_to(*P(764, 186))
    _reveal_stroke(n, a, lw * 1.2, draw)
    for k in range(3):
        c.new_path()
        c.move_to(*P(774 - k * 2, 160 - k * 26))
        c.line_to(*P(760 - k * 2, 160 - k * 26))
        _reveal_stroke(n, a * 0.6, lw * 0.5, draw)

    # interior seats (cut-away glow)
    if seats > 0:
        for i, x in enumerate((90, 180, 300, 390, 500)):
            k = clamp(seats * 5 - i)
            if k <= 0:
                continue
            c.new_path()
            c.move_to(*P(x, 250))
            c.curve_to(*P(x - 6, 300), *P(x + 4, 322), *P(x + 18, 324))
            c.line_to(*P(x + 30, 260))
            c.line_to(*P(x + 70, 255))
            _reveal_stroke(n, a * 0.8 * k, lw * 0.8, 1)

    # sliding door: closed seam at 250..452, slides back when opening
    off = -175 * ease_io(door)
    c.new_path()
    c.move_to(*P(250 + off, 236))
    c.line_to(*P(250 + off, 62))
    c.line_to(*P(452 + off, 62))
    c.line_to(*P(452 + off, 236))
    _reveal_stroke(n, a * (0.7 if door == 0 else 0.95), lw * 0.7, draw)
    c.new_path()
    c.move_to(*P(420 + off, 205))
    c.line_to(*P(440 + off, 205))
    _reveal_stroke(n, a, lw * 0.7, draw)
    if door > 0:  # rail + opening glow
        c.new_path()
        c.move_to(*P(60, 228))
        c.line_to(*P(250, 228))
        _reveal_stroke(n, a * 0.6 * door, lw * 0.5, 1)
        c.rectangle(*P(258 + off * 0 , 236), 186 * s * door, 170 * s)
        n.fill(0.06 * door)

    # wheels
    for wx in (165, 625):
        x, y = P(wx, 70)
        c.new_path()
        c.arc(x, y, 64 * s, 0, 2 * math.pi)
        _reveal_stroke(n, a, lw, draw)
        c.new_path()
        c.arc(x, y, 34 * s, 0, 2 * math.pi)
        _reveal_stroke(n, a * 0.7, lw * 0.6, draw)
        for k in range(5):
            ang = wheel_rot + k * 2 * math.pi / 5
            c.new_path()
            c.move_to(x + math.cos(ang) * 10 * s, y + math.sin(ang) * 10 * s)
            c.line_to(x + math.cos(ang) * 32 * s, y + math.sin(ang) * 32 * s)
            _reveal_stroke(n, a * 0.5, lw * 0.4, draw)


def _reveal_stroke(n, a, lw, draw):
    c = n.c
    if draw < 1:
        # dash-reveal along path length
        path = c.copy_path_flat()
        length, last, first = 0.0, None, None
        for typ, pts in path:
            if typ == cairo.PATH_MOVE_TO:
                last = first = pts
            elif typ == cairo.PATH_LINE_TO:
                length += math.dist(last, pts)
                last = pts
            elif typ == cairo.PATH_CLOSE_PATH and first:
                length += math.dist(last, first)
        c.set_dash([length * draw + 0.01, length + 10])
    n.stroke(a, lw)
    c.set_dash([])


def person(n, x, gy, s=1.0, a=1.0, kind="adult", walk=0.0):
    """Rounded line-icon person (not a stick figure). kind: adult/child/elder."""
    c = n.c
    if kind == "child":
        s *= 0.68
    bend = 0.0 if kind != "elder" else 0.28
    hy = gy - 250 * s
    hx = x + bend * 60 * s
    # head
    c.new_path()
    c.arc(hx, hy, 30 * s, 0, 2 * math.pi)
    n.stroke(a, 6 * s)
    # body: rounded capsule torso
    c.new_path()
    tx, ty = x + bend * 40 * s, gy - 205 * s
    c.move_to(tx - 42 * s, ty + 95 * s)
    c.line_to(tx - 42 * s, ty + 18 * s)
    c.curve_to(tx - 42 * s, ty - 4 * s, tx - 22 * s, ty - 8 * s, tx, ty - 8 * s)
    c.curve_to(tx + 22 * s, ty - 8 * s, tx + 42 * s, ty - 4 * s, tx + 42 * s, ty + 18 * s)
    c.line_to(tx + 42 * s, ty + 95 * s)
    n.stroke(a, 6 * s)
    # legs
    sw = math.sin(walk * 2 * math.pi) * 14 * s
    for dx, sg in ((-16, 1), (16, -1)):
        c.new_path()
        c.move_to(tx + dx * s, ty + 100 * s)
        c.line_to(x + dx * s + sg * sw, gy)
        n.stroke(a, 6 * s)
    if kind == "elder":  # cane
        c.new_path()
        c.move_to(tx + 70 * s, ty + 40 * s)
        c.curve_to(tx + 70 * s, ty + 20 * s, tx + 52 * s, ty + 20 * s, tx + 52 * s, ty + 36 * s)
        c.move_to(tx + 70 * s, ty + 40 * s)
        c.line_to(tx + 74 * s, gy)
        n.stroke(a, 5 * s)


def pill(n, cx, cy, text, size=34, a=1.0, strike=0.0, filled=False):
    c = n.c
    c.set_font_size(size)
    ext = c.text_extents(text)
    w, h = ext.width + size * 1.4, size * 1.9
    x, y = cx - w / 2, cy - h / 2
    r = h / 2
    c.new_path()
    c.arc(x + r, y + r, r, math.pi / 2, 3 * math.pi / 2)
    c.arc(x + w - r, y + r, r, -math.pi / 2, math.pi / 2)
    c.close_path()
    if filled:
        n.fill(a * 0.25)
        c.new_path()
        c.arc(x + r, y + r, r, math.pi / 2, 3 * math.pi / 2)
        c.arc(x + w - r, y + r, r, -math.pi / 2, math.pi / 2)
        c.close_path()
    n.stroke(a, 4)
    c.move_to(cx - ext.width / 2 - ext.x_bearing, cy - ext.height / 2 - ext.y_bearing)
    c.show_text(text)
    n.fill(a)
    if strike > 0:
        c.new_path()
        c.move_to(x - 10, cy + 8)
        c.line_to(x - 10 + (w + 20) * strike, cy - 8)
        n.stroke(a * 1.2, 7)


def ground(n, y, a=0.35, x0=140, x1=940):
    n.c.new_path()
    n.c.move_to(x0, y)
    n.c.line_to(x1, y)
    n.stroke(a, 2)


def spotlight(frame, cx, top, bottom, width, a):
    """soft additive light cone (drawn directly on the RGB frame)."""
    if a <= 0:
        return
    m = np.zeros((H, W), np.float32)
    pts = np.array([[cx - 40, top], [cx + 40, top], [cx + width / 2, bottom], [cx - width / 2, bottom]], np.int32)
    cv2.fillConvexPoly(m, pts, 1.0)
    for k in range(-3, 4):  # rays
        x = cx + k * width / 8
        cv2.line(m, (int(cx + k * 8), top), (int(x), bottom), 1.6, 6, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), 18)
    yy = np.linspace(0, 1, H)[:, None]
    fade = np.clip((yy * H - top) / (bottom - top), 0, 1) ** 0.7
    m *= (1 - fade * 0.55)
    frame += (m * a)[..., None] * np.array([40, 90, 35], np.float32)


# ---------------------------------------------------------------------------
# text overlay (PIL, Formula1)
# ---------------------------------------------------------------------------
class Typo:
    def __init__(self, font_path):
        self.fp = font_path
        self.cache = {}

    def font(self, size):
        if size not in self.cache:
            self.cache[size] = ImageFont.truetype(self.fp, size)
        return self.cache[size]


def draw_text_layer(typo, items):
    """items: list of dicts {kind, ...}. Returns RGBA PIL image."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for it in items:
        a = int(255 * clamp(it.get("a", 1.0)))
        if a <= 0:
            continue
        if it["kind"] == "header":
            f1, f2 = typo.font(30), typo.font(58)
            lab = " ".join(it["label"])  # letter-spacing
            w1 = d.textlength(lab, font=f1)
            d.text(((W - w1) / 2, 250), lab, font=f1, fill=GREEN_T + (a,))
            w2 = d.textlength(it["title"], font=f2)
            d.text(((W - w2) / 2, 298), it["title"], font=f2, fill=WHITE + (a,))
            # divider: two short lines + small green capsule
            cy = 400
            d.line([(W / 2 - 150, cy), (W / 2 - 34, cy)], fill=WHITE + (int(a * 0.5),), width=2)
            d.line([(W / 2 + 34, cy), (W / 2 + 150, cy)], fill=WHITE + (int(a * 0.5),), width=2)
            d.rounded_rectangle([W / 2 - 22, cy - 5, W / 2 + 22, cy + 5], radius=5, fill=GREEN_T + (a,))
        elif it["kind"] == "caption":
            _caption(d, typo, it["text"], it.get("y", 1390), a, it.get("size", 52))
        elif it["kind"] == "chip":
            f = typo.font(it.get("size", 40))
            tw = d.textlength(it["text"], font=f)
            x, y = it["x"] - tw / 2 - 30, it["y"]
            d.rounded_rectangle([x, y, x + tw + 60, y + 78], radius=39, fill=(10, 10, 10, int(a * 0.85)),
                                outline=GREEN_T + (a,), width=4)
            d.text((x + 30, y + 16), it["text"], font=f, fill=WHITE + (a,))
        elif it["kind"] == "cta":
            f = typo.font(56)
            txt = it["text"]
            tw = d.textlength(txt, font=f)
            sc = it.get("scale", 1.0)
            bw, bh = (tw + 110) * sc, 112 * sc
            x, y = W / 2 - bw / 2, it["y"]
            d.rounded_rectangle([x, y, x + bw, y + bh], radius=bh / 2, fill=GREEN_T + (a,))
            fs = typo.font(max(10, int(56 * sc)))
            tw2 = d.textlength(txt, font=fs)
            d.text((W / 2 - tw2 / 2, y + bh / 2 - 34 * sc), txt, font=fs, fill=(10, 10, 10, a))
            if it.get("sub"):
                f2 = typo.font(34)
                w2 = d.textlength(it["sub"], font=f2)
                d.text((W / 2 - w2 / 2, y + bh + 24), it["sub"], font=f2, fill=WHITE + (a,))
    return img


def _caption(d, typo, text, y, a, size):
    """'Ramai ingat *orang kaya* je' -> white + green keywords, wrapped to 2-3 lines."""
    f = typo.font(size)
    words, hl = [], False
    for tok in text.split():
        if tok.startswith("*"):
            hl, tok = True, tok[1:]
        end = tok.endswith("*") or tok.endswith("*,") or tok.endswith("*.")
        clean = tok.replace("*", "")
        words.append((clean, hl))
        if end:
            hl = False
    space = d.textlength(" ", font=f)
    max_w = 900
    lines, cur, cw = [], [], 0
    for w, h_ in words:
        ww = d.textlength(w, font=f)
        if cur and cw + space + ww > max_w:
            lines.append((cur, cw))
            cur, cw = [], 0
        cw = ww if not cur else cw + space + ww
        cur.append((w, h_))
    lines.append((cur, cw))
    lh = int(size * 1.32)
    y0 = y - (len(lines) * lh) / 2
    for i, (ln, lw) in enumerate(lines):
        x = (W - lw) / 2
        for w, h_ in ln:
            col = GREEN_T if h_ else WHITE
            # subtle dark shadow for legibility on footage
            d.text((x + 3, y0 + i * lh + 4), w, font=f, fill=(0, 0, 0, int(a * 0.6)))
            d.text((x, y0 + i * lh), w, font=f, fill=col + (a,),
                   stroke_width=3, stroke_fill=(0, 0, 0, int(a * 0.85)))
            x += d.textlength(w, font=f) + space


def composite(base_rgb, neon_mask, text_rgba):
    out = base_rgb
    if neon_mask is not None:
        out = out + glow(neon_mask)
    out = np.clip(out, 0, 255)
    if text_rgba is not None:
        t = np.asarray(text_rgba).astype(np.float32)
        al = t[..., 3:4] / 255.0
        out = t[..., :3] * al + out * (1 - al)
    return out.astype(np.uint8)


# ---------------------------------------------------------------------------
# footage panels
# ---------------------------------------------------------------------------
def grade_footage(rgb):
    """slight contrast/desaturate + bottom fade to black for captions."""
    f = rgb.astype(np.float32)
    lum = f.mean(axis=2, keepdims=True)
    f = lum + (f - lum) * 0.85
    f = (f - 128) * 1.08 + 122
    yy = np.linspace(0, 1, H)[:, None, None]
    shade = np.clip((yy - 0.5) / 0.38, 0, 1) ** 1.2 * 0.82
    top = np.clip((0.27 - yy) / 0.27, 0, 1) ** 0.8 * 0.72
    f = f * (1 - shade - top)
    return np.clip(f, 0, 255)


def ring_reveal(bg_frame, footage, p, n):
    """Green ring that grows from the centre revealing footage inside it."""
    r = 40 + ease_io(p) * 1150
    cx, cy = W / 2, H * 0.48
    m = np.zeros((H, W), np.float32)
    cv2.circle(m, (int(cx), int(cy)), int(r), 1.0, -1, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), 1.5)[..., None]
    out = footage * m + bg_frame * (1 - m)
    n.c.new_path()
    n.c.arc(cx, cy, r, 0, 2 * math.pi)
    n.stroke(1.0 - 0.6 * p, 7)
    return out


# ---------------------------------------------------------------------------
# scenes: each returns (rgb_float_frame, neon Neon, text items)
# ---------------------------------------------------------------------------
GY = 1130  # ground line for illustrations


def scene_hook(p, t):
    n = Neon()
    f = background()
    ground(n, GY)
    car(n, W / 2, GY, 1.0, draw=ease(seg(p, 0, 0.45)))
    k = ease(seg(p, 0.35, 0.55))
    pill(n, W / 2, GY - 470 - 20 * (1 - k), "ORANG KAYA?", 40, a=k)
    for x, y, r, a in particles(40, t):
        n.c.arc(x, y, r, 0, 6.3); n.fill(a * 0.6)
    return f, n, "Ramai ingat Alphard ni kereta *orang kaya* je."


def scene_twist(p, t):
    n = Neon()
    f = background()
    spotlight(f, W / 2, 470, GY + 20, 900, ease(seg(p, 0.2, 0.6)))
    ground(n, GY)
    car(n, W / 2, GY, 1.0)
    strike = ease(seg(p, 0.0, 0.25))
    fade = 1 - 0.75 * seg(p, 0.3, 0.6)
    pill(n, W / 2, GY - 490, "ORANG KAYA?", 40, a=fade, strike=strike)
    k = ease(seg(p, 0.45, 0.7))
    pill(n, W / 2, GY - 600, "YANG MEMERLUKAN", 40, a=k, filled=True)
    for x, y, r, a in particles(40, t):
        n.c.arc(x, y, r, 0, 6.3); n.fill(a * 0.6)
    return f, n, "Sebenarnya, Alphard ni untuk orang yang *betul-betul memerlukan*."


def scene_family(p, t):
    n = Neon()
    f = background()
    ground(n, GY)
    car(n, W / 2 + 120, GY, 0.82, seats=seg(p, 0.15, 0.95))
    family = [("elder", 0.62), ("adult", 0.78), ("adult", 0.8), ("child", 0.8), ("child", 0.8)]
    for i, (kind, sc) in enumerate(family):
        k = ease(seg(p, i * 0.12, i * 0.12 + 0.35))
        x = 62 + i * 66 + 40 * (1 - k)
        person(n, x, GY, sc * 0.9, a=k * (1 - 0.6 * seg(p, 0.85, 1.0)), kind=kind, walk=t * 1.5 + i * 0.3)
    k = ease(seg(p, 0.55, 0.75))
    pill(n, W / 2 + 120, GY - 430, "SEMUA MUAT", 38, a=k)
    for x, y, r, a in particles(40, t):
        n.c.arc(x, y, r, 0, 6.3); n.fill(a * 0.6)
    return f, n, "Contohnya *keluarga besar.* Anak ramai, bawa mak ayah sekali, *semua muat, semua selesa.*"


def scene_door(p, t):
    n = Neon()
    f = background()
    ground(n, GY)
    door = ease_io(seg(p, 0.1, 0.5))
    car(n, W / 2 + 130, GY, 0.86, door=door)
    # elder walks towards the opening
    k = ease(seg(p, 0.45, 1.0))
    person(n, 70 + 70 * k, GY, 0.72, kind="elder", walk=t * 1.2)
    # motion chevrons on the door
    if 0.1 < p < 0.6:
        for j in range(3):
            x = W / 2 + 130 - 95 - j * 34 - 140 * door
            n.c.new_path()
            n.c.move_to(x + 12, GY - 200)
            n.c.line_to(x, GY - 185)
            n.c.line_to(x + 12, GY - 170)
            n.stroke(0.8 - j * 0.25, 5)
    pill(n, W / 2 + 130, GY - 420, "PINTU AUTO", 38, a=ease(seg(p, 0.25, 0.45)))
    for x, y, r, a in particles(40, t):
        n.c.arc(x, y, r, 0, 6.3); n.fill(a * 0.6)
    return f, n, "Mak ayah dah berusia? Pintu belakang *buka sendiri*, tak payah tarik pintu berat."


def scene_trip(p, t):
    n = Neon()
    f = background()
    # road with moving dashes
    ground(n, GY, 0.5, 0, W)
    off = (t * 420) % 160
    for i in range(-1, 9):
        x = i * 160 - off
        n.c.new_path(); n.c.move_to(x, GY + 60); n.c.line_to(x + 80, GY + 60)
        n.stroke(0.45, 5)
    bob = math.sin(t * 9) * 2
    car(n, W / 2, GY + bob, 0.9, wheel_rot=t * 12)
    # speed lines
    for j, yy in enumerate((GY - 260, GY - 180, GY - 100)):
        x = 90 - (t * 300 + j * 80) % 60
        n.c.new_path(); n.c.move_to(x, yy); n.c.line_to(x + 70 - j * 15, yy)
        n.stroke(0.5, 4)
    # roof monitor call-out
    k = ease(seg(p, 0.3, 0.55))
    if k > 0:
        bx, by = W / 2 - 40, GY - 530
        n.c.new_path()
        n.c.rectangle(bx - 150, by - 90, 300, 180)
        n.stroke(k, 6)
        n.c.new_path(); n.c.move_to(bx, by + 90); n.c.line_to(bx - 30, GY - 330)
        n.stroke(k * 0.5, 3)
        # play icon pulses
        pul = 0.7 + 0.3 * math.sin(t * 6)
        n.c.new_path(); n.c.move_to(bx - 25, by - 35); n.c.line_to(bx + 35, by); n.c.line_to(bx - 25, by + 35)
        n.c.close_path(); n.fill(k * pul)
        pill(n, bx, by - 135, "ROOF MONITOR", 32, a=k)
    for x, y, r, a in particles(40, t):
        n.c.arc(x, y, r, 0, 6.3); n.fill(a * 0.6)
    return f, n, "Balik kampung jauh? Anak-anak duduk belakang, ada *roof monitor*, tak bosan sepanjang jalan."


def scene_price(p, t):
    n = Neon()
    f = background()
    ground(n, GY, 0.35)
    # heavy price tag dropping and thudding
    drop = ease(seg(p, 0, 0.3))
    y = GY - 160 - (1 - drop) * 700
    if seg(p, 0.3, 0.4) > 0 and p < 0.4:
        y += math.sin(seg(p, 0.3, 0.4) * math.pi) * 18
    cx = W / 2
    c = n.c
    c.new_path()
    c.move_to(cx - 230, y - 120)
    c.line_to(cx + 150, y - 120)
    c.line_to(cx + 260, y)
    c.line_to(cx + 150, y + 120)
    c.line_to(cx - 230, y + 120)
    c.close_path()
    n.stroke(1, 7)
    c.new_path(); c.arc(cx + 165, y, 18, 0, 6.3); n.stroke(1, 5)
    c.set_font_size(78)
    txt = "RM ???"
    e = c.text_extents(txt)
    c.move_to(cx - 50 - e.width / 2 - e.x_bearing, y - e.height / 2 - e.y_bearing)
    c.show_text(txt); n.fill(1)
    # impact lines
    if 0.28 < p < 0.6:
        k = 1 - seg(p, 0.28, 0.6)
        for sgn in (-1, 1):
            for j in range(3):
                x0 = cx + sgn * (290 + j * 10)
                c.new_path(); c.move_to(x0, GY - 20 - j * 40); c.line_to(x0 + sgn * 60, GY - 50 - j * 50)
                n.stroke(k, 5)
    # floating question marks
    k = ease(seg(p, 0.4, 0.7))
    c.set_font_size(90)
    for j, (dx, dy) in enumerate(((-260, -330), (230, -400), (0, -470))):
        c.move_to(cx + dx, y + dy + math.sin(t * 3 + j) * 10)
        c.show_text("?"); n.fill(k * (0.6 + 0.2 * j))
    for x, yy, r, a in particles(40, t):
        n.c.arc(x, yy, r, 0, 6.3); n.fill(a * 0.6)
    return f, n, "Masalahnya, ramai ingat bulanan dia *mesti mencekik.*"


# ---------------------------------------------------------------------------
# storyboard
# ---------------------------------------------------------------------------
def read_frame(raw, t):
    out = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", raw, "-frames:v", "1",
                          "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(out, np.uint8).reshape(H, W, 3).astype(np.float32)


def render_still(typo, f, n, caption, extra=(), header=True):
    items = []
    if header:
        items.append({"kind": "header", "label": HEADER_LABEL, "title": HEADER_TITLE})
    if caption:
        items.append({"kind": "caption", "text": caption})
    items.extend(extra)
    return composite(f, n.mask() if n else None, draw_text_layer(typo, items))


def storyboard(font, raw, outdir):
    os.makedirs(outdir, exist_ok=True)
    typo = Typo(font)
    frames = []
    anim = [
        ("01_hook", scene_hook, 0.9, "0–3s"),
        ("02_twist", scene_twist, 0.9, "3–6s"),
        ("03_family", scene_family, 0.8, "6–10s"),
        ("04_door", scene_door, 0.8, "10–14s"),
        ("05_trip", scene_trip, 0.8, "14–18s"),
        ("06_price", scene_price, 0.8, "18–20s"),
    ]
    for name, fn, p, _ in anim:
        f, n, cap = fn(p, p * 3)
        img = render_still(typo, f, n, cap)
        frames.append((name, img))

    # 07 ring transition into footage + spec chips
    fo = grade_footage(read_frame(raw, 10.0))
    n = Neon()
    bgf = background()
    mix = ring_reveal(bgf, fo, 0.45, n)
    img = render_still(typo, mix, n, "Unit *Alphard Z 2024* ni, *grade 5A*, mileage baru *5,000 km.*")
    frames.append(("07a_ring", img))
    n = Neon()
    chips = [
        {"kind": "chip", "text": "GRADE 5A", "x": W / 2 - 200, "y": 1520},
        {"kind": "chip", "text": "5,000 KM", "x": W / 2 + 200, "y": 1520},
        {"kind": "chip", "text": "RM2,700 / BULAN", "x": W / 2, "y": 1625, "size": 46},
    ]
    img = render_still(typo, fo, None, "Bulanan sekitar *RM2,700* je.", chips)
    frames.append(("07b_specs", img))

    fo = grade_footage(read_frame(raw, 19.5))
    img = render_still(typo, fo, None, "Siap *free bodykit Modellista.*",
                       [{"kind": "chip", "text": "FREE BODYKIT", "x": W / 2, "y": 1520}])
    frames.append(("08_bodykit", img))

    fo = grade_footage(read_frame(raw, 45.0))
    img = render_still(typo, fo, None, "Kalau betul-betul perlukan,",
                       [{"kind": "cta", "text": 'KOMEN "NAK"', "y": 1500, "sub": "SAYA DM KORANG"}])
    frames.append(("09_cta", img))

    for name, img in frames:
        Image.fromarray(img).save(os.path.join(outdir, f"{name}.png"))
    # contact sheet with labels
    tw, th = 360, 640
    cols = 5
    rows = math.ceil(len(frames) / cols)
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * 16, rows * (th + 56) + 16), (24, 24, 24))
    d = ImageDraw.Draw(sheet)
    lf = ImageFont.truetype(font, 24)
    for i, (name, img) in enumerate(frames):
        r, cidx = divmod(i, cols)
        x, y = 16 + cidx * (tw + 16), 16 + r * (th + 56)
        sheet.paste(Image.fromarray(img).resize((tw, th), Image.LANCZOS), (x, y + 40))
        d.text((x, y + 4), name.upper().replace("_", " "), font=lf, fill=GREEN_T)
    sheet.save(os.path.join(outdir, "storyboard_sheet.jpg"), quality=92)
    return frames


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", required=True)
    ap.add_argument("--raw", required=True)
    ap.add_argument("--outdir", required=True)
    a = ap.parse_args()
    storyboard(a.font, a.raw, a.outdir)
    print("ok")
