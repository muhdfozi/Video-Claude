#!/usr/bin/env python3
"""Neon line-art scene library for the "Alphard Bukan Untuk Orang Kaya Je" video.

Look: black background, fluorescent-green (#39FF14) glowing line art, white
captions with green keywords, Formula1 font. Every scene is a function of local
progress p (0..1) so the same code renders storyboard stills and the final
animation.

Primitives only; scenes and the timeline live in alphard_neon_video.py.
"""
import math

import cairo
import cv2
import numpy as np
from PIL import ImageFont

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


GY = 1130  # ground line for illustrations
