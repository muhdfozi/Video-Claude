"""Toyota Alphard Z 2023 — "gaji berapa layak?" — STYLE KIRA DETAIL (glass theme).
Source: user's version from another app (copy_FE5D9A80....mov, 1080x1920 SDR 60 fps) with a burned-in
header "TOYOTA ALPHARD Z 2023 RM245,000" (y ~290-750). Rules for this source:
- NO_ZOOM (header in pixels); colour exactly as the file (SDR, no grade).
- Glass only below the header (GLASS_TOP), every glass element placed below y ~860.
- Audio: identical timing to raw IMG_1340 (lag 0) -> cleaner raw audio + its transcript.
Calculated totals are shown exactly (user rule), not the rounded spoken figures.
Order rearranged: hook question -> car + price -> features -> the maths -> answer to the end -> CTA.
Times are SOURCE seconds.
"""
THEME = "glass"
ACCENT = "C8102E"
NO_ZOOM = True
GLASS_TOP = 780
AUDIO = "/home/user/work5/audio48k.wav"
K = [(0, 1.0, 0.5, 0.5)]

SEGMENTS = [
    dict(id="hook", a=(16.20, 20.95), v=104.80, keys=K,
         why="Hook = the question, over the best shot (front grille close-up, flash-forward)."),
    dict(id="intro", a=(0.00, 9.25), v=0.70, keys=K,
         why="Model, year, grade 4.5, mileage. Video +0.7 s skips the header's intro animation (POV)."),
    dict(id="price", a=(9.65, 15.55), keys=K, why="RM245,000 not yet on the road."),
    dict(id="feat1", a=(83.30, 87.62), keys=K, why="Features moved before the maths (answer stays the ending)."),
    dict(id="feat2", a=(91.05, 107.14), keys=K, why="Dropped the repeated 'tepi kiri kanan ada side step'."),
    dict(id="jom", a=(21.25, 22.40), keys=K, why="'Jom kita buat kira-kira' = chapter start."),
    dict(id="otr1", a=(22.45, 45.95), keys=K, why="Body price, road tax, insurance, processing fee."),
    dict(id="otr2", a=(46.05, 51.35), keys=K, why="Total OTR ~RM252,000."),
    dict(id="loan", a=(51.55, 57.45), keys=K, why="9-year loan, no down payment, ~RM2,800/month."),
    dict(id="rule", a=(58.20, 65.70), keys=K, why="1/3 salary rule: x3 = RM8,000+."),
    dict(id="answer", a=(65.75, 71.75), keys=K,
         why="Answer. Dropped 74-83 s: a false start + the same answer sentence repeated."),
    dict(id="cta", a=(107.14, 110.20), keys=K, why="CTA. Dropped 'Sekian, Assalamualaikum'."),
]

GRAPHICS = []
KEYPOINTS = []

GLASS = [
    dict(win=(22.45, 38.00), items=[
        dict(kind="card", title="Kos on the road", y=1000, rows=[(24.48, "Harga body", "RM245,000"),
                                                               (29.16, "Road tax", "RM840"),
                                                               (33.10, "Insurans · NCD 55%", "RM3,500")]),
    ]),
    dict(win=(46.05, 51.35), items=[
        dict(kind="label", text="Jumlah", y=880),
        dict(kind="counter", at=48.50, to=252140, frm=0, dur=1.3, lab="On the road", sub="245,000 + 840 + 3,500 + 2,800", accent=True, y=1180),
    ]),
    dict(win=(51.55, 57.45), items=[
        dict(kind="card", title="Kira loan", y=1000, rows=[(53.12, "Tempoh loan", "9 tahun"),
                                                         (54.56, "Down payment", "Tiada"),
                                                         (56.74, "Bulanan (anggaran)", 2800, "total")]),
    ]),
    dict(win=(58.20, 65.70), items=[
        dict(kind="label", text="Rule 1/3 gaji", y=880),
        dict(kind="cards", y=960, items=[(59.24, "01 · Rule", "Ansuran ≤ 1/3 gaji"),
                                         (62.06, "02 · Kira", "RM2,800 × 3"),
                                         (64.18, "03 · Hasil", "RM8,400 sebulan")]),
    ]),
    dict(win=(65.75, 999), items=[
        dict(kind="label", text="Jawapan", y=880),
        dict(kind="counter", at=66.30, to=8400, frm=0, dur=1.4, lab="Gaji layak", sub="RM2,800 × 3 = RM8,400 sebulan", accent=True, y=1180),
    ]),
]

OVERLAYS = [
    dict(kind="counter_pill", at=16.22, dur=4.6, to=252140, frm=0, dur_roll=1.4, lab="Alphard Z · on the road", sub="Gaji berapa layak?"),
    dict(kind="pill", at=4.18, dur=2.2, text="Grade *4.5*"),
    dict(kind="pill", at=6.72, dur=2.4, text="Mileage *25,000 km*"),
    dict(kind="pill", at=11.72, dur=3.4, text="RM245,000 · *belum on the road*"),
    dict(kind="pill", at=87.00, dur=1.6, text="*Side step* kiri kanan"),
    dict(kind="pill", at=91.10, dur=1.2, text="*Full ladder*"),
    dict(kind="pill", at=92.26, dur=1.2, text="*Moonroof*"),
    dict(kind="pill", at=94.18, dur=1.4, text="*Roof monitor*"),
    dict(kind="pill", at=96.66, dur=1.5, text="Toyota *T-Mate*"),
    dict(kind="pill", at=98.26, dur=1.0, text="*Parking assist*"),
    dict(kind="pill", at=99.10, dur=1.6, text="Digital *inner mirror*"),
    dict(kind="pill", at=100.88, dur=1.2, text="*Blind spot* monitoring"),
    dict(kind="pill", at=102.06, dur=1.1, text="*360* camera"),
    dict(kind="pill", at=103.76, dur=2.6, text="Lampu *DRL* original"),
    dict(kind="title", at=21.30, dur=1.2, chip="JOM KIRA", accent="Gaji layak?"),
    dict(kind="pill", at=41.80, dur=3.6, text="Processing fee *RM2,800* · fixed"),
    dict(kind="pill", at=108.46, dur=2.0, text="Berminat? Tekan *link*"),
]

MUSIC = dict(file="/home/user/drive_dl/Music/music1.mp4", start=1.6, lufs=-28, duck_db=8, fade_out=1.8)
