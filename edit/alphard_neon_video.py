#!/usr/bin/env python3
"""Render "Alphard Bukan Untuk Orang Kaya Je" (neon explainer -> footage -> CTA).

Assets (all from the Drive folder):
  Voiceover/Prife International 6.m4a      narration (timeline master, 49.6 s)
  Raw Video/IMG_0212..0218.MOV              4K HLG clips (tone-mapped to SDR)
  Music/v24044gl0000cthro1vog65gunpi1teg.mp4  background bed
  Font Type/Formula1-Bold_web_0.ttf

Usage:
  python3 alphard_neon_video.py --assets "DIR/Video Claude" --out OUT.mp4 [--preview]
  python3 alphard_neon_video.py --assets ... --storyboard OUTDIR
"""
import argparse
import math
import os
import subprocess
import sys
import wave

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from neon_scenes import (GY, GREEN_T, H, HEADER_LABEL, HEADER_TITLE, W, Neon, Typo,  # noqa: E402
                         background, car, clamp, ease, ease_io, glow, ground, particles,
                         person, pill)

FPS = 30
DURATION = 49.64
MUSIC_START = 705.0  # calm, steady passage of the classical bed

VO = "Voiceover/Prife International 6.m4a"
MUSIC = "Music/v24044gl0000cthro1vog65gunpi1teg.mp4"
FONT = "Font Type/Formula1-Bold_web_0.ttf"


def sec(lt, a, b):
    """0..1 progress of local time lt inside [a, b] seconds."""
    return clamp((lt - a) / (b - a)) if b > a else float(lt >= a)


# ---------------------------------------------------------------------------
# Captions, synced to the voiceover (Whisper word timestamps, text corrected)
# ---------------------------------------------------------------------------
CAPTIONS = [
    (0.90, 4.60, "Ramai ingat Alphard ni kereta *orang kaya* je."),
    (4.68, 6.58, "Sebenarnya, Alphard ni"),
    (6.62, 9.20, "untuk orang yang *betul-betul memerlukan.*"),
    (9.34, 11.40, "Contohnya, *keluarga besar,*"),
    (11.44, 14.14, "anak ramai, nak bawa *mak ayah* sekali."),
    (14.18, 16.70, "*Semua muat, semua selesa.*"),
    (16.82, 18.20, "Mak ayah dah *berusia,*"),
    (18.24, 20.18, "pintu belakang *buka sendiri,*"),
    (20.22, 22.24, "tak payah tarik pintu yang berat."),
    (22.32, 23.82, "Balik kampung *jauh,*"),
    (23.86, 25.54, "anak-anak duduk belakang,"),
    (25.58, 26.86, "ada *roof monitor,*"),
    (26.90, 28.18, "tak bosan sepanjang jalan."),
    (28.22, 29.72, "Masalahnya,"),
    (29.76, 32.80, "ramai ingat bulanan dia *mesti mencekik.*"),
    (32.90, 36.00, "Unit *Alphard Z* tahun *2024* ni,"),
    (36.06, 37.46, "*grade 5A,*"),
    (37.50, 39.84, "mileage baru *5,000 km,*"),
    (39.88, 42.36, "bulanan sekitar *RM2,700* je."),
    (42.40, 44.70, "Siap *free bodykit Modellista.*"),
    (44.76, 46.52, "Kalau *betul-betul perlukan,*"),
    (46.56, DURATION, "komen *\"NAK\",* saya DM korang."),
]

# ---------------------------------------------------------------------------
# Neon scenes (local time lt in seconds, global time t)
# ---------------------------------------------------------------------------
def dust(n, t):
    for x, y, r, a in particles(45, t):
        n.c.new_path()
        n.c.arc(x, y, r, 0, 6.3)
        n.fill(a * 0.55)


SPOT_CACHE = {}


def spotlight_mask():
    if "m" in SPOT_CACHE:
        return SPOT_CACHE["m"]
    cx, top, bottom, width = W / 2, 520, GY + 20, 900
    m = np.zeros((H, W), np.float32)
    pts = np.array([[cx - 40, top], [cx + 40, top], [cx + width / 2, bottom], [cx - width / 2, bottom]], np.int32)
    cv2.fillConvexPoly(m, pts, 1.0)
    for k in range(-3, 4):
        cv2.line(m, (int(cx + k * 8), top), (int(cx + k * width / 8), bottom), 1.6, 6, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), 18)
    yy = np.linspace(0, 1, H)[:, None]
    fade = np.clip((yy * H - top) / (bottom - top), 0, 1) ** 0.7
    m *= (1 - fade * 0.55)
    SPOT_CACHE["m"] = m[..., None] * np.array([40, 90, 35], np.float32)
    return SPOT_CACHE["m"]


