"""Mercedes-Benz C200 AMG Avantgarde 2022 (white, grade 4A, 43,674 km) — POJI PADU (showroom theme) + studio voice.
Audio = separate VOICEOVER (Drive "Voiceover/C200 amg.m4a", 91.1 s) -> DeepFilterNet3 (vo_df.wav) -> VOICE="studio".
Video (Drive "Raw Video", 4K HLG): 1888 front 3/4 (static), 1889 front 3/4, 1890 front wheel, 1891 headlight/grille,
1892 rear 3/4 (lights on), 1893 rear, 1894 POV rear 3/4 (10 s), 1895 cabin + ambient light, 1896 meter (43,674 km),
1897 rear seats + ambient light, 1898 POV front 3/4 walk-up (29 s); photo IMG_1887.JPG (front seats) for the feature card.
Exact totals (user rule): OTR 190,000 + 2,900 + 90 + 2,800 = RM195,790 (VO "195,000 lebih");
full loan 9 yrs, no DP, VO "2,100 lebih" (no rate given) -> card "± RM2,100" (anggaran); x3 = RM6,300 (VO: "inilah gaji",
no figure) labelled anggaran. Mileage: VO "43,000 lebih", meter shows 43,674 -> odometer 43,674.
Dropped: "Guys, hari ni kita ada sebuah unit" (hook starts on the car).
Whisper fixes: "Avangard" = Avantgarde, "Rocktax" = road tax, "bermesor" = Burmester, "seleksi" = seksi.
Order (poji padu): hook -> unit -> question -> maths -> answer -> interior/features -> CTA.
"""
R = "/home/user/drive_dl/c200/Raw Video/"
W = "/home/user/work_c200/"
SOURCES = {f"b{n % 100:02d}": R + f"IMG_{n}.MOV" for n in [1888, 1889, 1890, 1891, 1892, 1893, 1895, 1896, 1897]}
SOURCES.update({"p94": R + "IMG_1894.MOV", "p98": R + "IMG_1898.MOV"})
THEME = "showroom"
ACCENT = "E6C07B"
AUDIO = W + "vo_df.wav"
VOICE = "studio"
VAD_DB = -45
GRAPHICS, KEYPOINTS = [], []
CC = (0.5, 0.5)


def K(v, s=1.06, c=CC, s2=None, d=4.0):
    return [(v, s, *c)] + ([(v + d, s2, *c)] if s2 else [])


def seg(id, a0, a1, src, v, keys, why, **kw):
    return dict(id=id, a=(a0, a1), vsrc=src, v=v, keys=keys, why=why, **kw)


