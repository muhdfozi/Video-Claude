"""Mercedes CLA180 SE 2023 — "gaji berapa layak?" — STYLE KIRA DETAIL (glass), PREVIEW first.
Source: user's version from another app (copy_264E3657....mov, 1080x1920 SDR 60 fps, 85.75 s) with a burned-in
header "MERCEDES CLA180 SE 2023 RM183,000" (ends y ~725). NO_ZOOM, glass only below the header, colour as file.
No raw file this time -> audio from the same file.
Exact totals (user rule): OTR 183,000 + 2,700 + 70 + 2,800 = RM188,570 (presenter says "188,000").
The presenter never states the salary answer; the rule-1/3 answer (RM2,000 x 3 = RM6,000, anggaran) is an EDITOR
ADDITION to close the hook question, consistent with his other videos — flagged to the user for approval.
Whisper fixes: Rocktex = road tax, "under load" = on the road, "semi ladder" = semi leather, RM7,000/RM6,000 = km.
Order: hook -> car + price -> features & mileage -> the maths -> answer + CTA. Times = SOURCE seconds.
"""
THEME = "glass"
ACCENT = "C8102E"
NO_ZOOM = True
GLASS_TOP = 780
VAD_DB = -31          # this file's audio was boosted by the other app: the auto threshold clipped soft words
K = [(0, 1.0, 0.5, 0.5)]

SEGMENTS = [
    dict(id="hook", a=(15.80, 21.12), v=29.60, keys=K,
         why="Hook = the salary question over the front 3/4 walk-around (flash-forward). Dropped 'Jadi'."),
    dict(id="intro", a=(0.00, 10.40), v=0.70, keys=K,
         why="Model, year, grade 5A, mileage. Video +0.7 s skips the header intro animation."),
    dict(id="price", a=(10.90, 14.72), keys=K, why="Selling price RM183,000."),
    dict(id="feat", a=(52.50, 66.12), keys=K, why="Semi leather, SE seat design (executive, not AMG), SE steering."),
    dict(id="mileage", a=(66.20, 72.95), keys=K, why="Mileage: 7,000 km driven, auction report 6,000 km."),
    dict(id="seats", a=(73.00, 80.55), keys=K, why="Electronic + memory seat, coupe design, frameless."),
    dict(id="otr1", a=(21.14, 39.55), keys=K, why="Body price, insurance, road tax (1.3 turbo = RM70), processing fee."),
    dict(id="otr2", a=(39.60, 43.12), keys=K, why="Total on the road."),
    dict(id="loan", a=(43.16, 52.05), keys=K, why="9-year full loan, no down payment, ~RM2,000+/month."),
    dict(id="cta", a=(80.60, 84.30), keys=K, why="CTA. Dropped 'Assalamualaikum'."),
]

GRAPHICS = []
KEYPOINTS = []

GLASS = [
    dict(win=(21.14, 30.20), items=[
        dict(kind="card", title="Kos on the road", y=1000, rows=[(23.10, "Harga body", "RM183,000"),
                                                               (27.92, "Insurans · NCD 55%", "RM2,700")]),
    ]),
    dict(win=(35.30, 39.55), items=[
        dict(kind="card", title="Kos on the road", y=1000, rows=[(23.10, "Harga body", "RM183,000"),
                                                               (27.92, "Insurans · NCD 55%", "RM2,700"),
                                                               (35.54, "Road tax · 1.3 turbo", "RM70"),
                                                               (38.72, "Processing fee", "RM2,800")]),
    ]),
    dict(win=(39.60, 43.12), items=[
        dict(kind="label", text="Jumlah", y=880),
        dict(kind="counter", at=41.44, to=188570, frm=0, dur=1.2, lab="On the road", sub="183,000 + 2,700 + 70 + 2,800", accent=True, y=1180),
    ]),
    dict(win=(43.16, 51.98), items=[
        dict(kind="card", title="Kira loan", y=1000, rows=[(45.24, "Tempoh loan", "9 tahun"),
                                                         (46.28, "Down payment", "Tiada (full loan)"),
                                                         (50.20, "Bulanan (anggaran)", "± RM2,000+")]),
    ]),
    dict(win=(80.60, 999), items=[
        dict(kind="label", text="Gaji layak · rule 1/3", y=880),
        dict(kind="counter", at=80.70, to=6000, frm=0, dur=1.2, lab="Gaji (anggaran)", sub="ansuran RM2,000 × 3", accent=True, y=1180),
    ]),
]

OVERLAYS = [
    dict(kind="counter_pill", at=15.86, dur=5.0, to=188570, frm=0, dur_roll=1.4, lab="CLA180 SE · on the road", sub="Gaji berapa layak?"),
    dict(kind="pill", at=6.68, dur=1.8, text="Grade *5A*"),
    dict(kind="pill", at=8.28, dur=2.2, text="Mileage *6,000 km*"),
    dict(kind="pill", at=12.96, dur=2.0, text="Harga jual *RM183,000*"),
    dict(kind="pill", at=55.44, dur=1.4, text="*Semi leather*"),
    dict(kind="pill", at=57.86, dur=2.4, text="Seat *SE* · design executive"),
    dict(kind="pill", at=61.06, dur=1.6, text="Bukan *AMG*"),
    dict(kind="pill", at=63.66, dur=2.4, text="Steering *SE spec*"),
    dict(kind="pill", at=69.40, dur=1.6, text="Dah jalan *7,000 km*"),
    dict(kind="pill", at=71.70, dur=1.4, text="Auction report *6,000 km*"),
    dict(kind="pill", at=74.68, dur=1.2, text="*Electronic* seat"),
    dict(kind="pill", at=75.94, dur=1.0, text="*Memory* seat"),
    dict(kind="pill", at=78.32, dur=1.0, text="*Coupe* design"),
    dict(kind="pill", at=79.92, dur=1.2, text="*Frameless*"),
    dict(kind="pill", at=32.16, dur=2.6, text="Enjin *1.3 turbo*"),
    dict(kind="pill", at=82.84, dur=2.0, text="Berminat? Tekan *link*"),
]

MUSIC = dict(file="/home/user/drive_dl/Music/music1.mp4", start=1.6, lufs=-28, duck_db=8, fade_out=1.8)
