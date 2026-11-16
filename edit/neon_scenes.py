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


# ---------------------------------------------------------------------------
# extra primitives (money / smoking / hot-hatch story)
# ---------------------------------------------------------------------------
def hatch(n, cx, gy, s=1.0, a=1.0, draw=1.0, wheel_rot=0.0):
    """Hot-hatch side profile with a tall rear wing (facing right)."""
    c = n.c
    ox = cx - 390 * s

    def P(x, h):
        return ox + x * s, gy - h * s

    lw = 6 * s
    c.new_path()
    c.move_to(*P(60, 40))
    c.line_to(*P(84, 40))
    c.arc_negative(*P(170, 72), 90 * s, math.radians(165), math.radians(15))
    c.line_to(*P(522, 40))
    c.arc_negative(*P(610, 72), 90 * s, math.radians(165), math.radians(15))
    c.line_to(*P(745, 40))
    c.curve_to(*P(768, 42), *P(778, 60), *P(778, 85))      # front bumper
    c.line_to(*P(772, 130))
    c.curve_to(*P(766, 150), *P(745, 162), *P(720, 168))   # nose
    c.line_to(*P(585, 205))                                # long low hood
    c.line_to(*P(470, 292))                                # windscreen
    c.curve_to(*P(455, 302), *P(430, 304), *P(400, 304))
    c.line_to(*P(250, 296))                                # roof
    c.curve_to(*P(160, 280), *P(90, 230), *P(52, 196))     # fastback hatch
    c.line_to(*P(36, 150))
    c.line_to(*P(30, 90))                                  # rear bumper
    c.curve_to(*P(30, 55), *P(40, 40), *P(60, 40))
    c.close_path()
    _reveal(n, a, lw, draw)
    # glass
    c.new_path()
    c.move_to(*P(150, 215))
    c.curve_to(*P(190, 250), *P(220, 272), *P(255, 282))
    c.line_to(*P(398, 288))
    c.line_to(*P(462, 222))
    c.close_path()
    _reveal(n, a * 0.85, lw * 0.75, draw)
    c.new_path()
    c.move_to(*P(352, 286))
    c.line_to(*P(352, 218))
    _reveal(n, a * 0.85, lw * 0.75, draw)
    # rear wing on stilts
    c.new_path()
    c.move_to(*P(70, 210))
    c.line_to(*P(56, 262))
    c.move_to(*P(118, 240))
    c.line_to(*P(108, 266))
    _reveal(n, a, lw * 0.8, draw)
    c.new_path()
    c.move_to(*P(8, 262))
    c.line_to(*P(150, 272))
    _reveal(n, a, lw * 1.5, draw)
    # side skirt, door seam, hood vent, headlight
    for (x0, h0, x1, h1, k) in ((150, 58, 520, 58, 0.55), (468, 210, 474, 70, 0.6),
                                (600, 196, 650, 186, 0.8), (700, 160, 760, 140, 1.0)):
        c.new_path()
        c.move_to(*P(x0, h0))
        c.line_to(*P(x1, h1))
        _reveal(n, a * k, lw * (1.1 if k == 1.0 else 0.6), draw)
    for wx in (170, 610):
        x, y = P(wx, 72)
        c.new_path()
        c.arc(x, y, 66 * s, 0, 2 * math.pi)
        _reveal(n, a, lw, draw)
        c.new_path()
        c.arc(x, y, 40 * s, 0, 2 * math.pi)
        _reveal(n, a * 0.7, lw * 0.6, draw)
        for k in range(10):
            ang = wheel_rot + k * math.pi / 5
            c.new_path()
            c.move_to(x + math.cos(ang) * 12 * s, y + math.sin(ang) * 12 * s)
            c.line_to(x + math.cos(ang) * 38 * s, y + math.sin(ang) * 38 * s)
            _reveal(n, a * 0.45, lw * 0.35, draw)


def _reveal(n, a, lw, draw):
    _reveal_stroke(n, a, lw, draw)