CARD = "p98"     # footage under full-screen cards is never seen
SEGMENTS = [
    # hook
    seg("hookA", 1.76, 3.90, "b88", 0.0, K(0.0, 1.08, CC, 1.15, 2.2), "'Mercedes-Benz C200 AMG' — front 3/4, C200 title behind the car."),
    seg("hookB", 3.90, 6.12, "p98", 0.5, K(0.5, 1.08, (0.5, 0.48), 1.15, 2.2), "'Avantgarde tahun 2022' — POV walk-up, title settles and exits."),
    # unit
    seg("unit", 6.12, 7.46, "b91", 0.0, K(0.0, 1.05, CC, 1.12, 1.4), "'Unit ni datang dengan' (headlight + grille)."),
    seg("grade", 7.46, 8.98, "b90", 0.0, K(0.0, 1.04, CC, 1.10, 1.6), "'grade 4A dan' (front wheel)."),
    seg("mile1", 8.98, 10.72, "b89", 0.2, K(0.2, 1.04, CC, 1.10, 1.8), "'mileage original hanya' (front 3/4)."),
    seg("mile2", 10.72, 12.30, "b96", 0.0, K(0.0, 1.06, CC, 1.12, 1.6), "'43,000 lebih' over the meter (43,674 km)."),
    seg("mile3", 12.30, 13.68, "b95", 0.0, K(0.0, 1.04, CC, 1.08, 1.4), "'km sahaja' (cabin)."),
    seg("soalan", 14.26, 18.22, "p94", 0.0, K(0.0, 1.05, CC, 1.12, 4.0), "Question: gaji berapa layak? (POV rear 3/4)."),
    # maths
    seg("jom", 18.70, 20.62, "p94", 4.2, K(4.2, 1.08), "Jom kira."),
    seg("harga", 20.78, 25.80, CARD, 0.0, K(0.0), "Card: body price RM190,000."),
    seg("kos", 25.80, 39.20, "p98", 6.0, K(6.0, 1.05, CC, 1.12, 12.0), "Ledger box: insurance, road tax, fee."),
    seg("otr", 39.90, 44.70, CARD, 0.0, K(0.0), "Card: OTR RM195,790."),
    seg("loan", 45.10, 51.50, CARD, 0.0, K(0.0), "Card: full loan 9 yrs, ± RM2,100."),
    seg("rule", 51.50, 58.46, "p98", 19.2, K(19.2, 1.05, CC, 1.12, 6.5), "x3 and the 1/3 rule."),
    seg("gaji", 58.62, 62.52, CARD, 0.0, K(0.0), "Card: salary RM6,300 (anggaran)."),
    # interior / features
    seg("interior", 63.94, 66.52, "b95", 0.0, K(0.0, 1.04, CC, 1.10, 2.5), "C200 AMG Avantgarde: black interior (cabin)."),
    seg("interior2", 66.54, 69.12, "b97", 0.0, K(0.0, 1.04, CC, 1.10, 2.4), "'interior berwarna hitam' (rear seats, ambient light)."),
    seg("features", 69.28, 80.14, CARD, 0.0, K(0.0), "Card: feature checklist (photo IMG_1887)."),
    seg("sunroof", 80.14, 81.78, "b89", 0.2, K(0.2, 1.04, CC, 1.10, 1.6), "'Cuma kurang sahaja' (front 3/4, roof)."),
    seg("sunroof2", 81.78, 83.80, "p98", 26.9, K(26.9, 1.04, CC, 1.10, 2.0), "No panoramic sunroof (close to the roof/window)."),
    seg("belakang", 83.90, 85.18, "b92", 0.0, K(0.0, 1.04, CC, 1.10, 1.3), "'sangat seksi' (rear 3/4, lights on)."),
    seg("belakang2", 85.18, 86.78, "b93", 0.0, K(0.0, 1.04, CC, 1.10, 1.6), "'lagi-lagi dekat bahagian belakang' (rear)."),
    # CTA
    seg("cta", 86.94, 90.00, "p94", 6.5, K(6.5, 1.04, CC, 1.12, 3.0), "CTA over the POV pointing at the rear 3/4."),
]

FRONT, SEATS = W + "still_front.png", W + "photo_seats.png"
F1 = "/home/user/fonts_dl/f1/Formula1-Bold.ttf"
MASK_MODEL = "birefnet-general-lite"
BEHIND = [
    dict(win=(1.76, 3.90), font=F1, top="MERCEDES-BENZ", main="C*200*", bottom=690, width=900, top_scale=0.22, dim=0.42, enter="slam", exit=False),
    dict(win=(3.90, 6.12), font=F1, top="MERCEDES-BENZ", main="C*200*", bottom=915, width=900, top_scale=0.22, dim=0.42, enter="settle", exit=True),
]