def s_hook(lt, t):
    n, f = Neon(), background()
    ground(n, GY)
    car(n, W / 2, GY, 1.0, draw=ease(sec(lt, 0.0, 1.9)))
    k = ease(sec(lt, 2.0, 2.5))
    pill(n, W / 2, GY - 470 - 20 * (1 - k), "ORANG KAYA?", 40, a=k)
    dust(n, t)
    return f, n


def s_twist(lt, t):  # starts 4.68
    n, f = Neon(), background()
    f = f + spotlight_mask() * ease(sec(lt, 2.0, 3.0))
    ground(n, GY)
    car(n, W / 2, GY, 1.0)
    pill(n, W / 2, GY - 470, "ORANG KAYA?", 40, a=1 - 0.75 * sec(lt, 0.8, 1.6),
         strike=ease(sec(lt, 0.1, 0.6)))
    k = ease(sec(lt, 2.6, 3.1))
    pill(n, W / 2, GY - 590, "YANG MEMERLUKAN", 40, a=k, filled=True)
    dust(n, t)
    return f, n


def s_family(lt, t):  # starts 9.2
    n, f = Neon(), background()
    ground(n, GY)
    car(n, W / 2 + 120, GY, 0.82, seats=sec(lt, 2.4, 6.0))
    family = [("elder", 0.62), ("adult", 0.78), ("adult", 0.8), ("child", 0.8), ("child", 0.8)]
    for i, (kind, sc) in enumerate(family):
        k = ease(sec(lt, 0.8 + i * 0.5, 1.8 + i * 0.5))
        x = 62 + i * 66 + 40 * (1 - k)
        person(n, x, GY, sc * 0.9, a=k, kind=kind, walk=t * 1.5 + i * 0.3)
    pill(n, W / 2 + 120, GY - 430, "SEMUA MUAT", 38, a=ease(sec(lt, 5.0, 5.5)))
    dust(n, t)
    return f, n


def s_door(lt, t):  # starts 16.6
    n, f = Neon(), background()
    ground(n, GY)
    door = ease_io(sec(lt, 2.1, 3.4))
    car(n, W / 2 + 130, GY, 0.86, door=door)
    k = ease(sec(lt, 3.6, 5.4))
    person(n, 70 + 70 * k, GY, 0.72, a=ease(sec(lt, 0.3, 0.9)), kind="elder", walk=t * 1.2)
    if 2.0 < lt < 3.8:
        for j in range(3):
            x = W / 2 + 130 - 95 - j * 34 - 140 * door
            n.c.new_path()
            n.c.move_to(x + 12, GY - 200)
            n.c.line_to(x, GY - 185)
            n.c.line_to(x + 12, GY - 170)
            n.stroke(0.8 - j * 0.25, 5)
    pill(n, W / 2 + 130, GY - 420, "PINTU AUTO", 38, a=ease(sec(lt, 2.4, 2.9)))
    dust(n, t)
    return f, n


def s_trip(lt, t):  # starts 22.2
    n, f = Neon(), background()
    ground(n, GY, 0.5, 0, W)
    off = (t * 420) % 160
    for i in range(-1, 9):
        x = i * 160 - off
        n.c.new_path()
        n.c.move_to(x, GY + 60)
        n.c.line_to(x + 80, GY + 60)
        n.stroke(0.45, 5)
    car(n, W / 2, GY + math.sin(t * 9) * 2, 0.9, wheel_rot=t * 12)
    for j, yy in enumerate((GY - 260, GY - 180, GY - 100)):
        x = 90 - (t * 300 + j * 80) % 60
        n.c.new_path()
        n.c.move_to(x, yy)
        n.c.line_to(x + 70 - j * 15, yy)
        n.stroke(0.5, 4)
    k = ease(sec(lt, 3.3, 3.8))
    if k > 0:
        bx, by = W / 2 - 40, GY - 530
        n.c.new_path()
        n.c.rectangle(bx - 150, by - 90, 300, 180)
        n.stroke(k, 6)
        n.c.new_path()
        n.c.move_to(bx, by + 90)
        n.c.line_to(bx - 30, GY - 330)
        n.stroke(k * 0.5, 3)
        pul = 0.7 + 0.3 * math.sin(t * 6)
        n.c.new_path()
        n.c.move_to(bx - 25, by - 35)
        n.c.line_to(bx + 35, by)
        n.c.line_to(bx - 25, by + 35)
        n.c.close_path()
        n.fill(k * pul)
        pill(n, bx, by - 135, "ROOF MONITOR", 32, a=k)
    dust(n, t)
    return f, n