def cigarette(n, cx, cy, length=520, a=1.0, ember=1.0, burn=0.0, broken=0.0):
    """Horizontal cigarette, filter on the left, ember on the right.
    burn: 0..1 shortens it, broken: 0..1 snaps it in two."""
    c = n.c
    h = length * 0.13
    L = length * (1 - 0.35 * burn)
    x0 = cx - length / 2
    gap = 60 * broken
    rot = 0.35 * broken
    for half in (0, 1):
        c.save()
        mid = x0 + L * 0.5
        if broken > 0:
            c.translate(mid, cy)
            c.rotate(-rot if half == 0 else rot)
            c.translate(-mid + (-gap if half == 0 else gap), -cy)
        xa, xb = (x0, mid) if half == 0 else (mid, x0 + L)
        c.new_path()
        if half == 0:
            c.move_to(xb, cy - h / 2)
            c.line_to(xa + h / 2, cy - h / 2)
            c.arc_negative(xa + h / 2, cy, h / 2, -math.pi / 2, math.pi / 2)
            c.line_to(xb, cy + h / 2)
            n.stroke(a, 6)
            fx = xa + length * 0.27  # filter band
            c.new_path()
            c.move_to(fx, cy - h / 2)
            c.line_to(fx, cy + h / 2)
            n.stroke(a, 5)
            for k in range(3):
                c.new_path()
                c.arc(xa + 30 + k * 34, cy + (k % 2 - 0.5) * h * 0.35, 4, 0, 6.3)
                n.fill(a * 0.6)
        else:
            c.move_to(xa, cy - h / 2)
            c.line_to(xb, cy - h / 2)
            c.line_to(xb, cy + h / 2)
            c.line_to(xa, cy + h / 2)
            n.stroke(a, 6)
            if ember > 0:
                c.new_path()
                c.rectangle(xb - 10, cy - h / 2 + 6, 12, h - 12)
                n.fill(a * ember)
                c.new_path()
                c.arc(xb + 6, cy, h * 0.42, 0, 6.3)
                n.fill(a * ember * 0.35)
        c.restore()
    return x0 + L  # ember x


def smoke(n, x, y, t, a=1.0, height=330, strands=3):
    c = n.c
    for k in range(strands):
        ph = t * 1.6 + k * 2.1
        c.new_path()
        steps = 24
        for i in range(steps + 1):
            u = i / steps
            px = x + math.sin(u * 5 + ph) * (12 + 40 * u) + (k - 1) * 14 * u
            py = y - u * height
            if i == 0:
                c.move_to(px, py)
            else:
                c.line_to(px, py)
        n.stroke(a * 0.5, 4)


def bill(n, x, y, s=1.0, a=1.0, rot=0.0):
    c = n.c
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    w, h = 150 * s, 76 * s
    c.new_path()
    c.rectangle(-w / 2, -h / 2, w, h)
    n.stroke(a, 5 * s)
    c.new_path()
    c.rectangle(-w / 2 + 10 * s, -h / 2 + 10 * s, w - 20 * s, h - 20 * s)
    n.stroke(a * 0.5, 2.5 * s)
    c.set_font_size(30 * s)
    e = c.text_extents("RM")
    c.move_to(-e.width / 2 - e.x_bearing, -e.height / 2 - e.y_bearing)
    c.show_text("RM")
    n.fill(a)
    c.restore()


def coin(n, x, y, r=26, a=1.0):
    c = n.c
    c.new_path()
    c.arc(x, y, r, 0, 6.3)
    n.stroke(a, 5)
    c.new_path()
    c.arc(x, y, r * 0.62, 0, 6.3)
    n.stroke(a * 0.6, 3)


def cig_box(n, cx, cy, s=1.0, a=1.0, label="ROKOK"):
    c = n.c
    w, h = 200 * s, 270 * s
    x0, y0 = cx - w / 2, cy - h / 2
    for k in range(3):  # cigarettes peeking out
        c.new_path()
        c.rectangle(x0 + 38 * s + k * 46 * s, y0 - 46 * s, 30 * s, 60 * s)
        n.stroke(a * 0.8, 4 * s)
    c.new_path()
    c.rectangle(x0, y0, w, h)
    n.stroke(a, 6 * s)
    c.new_path()
    c.move_to(x0, y0 + 70 * s)
    c.line_to(x0 + w, y0 + 70 * s)
    n.stroke(a * 0.7, 4 * s)
    c.set_font_size(36 * s)
    e = c.text_extents(label)
    c.move_to(cx - e.width / 2 - e.x_bearing, cy + 40 * s - e.height / 2 - e.y_bearing)
    c.show_text(label)
    n.fill(a)


