#!/usr/bin/env python3
"""Video 2: "Duit Rokok vs Civic FL5 Type R", neon style @ 110 BPM.

Assets (Drive folder "Video Claude"):
  Voiceover/Civic FL5 Type-R              narration (m4a, 55 s) - run studio_voice.py first
  Raw Video/IMG_9374.MOV  red + blue FL5 front 3/4 (7.2 s, HLG)
  Raw Video/IMG_9385.MOV  blue FL5 rear + red (3.3 s, 60p)
  Raw Video/IMG_9391.MOV  bucket seats (4.75 s, 60p)

Usage:
  python3 studio_voice.py "DIR/Video Claude/Voiceover/Civic FL5 Type-R" vo_studio.wav --deep-filter BIN
  python3 typer_rokok_video.py --assets "DIR/Video Claude" --studio-vo vo_studio.wav --storyboard OUTDIR
  python3 typer_rokok_video.py --assets "DIR/Video Claude" --studio-vo vo_studio.wav --out OUT.mp4 [--preview]
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from neon_engine import (BEAT, VO_PREMASTERED, Project, bt, count_up, ev, render, snap,  # noqa: E402
                         storyboard)
from neon_scenes import (GY, W, Neon, background, bill, calendar, cig_box, cigarette, coin,  # noqa: E402
                         ease, ground, hatch, neon_text, particles, person, pill, smoke, tabung_ayam)

DURATION = 55.0


def dust(n, t):
    for x, y, r, a in particles(45, t):
        n.c.new_path()
        n.c.arc(x, y, r, 0, 6.3)
        n.fill(a * 0.55)


def fade_in(lt, t, a, d=0.3):
    return ease(ev(lt, t, a, d))


def at(lt, t, abs_t, d=0.3):
    """fade-in progress for an event given in absolute (voice-over) time."""
    return fade_in(lt, t, abs_t - (t - lt), d)


# ---------------------------------------------------------------------------
# neon scenes  (lt = local seconds, t = global seconds; events snap to beats)
# ---------------------------------------------------------------------------
def s_hook(lt, t):
    """Cigarette burning, money floating up and dissolving into smoke."""
    n, f = Neon(), background()
    cy = 900
    k = fade_in(lt, t, 0.0, 0.5)
    ember_x = cigarette(n, W / 2 - 20, cy, 560, a=k, ember=k * (0.75 + 0.25 * math.sin(t * 7)),
                        burn=0.25 * min(1, lt / 6.5))
    smoke(n, ember_x + 6, cy - 40, t, a=k)
    first = snap(3.3)  # "duit korang"
    for i in range(8):
        t0 = first + i * BEAT
        u = (t - t0) / 1.9
        if 0 <= u <= 1:
            y = cy - 60 - u * 420
            x = ember_x + math.sin(u * 4 + i) * 60 - 20
            bill(n, x, y, 0.7, a=(1 - u) ** 1.2, rot=math.sin(u * 3 + i) * 0.5)
    pill(n, W / 2, 1120, "LESAP JADI ASAP", 36, a=at(lt, t, 4.54, 0.25))
    dust(n, t)
    return f, n


def s_math(lt, t):
    n, f = Neon(), background()
    cig_box(n, W / 2 - 200, 720, 0.85, a=fade_in(lt, t, 0.0, 0.4))
    k = at(lt, t, 7.36, 0.2)
    if k > 0:
        pill(n, W / 2 + 190, 690 - 15 * (1 - k), "RM18.20", 54, a=k, filled=True)
        neon_text(n, W / 2 + 190, 790, "SEKOTAK", 30, a=k * 0.8)
    st = t - lt
    rows = [(9.26, "SEHARI", lambda v: "1 KOTAK", None),
            (10.82, "SEBULAN", lambda v: f"RM{int(v):,}", 546),
            (12.64, "SETAHUN", lambda v: f"RM{int(v):,}", 6643)]
    for j, (ta, lab, fmt, target) in enumerate(rows):
        k = at(lt, t, ta, 0.2)
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


def s_tabung(lt, t):
    n, f = Neon(), background()
    st = t - lt
    ground(n, GY - 110, 0.3)
    sx, sy = tabung_ayam(n, W / 2 - 190, 890, 0.72, a=fade_in(lt, t, 0.0, 0.4),
                         fill=0.35 * ease(ev(lt, t, 15.12 - st, 2.8)))
    for i in range(5):  # coins drop into the slot on the beat
        t0 = snap(15.12) + i * BEAT
        u = (t - t0) / 0.32
        if 0 <= u <= 1.15:
            yy = sy - 260 + 260 * min(1, ease(min(u, 1)))
            coin(n, sx, yy, 24, a=1 - max(0, u - 0.9) * 4)
    pill(n, W / 2 - 190, 560, "TABUNG KERETA", 34, a=at(lt, t, 16.46, 0.25))
    kc = ev(lt, t, 18.26 - st, 1.2)
    if kc > 0:
        hatch(n, W / 2 + 255, 1000, 0.42, draw=ease(kc))
        n.c.set_dash([14, 14], -t * 60)
        n.c.new_path()
        n.c.move_to(W / 2 + 10, 800)
        n.c.curve_to(W / 2 + 70, 720, W / 2 + 140, 730, W / 2 + 190, 820)
        n.stroke(0.6 * ease(kc), 4)
        n.c.set_dash([])
    kq = at(lt, t, 20.66, 0.2)
    if kq > 0:
        neon_text(n, W / 2 + 255, 750 + math.sin(t * 3) * 8, "?", 130, a=kq)
    dust(n, t)
    return f, n


def s_answer(lt, t):
    n, f = Neon(), background()
    st = t - lt
    cols, rows = 10, 7
    cw, ch, gap = 58, 40, 14
    x0 = W / 2 - (cols * (cw + gap) - gap) / 2
    y0 = 520
    filled = count_up(lt, t, 22.58 - st, 1.6, 0, cols * rows)
    for r in range(rows):
        for c_ in range(cols):
            idx = (rows - 1 - r) * cols + c_
            n.c.new_path()
            n.c.rectangle(x0 + c_ * (cw + gap), y0 + r * (ch + gap), cw, ch)
            if idx < filled:
                n.fill(0.18)
                n.c.rectangle(x0 + c_ * (cw + gap), y0 + r * (ch + gap), cw, ch)
                n.stroke(0.9, 3.5)
            else:
                n.stroke(0.18, 2)
    v = count_up(lt, t, 22.58 - st, 1.6, 0, 15000)
    neon_text(n, W / 2, 985, f"{int(v):,} KOTAK", 82, a=at(lt, t, 22.58, 0.15))
    k2 = ev(lt, t, 25.42 - st, 0.25)
    if k2 > 0:
        neon_text(n, W / 2, 1120 + 30 * (1 - ease(k2)), "= RM273,000", 92 * (1.25 - 0.25 * ease(k2)),
                  a=ease(k2))
    dust(n, t)
    return f, n


def s_years(lt, t):
    n, f = Neon(), background()
    st = t - lt
    ground(n, GY - 60, 0.3)
    morph = ev(lt, t, 29.86 - st, 1.6)
    k0 = fade_in(lt, t, 0.0, 0.4)
    person(n, 300, GY - 60, 0.95, a=k0 * (1 - ease(morph)), kind="adult", walk=t * 0.8)
    if morph > 0:
        person(n, 300, GY - 60, 0.95, a=ease(morph), kind="elder", walk=t * 0.5)
        yrs = count_up(lt, t, 29.86 - st, 1.4, 0, 41)
        calendar(n, W / 2 + 180, 800, 0.95, a=1, text=f"{int(round(yrs))}", sub="TAHUN")
    else:
        calendar(n, W / 2 + 180, 800, 0.95, a=k0, text="1", sub="KOTAK / HARI")
    pill(n, W / 2 + 180, 1010, "BARU TERKUMPUL", 32, a=at(lt, t, 31.08, 0.25))
    dust(n, t)
    return f, n


def s_stop(lt, t):
    """"Tak apa, berhenti rokok ataupun kurangkan rokok" - cigarette snaps."""
    n, f = Neon(), background()
    st = t - lt
    brk = ev(lt, t, 32.86 - st, 0.35)
    a = fade_in(lt, t, 0.0, 0.3)
    ex = cigarette(n, W / 2, 800, 480, a=a, ember=(1 - brk) * a, broken=ease(brk))
    if brk < 1:
        smoke(n, ex + 6, 760, t, a=a * (1 - brk))
    if 0 < brk < 1:
        for j in range(4):
            ang = j * math.pi / 2 + 0.6
            n.c.new_path()
            n.c.move_to(W / 2 + math.cos(ang) * 40, 800 + math.sin(ang) * 40)
            n.c.line_to(W / 2 + math.cos(ang) * (60 + 60 * brk), 800 + math.sin(ang) * (60 + 60 * brk))
            n.stroke(1 - brk, 5)
    pill(n, W / 2, 600, "BERHENTI", 40, a=at(lt, t, 32.86, 0.25), filled=True)
    pill(n, W / 2, 1010, "ATAU KURANGKAN", 36, a=at(lt, t, 34.32, 0.25))
    dust(n, t)
    return f, n


def s_cukup(lt, t):
    """"untuk sesiapa yang tak merokok, dah cukup duit nak beli FL5" - full tabung, car arrives."""
    n, f = Neon(), background()
    st = t - lt
    ground(n, 1150, 0.35, 60, W - 60)
    fill = ease(ev(lt, t, 36.24 - st, 2.4))
    k = fade_in(lt, t, 0.0, 0.4)
    sx, sy = tabung_ayam(n, W / 2 - 200, 900, 0.68, a=k, fill=0.15 + 0.8 * fill)
    for i in range(4):
        t0 = snap(36.24) + i * BEAT
        u = (t - t0) / 0.32
        if 0 <= u <= 1.15:
            coin(n, sx, sy - 240 + 240 * min(1, ease(min(u, 1))), 22, a=1 - max(0, u - 0.9) * 4)
    pill(n, W / 2 - 200, 590, "DUIT CUKUP", 40, a=at(lt, t, 38.72, 0.25), filled=True)
    drive = ease(ev(lt, t, 39.68 - st, 0.7))
    if drive > 0:
        x = W + 260 - (W + 260 - (W / 2 + 230)) * drive
        hatch(n, x, 1150, 0.42, wheel_rot=-t * 14 * (1 - drive))
        if drive < 1:
            for j, yy in enumerate((1040, 1080, 1115)):
                n.c.new_path()
                n.c.move_to(x + 180 + j * 10, yy)
                n.c.line_to(x + 260 + j * 20, yy)
                n.stroke(0.6 * (1 - drive), 4)
    dust(n, t)
    return f, n


ANIM = [
    (0.0, snap(6.55), s_hook),
    (snap(6.55), snap(14.6), s_math),
    (snap(14.6), snap(21.4), s_tabung),
    (snap(21.4), snap(27.2), s_answer),
    (snap(27.2), snap(32.0), s_years),
    (snap(32.0), snap(35.6), s_stop),
    (snap(35.6), bt(76), s_cukup),
]

CAPTIONS = [
    (0.00, 1.46, "Hari-hari beli *rokok,*"),
    (1.50, 3.00, "tapi korang pernah terfikir tak"),
    (3.04, 4.50, "berapa banyak duit korang"),
    (4.54, 6.58, "dah *lesap* menjadi *asap?*"),
    (6.62, 9.22, "Dahlah sekotak *RM18.20.*"),
    (9.26, 10.78, "Kalau sehari *sekotak,*"),
    (10.82, 12.60, "sebulan dah *RM500 lebih,*"),
    (12.64, 14.62, "setahun *RM6,000 lebih.*"),
    (14.66, 18.22, "Kalau duit tu dimasukkan dalam *tabung beli kereta,*"),
    (18.26, 21.60, "agak-agak berapa banyak kotak baru dapat *Civic FL5?*"),
    (21.64, 24.18, "Jawapan dia *15,000 kotak*"),
    (24.22, 27.24, "dan nilai dia adalah *RM273,000.*"),
    (27.28, 29.82, "Tapi kalau sehari sekotak,"),
    (29.86, 32.04, "*41 tahun* juga lah baru terkumpul."),
    (32.08, 33.68, "Tak apa, *berhenti rokok*"),
    (33.72, 35.70, "ataupun *kurangkan rokok.*"),
    (35.74, 38.52, "Tapi untuk sesiapa yang *tak merokok,*"),
    (38.56, 40.66, "dah *cukup duit* nak beli *FL5,*"),
    (40.70, 44.30, "saya ada *2 unit* tahun *2025,*"),
    (44.34, 47.18, "*Racing Black* yang *ready* di showroom."),
    (47.22, 49.84, "Harganya *RM270,000.*"),
    (49.88, 51.54, "Nak tengok detail?"),
    (51.58, DURATION, "Komen *\"NAK\",* saya DM korang."),
]

FOOT = [  # (clip, b0, b1, src_offset, zoom, cx, cy) - cuts every 2 beats
    ("IMG_9374", 74, 78, 0.00, 1.00, 0.50, 0.50),   # ring reveal: 2 units
    ("IMG_9374", 78, 80, 2.40, 1.50, 0.55, 0.60),   # red FL5 front punch-in
    ("IMG_9385", 80, 82, 0.00, 1.00, 0.50, 0.50),   # blue rear
    ("IMG_9385", 82, 84, 1.20, 1.80, 0.69, 0.68),   # exhaust tips
    ("IMG_9391", 84, 86, 0.00, 1.00, 0.50, 0.50),   # bucket seats
    ("IMG_9374", 86, 88, 4.00, 1.00, 0.50, 0.50),   # harga
    ("IMG_9391", 88, 90, 1.60, 1.30, 0.50, 0.50),
    ("IMG_9385", 90, 92, 2.10, 1.10, 0.50, 0.50),
    ("IMG_9391", 92, 94, 3.30, 1.15, 0.50, 0.50),
    ("IMG_9374", 94, 101, 2.80, 1.00, 0.50, 0.50),  # CTA
]
CLIP_DUR = {"IMG_9374": 7.185, "IMG_9385": 3.30, "IMG_9391": 4.75}
CHIPS = [("2 UNIT FL5 2025", 76, 81), ("RACING BLACK • READY STOCK", 81, 87), ("RM270,000", 88, 94)]

SFX = ([("coin", snap(15.12) + i * BEAT + 0.3) for i in range(5)]
       + [("coin", snap(36.24) + i * BEAT + 0.3) for i in range(4)]
       + [("pop", snap(x)) for x in (7.36, 9.26, 10.82, 12.64)]
       + [("thud", snap(25.42)), ("thud", snap(32.86)), ("shimmer", snap(38.72)),
          ("shimmer", bt(74)), ("pop", bt(95))])

STORY = [
    (5.4, "01 HOOK", "0-6.5s rokok jadi asap"), (13.9, "02 KIRA", "6.5-14.7s RM18.20 > setahun"),
    (21.0, "03 TABUNG AYAM", "14.7-21.3s tabung > FL5?"), (26.4, "04 JAWAPAN", "21.3-27.3s 15,000 kotak"),
    (31.6, "05 41 TAHUN", "27.3-32.2s"), (34.9, "06 BERHENTI", "32.2-35.5s rokok patah"),
    (40.2, "07 DUIT CUKUP", "35.5-40.4s tabung penuh > FL5"), (40.9, "08 RING", "40.4-41.5s"),
    (42.0, "09 2 UNIT", "IMG_9374"), (43.0, "10 DEPAN", "IMG_9374 zoom"), (45.0, "11 EKZOS", "IMG_9385 zoom"),
    (45.9, "12 KERUSI", "IMG_9391"), (48.5, "13 HARGA", "IMG_9391 zoom"), (53.5, "14 CTA", "IMG_9374"),
]


def project(assets, studio_vo=None):
    return Project(
        assets=assets, duration=DURATION,
        vo=os.path.abspath(studio_vo) if studio_vo else "Voiceover/Civic FL5 Type-R",
        vo_filter=VO_PREMASTERED if studio_vo else Project.vo_filter,
        header_label="DUIT ROKOK", header_title="Berapa Kotak Untuk FL5?",
        captions=CAPTIONS, anim=ANIM, ring=(74, 76), foot=FOOT, clip_dur=CLIP_DUR,
        chips=CHIPS, cta_beat=95, sfx=SFX)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", required=True)
    ap.add_argument("--studio-vo", help="voice-over already processed by studio_voice.py")
    ap.add_argument("--out")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--storyboard")
    ap.add_argument("--sfx", default="/tmp/typer_sfx.wav")
    a = ap.parse_args()
    P = project(a.assets, a.studio_vo)
    if a.storyboard:
        storyboard(P, STORY, a.storyboard)
    if a.out:
        render(P, a.out, a.preview, a.sfx)