def s_price(lt, t):  # starts 28.1
    n, f = Neon(), background()
    ground(n, GY, 0.35)
    t_drop = 2.4  # "bulanan" @ 30.66
    drop = ease(sec(lt, t_drop - 0.45, t_drop))
    vis = sec(lt, t_drop - 0.5, t_drop - 0.45)
    y = GY - 160 - (1 - drop) * 760
    bounce = sec(lt, t_drop, t_drop + 0.25)
    if 0 < bounce < 1:
        y -= math.sin(bounce * math.pi) * 22
    cx = W / 2
    c = n.c
    if vis > 0:
        c.new_path()
        c.move_to(cx - 230, y - 120)
        c.line_to(cx + 150, y - 120)
        c.line_to(cx + 260, y)
        c.line_to(cx + 150, y + 120)
        c.line_to(cx - 230, y + 120)
        c.close_path()
        n.stroke(vis, 7)
        c.new_path()
        c.arc(cx + 165, y, 18, 0, 6.3)
        n.stroke(vis, 5)
        c.set_font_size(78)
        txt = "RM ???"
        e = c.text_extents(txt)
        c.move_to(cx - 50 - e.width / 2 - e.x_bearing, y - e.height / 2 - e.y_bearing)
        c.show_text(txt)
        n.fill(vis)
    imp = sec(lt, t_drop, t_drop + 0.6)
    if 0 < imp < 1:
        for sgn in (-1, 1):
            for j in range(3):
                x0 = cx + sgn * (290 + j * 10)
                c.new_path()
                c.move_to(x0, GY - 20 - j * 40)
                c.line_to(x0 + sgn * 60 * (0.5 + imp), GY - 50 - j * 50)
                n.stroke(1 - imp, 5)
    k = ease(sec(lt, 3.3, 3.8))  # "mesti mencekik"
    c.set_font_size(90)
    for j, (dx, dy) in enumerate(((-260, -270), (230, -330), (0, -390))):
        c.move_to(cx + dx, y + dy + math.sin(t * 3 + j) * 10)
        c.show_text("?")
        n.fill(k * (0.6 + 0.2 * j))
    dust(n, t)
    return f, n


ANIM = [  # (start, end, fn)
    (0.0, 4.68, s_hook),
    (4.68, 9.20, s_twist),
    (9.20, 16.60, s_family),
    (16.60, 22.20, s_door),
    (22.20, 28.10, s_trip),
    (28.10, 33.40, s_price),
]
XFADE = 0.45

# ---------------------------------------------------------------------------
# Footage
# ---------------------------------------------------------------------------
RING_START, RING_END = 32.55, 33.35
FOOT = [  # (clip, start, end, chip text)
    ("IMG_0212", 32.55, 36.00, "ALPHARD Z 2024"),
    ("IMG_0218", 36.00, 37.50, "GRADE 5A"),
    ("IMG_0217", 37.50, 39.86, "5,000 KM"),
    ("IMG_0215", 39.86, 42.38, "RM2,700 / BULAN"),
    ("IMG_0214", 42.38, 44.72, "FREE BODYKIT"),
]
CTA_START = 44.72          # Ken-Burns still from IMG_0212 under the CTA
CTA_BUTTON = 46.56
DISSOLVE = 0.22
CLIP_DUR = {"IMG_0212": 2.818, "IMG_0214": 1.467, "IMG_0215": 2.65, "IMG_0217": 2.45, "IMG_0218": 2.517}

TONEMAP = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,"
           "tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,"
           "eq=contrast=1.08:saturation=1.18:brightness=0.015")