def piggy(n, cx, cy, s=1.0, a=1.0):
    """Piggy-bank (tabung) side view facing right. Returns slot position."""
    c = n.c
    c.save()
    c.translate(cx, cy)
    c.scale(1.0, 0.78)
    c.new_path()
    c.arc(0, 0, 170 * s, 0, 2 * math.pi)
    c.restore()
    n.stroke(a, 6 * s)
    # snout
    c.new_path()
    c.save()
    c.translate(cx + 178 * s, cy + 6 * s)
    c.scale(0.7, 1.0)
    c.arc(0, 0, 44 * s, 0, 2 * math.pi)
    c.restore()
    n.stroke(a, 6 * s)
    for dy in (-12, 14):
        c.new_path()
        c.arc(cx + 180 * s, cy + (6 + dy) * s, 6 * s, 0, 6.3)
        n.fill(a)
    # ear, eye, legs, tail
    c.new_path()
    c.move_to(cx + 60 * s, cy - 118 * s)
    c.line_to(cx + 96 * s, cy - 178 * s)
    c.line_to(cx + 120 * s, cy - 104 * s)
    n.stroke(a, 6 * s)
    c.new_path()
    c.arc(cx + 112 * s, cy - 40 * s, 8 * s, 0, 6.3)
    n.fill(a)
    for lx in (-100, -40, 50, 110):
        c.new_path()
        c.move_to(cx + lx * s, cy + 118 * s)
        c.line_to(cx + lx * s, cy + 168 * s)
        n.stroke(a, 10 * s)
    c.new_path()
    c.move_to(cx - 170 * s, cy - 10 * s)
    c.curve_to(cx - 215 * s, cy - 30 * s, cx - 215 * s, cy + 30 * s, cx - 190 * s, cy + 18 * s)
    n.stroke(a, 5 * s)
    # coin slot
    c.new_path()
    c.move_to(cx - 40 * s, cy - 132 * s)
    c.line_to(cx + 30 * s, cy - 132 * s)
    n.stroke(a, 8 * s)
    return cx - 5 * s, cy - 132 * s


def calendar(n, cx, cy, s=1.0, a=1.0, text="", sub=""):
    c = n.c
    w, h = 260 * s, 250 * s
    x0, y0 = cx - w / 2, cy - h / 2
    c.new_path()
    c.rectangle(x0, y0, w, h)
    n.stroke(a, 6 * s)
    c.new_path()
    c.move_to(x0, y0 + 60 * s)
    c.line_to(x0 + w, y0 + 60 * s)
    n.stroke(a, 5 * s)
    for rx in (-60, 60):
        c.new_path()
        c.move_to(cx + rx * s, y0 - 20 * s)
        c.line_to(cx + rx * s, y0 + 22 * s)
        n.stroke(a, 8 * s)
    if text:
        c.set_font_size(96 * s)
        e = c.text_extents(text)
        c.move_to(cx - e.width / 2 - e.x_bearing, cy + 34 * s - e.height / 2 - e.y_bearing)
        c.show_text(text)
        n.fill(a)
    if sub:
        c.set_font_size(30 * s)
        e = c.text_extents(sub)
        c.move_to(cx - e.width / 2 - e.x_bearing, y0 + 30 * s - e.height / 2 - e.y_bearing)
        c.show_text(sub)
        n.fill(a)


def neon_text(n, cx, cy, text, size, a=1.0):
    c = n.c
    c.set_font_size(size)
    e = c.text_extents(text)
    c.move_to(cx - e.width / 2 - e.x_bearing, cy - e.height / 2 - e.y_bearing)
    c.show_text(text)
    n.fill(a)
