#!/usr/bin/env python3
"""Video 2: "Duit Rokok vs Type R" (Honda Civic FL5 Type R), neon style @ 110 BPM.

Assets (Drive folder "Video Claude"):
  Voiceover/Pusat Konvensyen CIDB.m4a     narration, 54 s
  Raw Video/IMG_9374.MOV  red + blue FL5 front 3/4 (7.2 s, HLG)
  Raw Video/IMG_9385.MOV  blue FL5 rear + red (3.3 s, 60p)
  Raw Video/IMG_9391.MOV  bucket seats (4.75 s, 60p)

Usage:
  python3 typer_rokok_video.py --assets "DIR/Video Claude" --storyboard OUTDIR
  python3 typer_rokok_video.py --assets "DIR/Video Claude" --out OUT.mp4 [--preview]
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from neon_engine import BEAT, Project, bt, count_up, ev, render, snap, storyboard  # noqa: E402
from neon_scenes import (GY, W, Neon, background, bill, calendar, cig_box, cigarette, coin,  # noqa: E402
                         ease, ground, hatch, neon_text, particles, person, piggy, pill, smoke)

DURATION = 54.0


def dust(n, t):
    for x, y, r, a in particles(45, t):
        n.c.new_path()
        n.c.arc(x, y, r, 0, 6.3)
        n.fill(a * 0.55)


def fade_in(lt, t, a, d=0.3):
    return ease(ev(lt, t, a, d))


# ---------------------------------------------------------------------------
# neon scenes  (lt = local seconds, t = global seconds; events snap to beats)
# ---------------------------------------------------------------------------
def s_hook(lt, t):
    """Cigarette burning, money floating up and dissolving into smoke."""
    n, f = Neon(), background()
    cy = 900
    k = fade_in(lt, t, 0.0, 0.5)
    ember_x = cigarette(n, W / 2 - 20, cy, 560, a=k, ember=k * (0.75 + 0.25 * math.sin(t * 7)),
                        burn=0.25 * min(1, lt / 7))
    smoke(n, ember_x + 6, cy - 40, t, a=k)
    # bills spawn on every beat from "duit" (4.4 s), rise along the smoke and fade away
    first = snap(3.9)
    for i in range(8):
        t0 = first + i * BEAT
        u = (t - t0) / 1.9
        if 0 <= u <= 1:
            y = cy - 60 - u * 420
            x = ember_x + math.sin(u * 4 + i) * 60 - 20
            bill(n, x, y, 0.7, a=(1 - u) ** 1.2, rot=math.sin(u * 3 + i) * 0.5)
    pill(n, W / 2, 1120, "LESAP JADI ASAP", 36, a=fade_in(lt, t, 5.18, 0.25))
    dust(n, t)
    return f, n


def s_math(lt, t):  # starts ~7.09
    n, f = Neon(), background()
    cig_box(n, W / 2 - 200, 720, 0.85, a=fade_in(lt, t, 0.0, 0.4))
    st = t - lt
    k = fade_in(lt, t, 8.08 - st, 0.2)
    if k > 0:
        pill(n, W / 2 + 190, 690 - 15 * (1 - k), "RM18.20", 54, a=k, filled=True)
        neon_text(n, W / 2 + 190, 790, "SEKOTAK", 30, a=k * 0.8)
    rows = [  # (abs time, label, value fn)
        (10.38, "SEHARI", lambda v: "1 KOTAK", None),
        (11.98, "SEBULAN", lambda v: f"RM{int(v):,}", 546),
        (14.16, "SETAHUN", lambda v: f"RM{int(v):,}", 6643),
    ]
    for j, (ta, lab, fmt, target) in enumerate(rows):
        k = fade_in(lt, t, ta - st, 0.2)
        if k <= 0:
            continue
        y = 990 + j * 105
        neon_text(n, W / 2 - 200, y, lab, 40, a=k * 0.75)
        v = count_up(lt, t, ta - st, 0.9, 0, target) if target else 0
        neon_text(n, W / 2 + 170, y, fmt(v), 62, a=k)
        n.c.new_path()
        n.c.move_to(160, y + 50)
        n.c.line_to(W - 160, y + 50)
        n.stroke(0.25 * k, 2)
    dust(n, t)
    return f, n


def s_tabung(lt, t):  # starts ~16.36
    n, f = Neon(), background()
    st = t - lt
    ground(n, GY - 120, 0.3)
    sx, sy = piggy(n, W / 2 - 180, 870, 0.72, a=fade_in(lt, t, 0.0, 0.4))
    # coins drop into the slot on each beat until "agak-agak"
    for i in range(5):
        t0 = snap(16.44) + i * BEAT
        u = (t - t0) / 0.32
        if 0 <= u <= 1.15:
            yy = sy - 260 + 260 * min(1, ease(min(u, 1)))
            coin(n, sx, yy, 24, a=1 - max(0, u - 0.9) * 4)
    pill(n, W / 2 - 180, 560, "TABUNG KERETA", 34, a=fade_in(lt, t, 17.22 - st, 0.25))
    kc = ev(lt, t, 18.72 - st, 1.2)
    if kc > 0:
        hatch(n, W / 2 + 250, 990, 0.42, draw=ease(kc))
        # dashed path piggy -> car
        n.c.set_dash([14, 14], -t * 60)
        n.c.new_path()
        n.c.move_to(W / 2 + 30, 860)
        n.c.curve_to(W / 2 + 80, 760, W / 2 + 140, 760, W / 2 + 190, 820)
        n.stroke(0.6 * ease(kc), 4)
        n.c.set_dash([])
    kq = fade_in(lt, t, 20.9 - st, 0.2)
    if kq > 0:
        neon_text(n, W / 2 + 250, 740 + math.sin(t * 3) * 8, "?", 130, a=kq)
    dust(n, t)
    return f, n


def s_answer(lt, t):  # starts ~21.82
    n, f = Neon(), background()
    st = t - lt
    cols, rows = 10, 7
    cw, ch, gap = 58, 40, 14
    x0 = W / 2 - (cols * (cw + gap) - gap) / 2
    y0 = 520
    filled = count_up(lt, t, 22.5 - st, 1.6, 0, cols * rows)
    for r in range(rows):
        for c_ in range(cols):
            idx = (rows - 1 - r) * cols + c_          # fill bottom-up
            on = idx < filled
            n.c.new_path()
            n.c.rectangle(x0 + c_ * (cw + gap), y0 + r * (ch + gap), cw, ch)
            if on:
                n.fill(0.18)
                n.c.rectangle(x0 + c_ * (cw + gap), y0 + r * (ch + gap), cw, ch)
                n.stroke(0.9, 3.5)
            else:
                n.stroke(0.18, 2)
    v = count_up(lt, t, 22.5 - st, 1.6, 0, 15000)
    k = fade_in(lt, t, 22.5 - st, 0.15)
    neon_text(n, W / 2, 985, f"{int(v):,} KOTAK", 82, a=k)
    k2 = ev(lt, t, 25.54 - st, 0.25)
    if k2 > 0:
        neon_text(n, W / 2, 1120 + 30 * (1 - ease(k2)), "= RM273,000", 92 * (1.25 - 0.25 * ease(k2)),
                  a=ease(k2))
    dust(n, t)
    return f, n


def s_years(lt, t):  # starts ~27.82
    n, f = Neon(), background()
    st = t - lt
    ground(n, GY - 60, 0.3)
    morph = ev(lt, t, 30.66 - st, 1.6)
    k0 = fade_in(lt, t, 0.0, 0.4)
    person(n, 300, GY - 60, 0.95, a=k0 * (1 - ease(morph)), kind="adult", walk=t * 0.8)
    if morph > 0:
        person(n, 300, GY - 60, 0.95, a=ease(morph), kind="elder", walk=t * 0.5)
    if morph <= 0:
        calendar(n, W / 2 + 180, 800, 0.95, a=k0, text="1", sub="KOTAK / HARI")
    else:
        yrs = count_up(lt, t, 30.66 - st, 1.7, 0, 41)
        calendar(n, W / 2 + 180, 800, 0.95, a=1, text=f"{int(round(yrs))}", sub="TAHUN")
    pill(n, W / 2 + 180, 1010, "BARU CUKUP", 34, a=fade_in(lt, t, 32.28 - st, 0.25))
    dust(n, t)
    return f, n


def s_impian(lt, t):  # starts ~33.82
    n, f = Neon(), background()
    st = t - lt
    brk = ev(lt, t, 34.62 - st, 0.35)
    gone = ev(lt, t, 35.2 - st, 0.6)
    a = fade_in(lt, t, 0.0, 0.3) * (1 - gone)
    if a > 0:
        ex = cigarette(n, W / 2, 760 + 120 * ease(gone), 460, a=a, ember=(1 - brk) * a, broken=ease(brk))
        if brk < 1:
            smoke(n, ex + 6, 720, t, a=a * (1 - brk))
        if 0 < brk < 1:  # snap flash lines
            for j in range(4):
                ang = j * math.pi / 2 + 0.6
                n.c.new_path()
                n.c.move_to(W / 2 + math.cos(ang) * 40, 760 + math.sin(ang) * 40)
                n.c.line_to(W / 2 + math.cos(ang) * (60 + 60 * brk), 760 + math.sin(ang) * (60 + 60 * brk))
                n.stroke(1 - brk, 5)
    kp = fade_in(lt, t, 35.98 - st, 0.4)
    if kp > 0:
        piggy(n, W / 2, 900, 0.8 * (0.85 + 0.15 * ease(kp)), a=kp)
        for j in range(6):  # sparkles
            ang = t * 0.8 + j * math.pi / 3
            sx, sy = W / 2 + math.cos(ang) * 290, 900 + math.sin(ang) * 210
            r = 12 + 6 * math.sin(t * 5 + j)
            n.c.new_path()
            n.c.move_to(sx - r, sy)
            n.c.line_to(sx + r, sy)
            n.c.move_to(sx, sy - r)
            n.c.line_to(sx, sy + r)
            n.stroke(kp * 0.8, 3)
        pill(n, W / 2, 600, "TABUNG IMPIAN", 40, a=fade_in(lt, t, 36.36 - st, 0.25), filled=True)
    dust(n, t)
    return f, n


ANIM = [
    (0.0, snap(6.93), s_hook),
    (snap(6.93), snap(16.1), s_math),
    (snap(16.1), snap(21.75), s_tabung),
    (snap(21.75), snap(28.0), s_answer),
    (snap(28.0), snap(33.6), s_years),
    (snap(33.6), bt(71), s_impian),
]

CAPTIONS = [
    (0.88, 2.90, "Hari-hari beli *rokok,*"),
    (2.94, 4.88, "pernah tak korang kira berapa duit"),
    (4.92, 6.90, "dah *lesap* menjadi *asap?*"),
    (6.96, 10.34, "Sekotak *RM18.20,*"),
    (10.38, 11.94, "sehari *sekotak,*"),
    (11.98, 14.12, "sebulan dah *RM500 lebih,*"),
    (14.16, 16.10, "setahun *RM6,000 lebih.*"),
    (16.16, 18.68, "Kalau duit tu masuk *tabung kereta,*"),
    (18.72, 21.80, "agak-agak berapa kotak baru dapat sebiji *Type R?*"),
    (21.84, 24.80, "Jawapannya *15,000 kotak,*"),
    (24.84, 28.04, "nilainya *RM273,000.*"),
    (28.08, 30.62, "Tapi sehari sekotak,"),
    (30.66, 33.62, "*41 tahun* juga lah baru kumpul."),
    (33.66, 35.94, "Tak apa, *kurangkan rokok,*"),
    (35.98, 37.76, "mulakan *tabung impian* dulu."),
    (37.80, 39.16, "Kalau korang tengah mencari"),
    (39.20, 43.86, "*FL5 Type R Racing Black* tahun *2025,*"),
    (43.90, 46.38, "saya ada *2 unit ready stock* di showroom,"),
    (46.42, 49.38, "harga *RM273,000.*"),
    (49.42, 51.10, "Nak tengok unit dan detail?"),
    (51.14, DURATION, "Komen *\"NAK\",* saya DM korang."),
]

FOOT = [  # (clip, b0, b1, src_offset, zoom, cx, cy) - cuts every 2 beats
    ("IMG_9374", 69, 73, 0.00, 1.00, 0.50, 0.50),   # ring reveal: red + blue FL5
    ("IMG_9374", 73, 75, 2.40, 1.50, 0.55, 0.60),   # red FL5 front punch-in
    ("IMG_9385", 75, 77, 0.00, 1.00, 0.50, 0.50),   # blue rear
    ("IMG_9385", 77, 79, 1.20, 1.80, 0.69, 0.68),   # exhaust tips
    ("IMG_9391", 79, 81, 0.00, 1.00, 0.50, 0.50),   # bucket seats
    ("IMG_9374", 81, 83, 4.00, 1.00, 0.50, 0.50),   # 2 unit ready stock
    ("IMG_9374", 83, 85, 5.30, 1.25, 0.50, 0.55),
    ("IMG_9391", 85, 87, 1.60, 1.30, 0.50, 0.50),   # harga
    ("IMG_9385", 87, 89, 2.10, 1.10, 0.50, 0.50),
    ("IMG_9391", 89, 91, 3.30, 1.15, 0.50, 0.50),
    ("IMG_9374", 91, 99, 2.80, 1.00, 0.50, 0.50),   # CTA
]
CLIP_DUR = {"IMG_9374": 7.185, "IMG_9385": 3.30, "IMG_9391": 4.75}
CHIPS = [("FL5 TYPE R 2025", 72, 79), ("2 UNIT READY STOCK", 81, 85), ("RM273,000", 86, 91)]

SFX = ([("coin", snap(16.44) + i * BEAT + 0.3) for i in range(5)]
       + [("pop", snap(x)) for x in (8.08, 10.38, 11.98, 14.16)]
       + [("thud", snap(25.54)), ("thud", snap(34.62)), ("shimmer", snap(36.36)),
          ("shimmer", bt(69)), ("pop", bt(94))])

STORY = [
    (5.6, "01 HOOK", "0-7.1s rokok jadi asap"), (14.9, "02 KIRA", "7.1-16.4s RM18.20 > setahun"),
    (21.3, "03 TABUNG", "16.4-21.8s tabung > Type R?"), (26.4, "04 JAWAPAN", "21.8-27.8s 15,000 kotak"),
    (32.6, "05 41 TAHUN", "27.8-33.8s umur > 41 tahun"), (36.9, "06 IMPIAN", "33.8-37.6s patah rokok"),
    (38.2, "07 RING", "37.6-38.7s"), (40.0, "08 DEPAN", "IMG_9374"), (41.0, "09 BELAKANG", "IMG_9385"),
    (42.5, "10 EKZOS", "IMG_9385 zoom"), (43.6, "11 KERUSI", "IMG_9391"), (44.8, "12 2 UNIT", "IMG_9374"),
    (47.4, "13 HARGA", "IMG_9391 zoom"), (52.5, "14 CTA", "IMG_9374"),
]


def project(assets):
    return Project(
        assets=assets, duration=DURATION, vo="Voiceover/Pusat Konvensyen CIDB.m4a",
        header_label="DUIT ROKOK", header_title="Berapa Kotak Untuk Type R?",
        captions=CAPTIONS, anim=ANIM, ring=(69, 71), foot=FOOT, clip_dur=CLIP_DUR,
        chips=CHIPS, cta_beat=94, sfx=SFX)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", required=True)
    ap.add_argument("--out")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--storyboard")
    ap.add_argument("--sfx", default="/tmp/typer_sfx.wav")
    a = ap.parse_args()
    P = project(a.assets)
    if a.storyboard:
        storyboard(P, STORY, a.storyboard)
    if a.out:
        render(P, a.out, a.preview, a.sfx)