class ClipReader:
    """Streams tone-mapped 1080x1920 frames at 30 fps, slowed to fill the slot."""

    def __init__(self, path, slot):
        src = CLIP_DUR[os.path.basename(path).split(".")[0]]
        self.speed = min(1.0, (src - 0.05) / (slot + DISSOLVE))
        vf = (f"{TONEMAP},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
              f"setpts=(PTS-STARTPTS)/{self.speed:.4f},fps={FPS}")
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-an", "-vf", vf,
                                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        self.idx, self.last = -1, None

    def frame(self, lt):
        want = max(0, int(lt * FPS + 1e-6))
        while self.idx < want:
            buf = self.p.stdout.read(W * H * 3)
            if len(buf) < W * H * 3:
                break
            self.last = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
            self.idx += 1
        return self.last

    def close(self):
        self.p.kill()


def push(img, z):
    if abs(z - 1) < 1e-4:
        return img.astype(np.float32)
    M = np.float32([[z, 0, (1 - z) * W / 2], [0, z, (1 - z) * H / 2]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR).astype(np.float32)


_SHADE = {}


def shade(img):
    """darken bottom (captions) and top a little."""
    if "s" not in _SHADE:
        yy = np.linspace(0, 1, H)[:, None, None]
        s = np.clip((yy - 0.52) / 0.38, 0, 1) ** 1.2 * 0.75 + np.clip((0.18 - yy) / 0.18, 0, 1) * 0.35
        _SHADE["s"] = (1 - s).astype(np.float32)
    return img * _SHADE["s"]


# ---------------------------------------------------------------------------
# Text layer
# ---------------------------------------------------------------------------
def parse(text):
    words, hl = [], False
    for tok in text.split():
        if tok.startswith("*"):
            hl, tok = True, tok[1:]
        end = "*" in tok
        words.append((tok.replace("*", ""), hl))
        if end:
            hl = False
    return words


def caption(d, typo, text, a, dy=0, size=54, y=1395):
    f = typo.font(size)
    words = parse(text)
    space = d.textlength(" ", font=f)
    def width(ws):
        return sum(d.textlength(w, font=f) for w, _ in ws) + space * (len(ws) - 1)

    if width(words) <= 900 or len(words) < 2:
        lines = [(words, width(words))]
    else:  # two balanced lines (no orphan words)
        k = min(range(1, len(words)), key=lambda k: max(width(words[:k]), width(words[k:])))
        lines = [(words[:k], width(words[:k])), (words[k:], width(words[k:]))]
    lh = int(size * 1.32)
    y0 = y - len(lines) * lh / 2 + dy
    for i, (ln, lw) in enumerate(lines):
        x = (W - lw) / 2
        for w, h_ in ln:
            col = GREEN_T if h_ else (255, 255, 255)
            d.text((x + 2, y0 + i * lh + 4), w, font=f, fill=(0, 0, 0, int(a * 0.55)))
            d.text((x, y0 + i * lh), w, font=f, fill=col + (a,), stroke_width=3,
                   stroke_fill=(0, 0, 0, int(a * 0.8)))
            x += d.textlength(w, font=f) + space


def header(d, typo, a):
    f1, f2 = typo.font(30), typo.font(58)
    lab = " ".join(HEADER_LABEL)
    w1 = d.textlength(lab, font=f1)
    d.text(((W - w1) / 2, 250), lab, font=f1, fill=GREEN_T + (a,))
    w2 = d.textlength(HEADER_TITLE, font=f2)
    d.text(((W - w2) / 2, 298), HEADER_TITLE, font=f2, fill=(255, 255, 255, a))
    cy = 400
    d.line([(W / 2 - 150, cy), (W / 2 - 34, cy)], fill=(255, 255, 255, a // 2), width=2)
    d.line([(W / 2 + 34, cy), (W / 2 + 150, cy)], fill=(255, 255, 255, a // 2), width=2)
    d.rounded_rectangle([W / 2 - 22, cy - 5, W / 2 + 22, cy + 5], radius=5, fill=GREEN_T + (a,))


def chip(d, typo, text, a, sc, y=1520):
    f = typo.font(max(8, int(44 * sc)))
    tw = d.textlength(text, font=f)
    w, h = tw + 64 * sc, 84 * sc
    x0, y0 = W / 2 - w / 2, y + (84 - h) / 2
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=h / 2, fill=(10, 10, 10, int(a * 0.85)),
                        outline=GREEN_T + (a,), width=max(2, int(4 * sc)))
    d.text((W / 2 - tw / 2, y0 + 16 * sc), text, font=f, fill=(255, 255, 255, a))


def cta(d, typo, a, sc):
    txt = 'KOMEN "NAK"'
    f = typo.font(max(8, int(60 * sc)))
    tw = d.textlength(txt, font=f)
    bw, bh = tw + 120 * sc, 118 * sc
    cy = 1560
    d.rounded_rectangle([W / 2 - bw / 2, cy - bh / 2, W / 2 + bw / 2, cy + bh / 2], radius=bh / 2,
                        fill=GREEN_T + (a,))
    d.text((W / 2 - tw / 2, cy - 36 * sc), txt, font=f, fill=(10, 10, 10, a))
    f2 = typo.font(34)
    sub = "SAYA DM KORANG"
    w2 = d.textlength(sub, font=f2)
    d.text((W / 2 - w2 / 2, cy + 82), sub, font=f2, fill=(255, 255, 255, a))


def pop(dt, dur=0.22, k=1.8):
    if dt >= dur:
        return 1.0
    x = dt / dur - 1
    return 0.5 + 0.5 * (1 + (k + 1) * x ** 3 + k * x ** 2)


_TXT_CACHE = {}


def text_layer(typo, t):
    items = []
    ha = 1 - sec(t, RING_START, RING_START + 0.45)
    if ha > 0:
        items.append(("h", round(ha, 2)))
    for i, (st, en, _) in enumerate(CAPTIONS):
        if st <= t < en:
            a = sec(t, st, st + 0.18) * (1 - sec(t, en - 0.1, en))
            items.append(("c", i, round(a, 2), round((1 - ease(sec(t, st, st + 0.25))) * 18)))
    for clip, st, en, txt in FOOT:
        cs = st + (0.75 if clip == "IMG_0212" else 0.15)
        if cs <= t < en:
            items.append(("chip", txt, round(sec(t, cs, cs + 0.12), 2), round(pop(t - cs), 2)))
    if t >= CTA_BUTTON:
        pul = 1 + 0.03 * math.sin((t - CTA_BUTTON) * 6) if t > CTA_BUTTON + 0.4 else 1
        items.append(("cta", round(sec(t, CTA_BUTTON, CTA_BUTTON + 0.1), 2),
                      round(pop(t - CTA_BUTTON, 0.3) * pul, 3)))
    key = tuple(items)
    if key in _TXT_CACHE:
        return _TXT_CACHE[key]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for it in items:
        if it[0] == "h":
            header(d, typo, int(255 * it[1]))
        elif it[0] == "c":
            caption(d, typo, CAPTIONS[it[1]][2], int(255 * it[2]), dy=it[3])
        elif it[0] == "chip":
            chip(d, typo, it[1], int(255 * it[2]), it[3])
        elif it[0] == "cta":
            cta(d, typo, int(255 * it[1]), it[2])
    arr = np.asarray(img).astype(np.float32)
    val = (arr[..., :3], arr[..., 3:4] / 255.0)
    if len(_TXT_CACHE) > 64:
        _TXT_CACHE.clear()
    _TXT_CACHE[key] = val
    return val


# ---------------------------------------------------------------------------
# Frame renderer
# ---------------------------------------------------------------------------
class Renderer:
    def __init__(self, assets):
        self.assets = assets
        self.typo = Typo(os.path.join(assets, FONT))
        self.readers = {}
        self.cta_still = None

    def reader(self, clip, slot):
        if clip not in self.readers:
            self.readers[clip] = ClipReader(os.path.join(self.assets, "Raw Video", clip + ".MOV"), slot)
        return self.readers[clip]

    def neon(self, t):
        """background + neon mask for the animated section (with crossfades)."""
        active = [(st, en, fn) for st, en, fn in ANIM if st - XFADE / 2 <= t < en + XFADE / 2]
        if len(active) == 1:
            st, _, fn = active[0]
            f, n = fn(t - st, t)
            return f, n.mask()
        (s1, e1, f1), (s2, _, f2) = active[:2]
        # dip: outgoing line art fades out, then the next scene fades in (no ghosting)
        x = sec(t, s2 - XFADE / 2, s2 + XFADE / 2)
        if x < 0.5:
            f, n = f1(t - s1, t)
            k = ease_io(1 - 2 * x)
        else:
            f, n = f2(t - s2, t)
            k = ease_io(2 * x - 1)
        bg = background()
        return bg + (f - bg) * k, n.mask() * k

    def footage(self, t):
        cur = None
        for i, (clip, st, en, _) in enumerate(FOOT):
            if st <= t < en:
                cur = i
        if t >= CTA_START:
            return self.cta_frame(t)
        clip, st, en, _ = FOOT[cur]
        z = 1.0 + 0.05 * sec(t, st, en + DISSOLVE)
        img = push(self.reader(clip, en - st).frame(t - st), z)
        nxt_start = FOOT[cur + 1][1] if cur + 1 < len(FOOT) else CTA_START
        if t > nxt_start - DISSOLVE:  # dissolve into next shot
            x = sec(t, nxt_start - DISSOLVE, nxt_start)
            if cur + 1 < len(FOOT):
                c2, s2, e2, _ = FOOT[cur + 1]
                nimg = push(self.reader(c2, e2 - s2).frame(0), 1.0)
            else:
                nimg = self.cta_frame(CTA_START)
            img = img * (1 - x) + nimg * x
        return img

    def cta_frame(self, t):
        if self.cta_still is None:
            r = ClipReader(os.path.join(self.assets, "Raw Video", "IMG_0212.MOV"), 2.7)
            self.cta_still = r.frame(1.2).copy()
            r.close()
        z = 1.04 + 0.08 * ease_io(sec(t, CTA_START, DURATION))
        img = push(self.cta_still, z)
        return img * (1 - 0.18 * sec(t, CTA_BUTTON - 0.3, CTA_BUTTON + 0.3))

    def frame(self, t):
        mask = None
        if t < RING_START:
            base, mask = self.neon(t)
        elif t < RING_END:
            p = sec(t, RING_START, RING_END)
            bg, mask = self.neon(t)
            fo = shade(self.footage(t))
            r = 40 + ease_io(p) * 1150
            m = np.zeros((H, W), np.float32)
            cv2.circle(m, (W // 2, int(H * 0.48)), int(r), 1.0, -1, cv2.LINE_AA)
            m = m[..., None]
            base = fo * m + bg * (1 - m)
            ring = Neon()
            ring.c.arc(W / 2, H * 0.48, r, 0, 2 * math.pi)
            ring.stroke(1.0 - 0.7 * p, 8)
            mask = mask * (1 - m[..., 0]) + ring.mask()
        else:
            base = shade(self.footage(t))
        out = base + glow(mask) if mask is not None else base
        out = np.clip(out, 0, 255)
        trgb, ta = text_layer(self.typo, t)
        out = trgb * ta + out * (1 - ta)
        return out.astype(np.uint8)

    def close(self):
        for r in self.readers.values():
            r.close()


# ---------------------------------------------------------------------------
# Audio
# ---------------------------------------------------------------------------
def make_sfx(path, sr=48000):
    n = int((DURATION + 1) * sr)
    out = np.zeros(n, np.float32)
    rng = np.random.default_rng(5)

    def add(sig, t):
        i = int(t * sr)
        j = min(n, i + len(sig))
        out[i:j] += sig[: j - i]

    # soft thud when the price tag lands
    tt = np.arange(int(0.6 * sr)) / sr
    add((np.sin(2 * np.pi * (70 * tt - 25 * tt ** 2)) * np.exp(-tt * 7) * 0.5).astype(np.float32), 30.66)
    # airy shimmer swell for the ring reveal
    m = int(0.9 * sr)
    noise = rng.standard_normal(m).astype(np.float32)
    noise = np.convolve(noise, np.ones(6) / 6, mode="same")
    x = np.linspace(0, 1, m)
    tt = np.arange(m) / sr
    chime = sum(np.sin(2 * np.pi * f * tt) for f in (1318.5, 1975.5, 2637)) / 3
    add(((noise * 0.08 + chime * 0.12) * np.sin(np.pi * x) ** 2).astype(np.float32), RING_START - 0.1)
    # soft pop for the CTA button
    tt = np.arange(int(0.15 * sr)) / sr
    add((np.sin(2 * np.pi * (520 * tt + 2200 * tt ** 2)) * np.exp(-tt * 30) * 0.3).astype(np.float32),
        CTA_BUTTON)
    out = np.clip(out, -1, 1)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((out * 32767).astype(np.int16).tobytes())


def audio_filter():
    return (
        "[1:a]aresample=48000,highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,"
        "loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000,apad,asplit=2[vo][key];"
        f"[2:a]atrim=start={MUSIC_START}:duration={DURATION},asetpts=PTS-STARTPTS,aresample=48000,"
        "loudnorm=I=-27:TP=-8:LRA=11,aresample=48000,"
        f"afade=t=in:d=1.0,afade=t=out:st={DURATION - 1.5}:d=1.5,apad[mus];"
        "[mus][key]sidechaincompress=threshold=0.05:ratio=3:attack=40:release=500[duck];"
        "[3:a]aresample=48000,apad[sfx];"
        f"[vo][duck][sfx]amix=inputs=3:normalize=0:duration=first,atrim=0:{DURATION},"
        "volume=2.5dB,alimiter=limit=0.95,apad[aout]"
    )


# ---------------------------------------------------------------------------
def render(assets, out, preview, sfx_path):
    make_sfx(sfx_path)
    R = Renderer(assets)
    ow, oh = (540, 960) if preview else (W, H)
    venc = (["-c:v", "libx264", "-preset", "veryfast", "-crf", "24"] if preview
            else ["-c:v", "libx264", "-preset", "slow", "-crf", "16", "-profile:v", "high"])
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-i", os.path.join(assets, VO), "-i", os.path.join(assets, MUSIC), "-i", sfx_path,
         "-filter_complex", audio_filter() + f";[0:v]scale={ow}:{oh}:flags=lanczos[v]",
         "-map", "[v]", "-map", "[aout]", *venc, "-pix_fmt", "yuv420p",
         "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", str(DURATION), out],
        stdin=subprocess.PIPE)
    nframes = int(round(DURATION * FPS))
    for i in range(nframes):
        enc.stdin.write(R.frame(i / FPS).tobytes())
        if i % 150 == 0:
            print(f"  {i}/{nframes}", flush=True)
    enc.stdin.close()
    enc.wait()
    R.close()
    print("done ->", out)


STORY_TIMES = [
    (3.4, "01 HOOK", "0.0-4.7s"), (8.4, "02 TWIST", "4.7-9.2s"), (15.0, "03 FAMILY", "9.2-16.6s"),
    (21.0, "04 DOOR", "16.6-22.2s"), (26.2, "05 TRIP", "22.2-28.1s"), (32.0, "06 PRICE", "28.1-32.6s"),
    (32.95, "07 RING", "32.6-33.4s"), (34.6, "08 DEPAN", "IMG_0212"), (36.9, "09 INTERIOR", "IMG_0218"),
    (38.9, "10 DASHBOARD", "IMG_0217"), (41.3, "11 BELAKANG", "IMG_0215"), (43.6, "12 TAYAR", "IMG_0214"),
    (48.0, "13 CTA", "IMG_0212 still"),
]


def storyboard(assets, outdir):
    os.makedirs(outdir, exist_ok=True)
    R = Renderer(assets)
    # footage readers stream forward, so render in time order
    shots = []
    for t, name, note in STORY_TIMES:
        img = R.frame(t)
        Image.fromarray(img).save(os.path.join(outdir, name.replace(" ", "_").lower() + ".png"))
        shots.append((name, note, img))
    R.close()
    font = os.path.join(assets, FONT)
    tw, th, cols = 300, 533, 7
    rows = math.ceil(len(shots) / cols)
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * 14, rows * (th + 78) + 14), (22, 22, 22))
    d = ImageDraw.Draw(sheet)
    f1, f2 = ImageFont.truetype(font, 22), ImageFont.truetype(font, 17)
    for i, (name, note, img) in enumerate(shots):
        r, c = divmod(i, cols)
        x, y = 14 + c * (tw + 14), 14 + r * (th + 78)
        d.text((x, y + 4), name, font=f1, fill=GREEN_T)
        d.text((x, y + 36), note, font=f2, fill=(190, 190, 190))
        sheet.paste(Image.fromarray(img).resize((tw, th), Image.LANCZOS), (x, y + 66))
    sheet.save(os.path.join(outdir, "storyboard_sheet.jpg"), quality=92)
    print("storyboard ->", outdir)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", required=True, help='the "Video Claude" folder from Drive')
    ap.add_argument("--out")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--storyboard")
    ap.add_argument("--sfx", default="/tmp/alphard_sfx.wav")
    a = ap.parse_args()
    if a.storyboard:
        storyboard(a.assets, a.storyboard)
    if a.out:
        render(a.assets, a.out, a.preview, a.sfx)
