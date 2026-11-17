"""Mercedes CLA180 SE 2023 (take 2, copy_E3163EA1....mov, 99 s, SDR 60 fps, burned-in header) — STYLE KIRA DETAIL.
Voice: "high-end mic in a studio" = DeepFilterNet3 noise removal (enhance_voice.py, AUDIO below) + VOICE="studio" chain.
Exact totals (user rule): OTR 183,000 + 70 + 2,700 + 2,800 = RM188,570 (presenter: "188,000 lebih");
rule 1/3 (his own maths this time): RM2,100 x 3 = RM6,300 (he says "itulah gaji yang layak" without the number).
Whisper fixes: "1.3 daripada gaji" = 1/3, "semi-ladder" = semi leather, "kupih" = coupe, "GL/GA" n/a.
Order: hook -> car + price -> spec & features -> jom kira -> maths -> answer + CTA. Times = SOURCE seconds.
"""
THEME = "glass"
ACCENT = "C8102E"
NO_ZOOM = True
GLASS_TOP = 780
AUDIO = "/home/user/work8/audio48k_df.wav"
VOICE = "studio"
K = [(0, 1.0, 0.5, 0.5)]

SEGMENTS = [
    dict(id="hook", a=(16.66, 21.30), v=26.00, keys=K, why="Hook = salary question over the front 3/4 walk-around."),
    dict(id="intro", a=(0.00, 9.95), v=0.70, keys=K, why="Model, year, grade 5A, mileage 6,000 km (+0.7 s skips header intro)."),
    dict(id="price", a=(10.10, 15.98), keys=K, why="Body price RM183,000, not yet on the road."),
    dict(id="spec", a=(63.66, 70.45), keys=K, why="Lower spec of the CLA class."),
    dict(id="inside", a=(70.64, 77.98), keys=K, why="Semi leather seat (not AMG design), SE spec steering."),
    dict(id="meter", a=(78.00, 84.12), keys=K, why="Meter shows 7,000 km (1,000 over the auction 6,000)."),
    dict(id="exec", a=(84.20, 90.62), keys=K, why="Executive looks, electronic + memory seat."),
    dict(id="frameless", a=(90.90, 95.70), keys=K, why="Frameless because coupe design."),
    dict(id="jom", a=(21.58, 22.62), keys=K, why="'Jom kita buat kira-kira' opens the maths."),
    dict(id="otr1", a=(22.66, 40.55), keys=K, why="Body price, road tax (1.3 turbo), insurance, processing fee."),
    dict(id="otr2", a=(40.60, 44.92), keys=K, why="Total on the road."),
    dict(id="loan", a=(44.96, 51.62), keys=K, why="9-year full loan, no DP, ~RM2,100+/month."),
    dict(id="rule", a=(51.66, 58.62), keys=K, why="x3 because the instalment = 1/3 of salary."),
    dict(id="answer", a=(58.64, 63.62), keys=K, why="'Itulah gaji yang layak' -> RM6,300 on screen."),
    dict(id="cta", a=(95.98, 98.62), v=93.30, keys=K, why="CTA. Video moved before the header's exit glitch (~97.8 s)."),
]

GRAPHICS = []
KEYPOINTS = []

GLASS = [
    dict(win=(22.66, 36.85), items=[
        dict(kind="card", title="Kos on the road", y=1000, rows=[(23.70, "Harga body", "RM183,000"),
                                                               (27.18, "Road tax · 1.3 turbo", "RM70"),
                                                               (35.62, "Insurans · NCD 55%", "RM2,700")]),
    ]),
    dict(win=(40.60, 44.90), items=[
        dict(kind="label", text="Jumlah", y=880),
        dict(kind="counter", at=42.08, to=188570, frm=0, dur=1.2, lab="On the road", sub="183,000 + 70 + 2,700 + 2,800", accent=True, y=1180),
    ]),
    dict(win=(44.96, 51.58), items=[
        dict(kind="card", title="Kira loan", y=1000, rows=[(46.12, "Tempoh loan", "9 tahun"),
                                                         (47.40, "Down payment", "Tiada (full loan)"),
                                                         (49.90, "Bulanan (anggaran)", "± RM2,100+")]),
    ]),
    dict(win=(51.66, 58.60), items=[
        dict(kind="label", text="Rule 1/3 gaji", y=880),
        dict(kind="cards", y=960, items=[(52.60, "01 · Rule", "Ansuran = 1/3 gaji"),
                                         (54.50, "02 · Kira", "RM2,100 × 3"),
                                         (57.10, "03 · Hasil", "RM6,300 sebulan")]),
    ]),
    dict(win=(58.64, 999), items=[
        dict(kind="label", text="Jawapan", y=880),
        dict(kind="counter", at=59.80, to=6300, frm=0, dur=1.3, lab="Gaji layak", sub="RM2,100 × 3 = RM6,300 sebulan", accent=True, y=1180),
    ]),
]

OVERLAYS = [
    dict(kind="counter_pill", at=16.72, dur=4.6, to=188570, frm=0, dur_roll=1.4, lab="CLA180 SE · on the road", sub="Gaji berapa layak?"),
    dict(kind="pill", at=6.22, dur=1.6, text="Grade *5A*"),
    dict(kind="pill", at=8.48, dur=1.8, text="Mileage *6,000 km*"),
    dict(kind="pill", at=12.12, dur=2.4, text="Harga body *RM183,000*"),
    dict(kind="pill", at=14.76, dur=1.4, text="*Belum* on the road"),
    dict(kind="pill", at=67.34, dur=2.4, text="*Lower spec* kelas CLA"),
    dict(kind="pill", at=72.18, dur=1.8, text="*Semi leather* seat"),
    dict(kind="pill", at=74.16, dur=1.4, text="Lain dari design *AMG*"),
    dict(kind="pill", at=77.32, dur=1.2, text="*SE* spec"),
    dict(kind="pill", at=81.22, dur=1.4, text="Meter *7,000 km*"),
    dict(kind="pill", at=82.62, dur=1.6, text="*+1,000 km* dari auction"),
    dict(kind="pill", at=86.52, dur=1.8, text="*Executive* looks"),
    dict(kind="pill", at=88.30, dur=1.8, text="*Electronic* & memory seat"),
    dict(kind="pill", at=92.40, dur=1.2, text="*Frameless* design"),
    dict(kind="pill", at=94.00, dur=1.6, text="Sebab *coupe*"),
    dict(kind="title", at=21.62, dur=1.0, chip="JOM KIRA", accent="Gaji layak?"),
    dict(kind="pill", at=39.14, dur=1.6, text="Processing fee *RM2,800*"),
    dict(kind="pill", at=97.82, dur=1.0, text="Berminat? Tekan *link*"),
]

MUSIC = dict(file="/home/user/drive_dl/Music/music1.mp4", start=1.6, lufs=-28, duck_db=8, fade_out=1.8)