SHOWROOM = dict(
    cards=[
        dict(win=(20.78, 25.80), kicker="Mercedes-Benz C200 AMG", heading="HARGA BODY", head_fs=120, ghost="HARGA",
             photo=FRONT, box=(90, 470, 900, 620),
             items=[dict(kind="counter", at=23.20, to=190000, y=1330, fs=170, lab="Harga jual")],
             footer="Mercedes-Benz C200 AMG Avantgarde · 2022 · grade 4A · 43,674 km"),
        dict(win=(39.90, 44.70), kicker="Kos on the road", heading="JUMLAH", head_fs=130, ghost="TOTAL",
             items=[dict(kind="tiles", y=520, tiles=[(39.96, "Harga body", "190,000"), (40.16, "Insurans", "2,900"),
                                                     (40.36, "Road tax", "90"), (40.56, "Processing", "2,800")]),
                    dict(kind="counter", at=41.64, to=195790, y=1200, fs=180, lab="On the road",
                         sub="190,000 + 2,900 + 90 + 2,800")]),
        dict(win=(45.10, 51.50), kicker="Full loan · tanpa DP", heading="KIRA LOAN", head_fs=120, ghost="LOAN",
             items=[dict(kind="ring", at=46.02, n=9, y=760, unit="TAHUN"),
                    dict(kind="chip", at=46.62, text="TANPA DOWN PAYMENT", y=1055),
                    dict(kind="counter", at=49.36, to=2100, y=1330, fs=160, pre="± ", lab="Bulanan (anggaran)")]),
        dict(win=(58.62, 62.52), kicker="Jawapan", heading="GAJI LAYAK", head_fs=120, ghost="GAJI",
             items=[dict(kind="fraction", at=58.64, frac=1 / 3, text="1/3", unit="ANSURAN", y=720),
                    dict(kind="counter", at=59.30, to=6300, y=1170, fs=190, lab="Gaji sebulan",
                         sub="RM2,100 × 3 = RM6,300 (anggaran)"),
                    dict(kind="chip", at=60.82, text="KORANG LAYAK? KOMEN ↓", y=1440, solid=True)]),
        dict(win=(69.28, 80.14), kicker="C200 AMG Avantgarde", heading="SIAP *DENGAN*", head_fs=120, ghost="LENGKAP",
             photo=SEATS, box=(90, 440, 900, 520),
             items=[dict(kind="checklist", y=1020, x=150,
                         items=[(69.76, "Seat semi-leather"), (71.60, "Head-up display"), (72.96, "Ambient lighting"),
                                (75.36, "Konsol carbon fibre"), (77.00, "Burmester sound"), (79.04, "Seat elektrik")])]),
    ],
    lowers=[
        # hook
        dict(at=1.82, until=6.10, kicker="Harga on the road", counter=dict(to=195790, dur=1.2), fs=150, y=1480),
        # unit
        dict(at=7.46, until=8.96, kicker="Grade", big="*4A*", fs=150),
        dict(at=9.40, until=13.66, kicker="Mileage original", odometer=43674, suffix="KM", keep=True),
        dict(at=14.48, until=18.20, kicker="Soalan hari ni", big="GAJI BERAPA *LAYAK?*", fs=120, thump=True),
        # maths
        dict(at=18.70, until=20.60, kicker="Bab 01", big="JOM *KIRA*", thump=True),
        dict(at=25.80, until=39.18, box="Kos on the road", box_h=460, y=1300,
             rows=[(27.64, "Insurans · NCD 55%", "RM2,900"), (32.30, "Road tax · 1.5 turbo", "RM90"),
                   (36.08, "Processing fee", "RM2,800")]),
        dict(at=51.50, until=53.68, kicker="Ansuran × 3", big="RM2,100 *× 3*", fs=140),
        dict(at=53.70, until=58.44, kicker="Rule paling simpel", big="MAKS *1/3 GAJI*", fs=130),
        # interior / features
        dict(at=64.58, until=67.42, kicker="Mercedes-Benz", big="C200 *AVANTGARDE*", fs=120, chips=["2022"]),
        dict(at=67.44, until=69.10, kicker="Dalaman", big="INTERIOR *HITAM*"),
        dict(at=80.14, until=83.78, kicker="Cuma kurang", big="TIADA *SUNROOF*", chips=[(82.46, "PANORAMIC SUNROOF", False)]),
        dict(at=84.32, until=86.76, kicker="Sangat seksi", big="BAHAGIAN *BELAKANG*", fs=120, thump=True),
        # CTA
        dict(at=86.94, until=89.98, kicker="Mercedes-Benz C200 AMG", big="BERMINAT?",
             chips=[(88.80, "TEKAN LINK", True)], thump=True),
    ],
)

MUSIC = dict(file="/home/user/drive_dl/porsche/Music/music.mp4", start=1.0, lufs=-29, duck_db=8, fade_out=1.8)
