"""Mercedes-AMG CLE 53 4MATIC+ Coupe 2024 (white, recond Japan, unregistered, grade 5A, 5,582 km) — POJI PADU
(showroom theme) + studio voice. VOICEOVER (Drive "Voiceover/Cle53.m4a", 156.4 s) -> DeepFilterNet3 (vo_df.wav).
Video (Drive "Raw Video", 4K HLG): 1997 rear static (start-up), 1998 rear -> drives away, 1999 side, 2001 front 3/4,
2002 front wheel (red caliper), 2003 rear 3/4 (quad exhaust), 2004 rear 3/4 wide, 2005 rear (CLE 53), 2007 rear corner
badge + exhaust, 2008 POV rear 3/4 (19 s), 2009 rear wheel, 2010 door (Burmester, seat controls), 2012 cabin,
2013 seat + panoramic roof, 2014 meter (5,582 km), 2016 screen + carbon, 2018 AMG drive-mode dial, 2019 engine bay,
2020 POV front 3/4 (21 s).
User's quotation (verified): OTR 598,000 + 7,800 + 2,130 + 2,800 = RM610,730; DP 20% of 598,000 = RM119,600;
loan = 610,730 - 119,600 = RM491,130 (charges inside the loan) @ 2.3%: 9 yrs RM5,488.83, 7 yrs RM6,788.12,
5 yrs RM9,126.83; salary (9 yrs) 5,488.83 x 3 = RM16,466 (VO "16,000 lebih").
Official price RM722,888 (OTR without insurance, Sept 2025) vs this unit without insurance 598,000 + 2,130 + 2,800 =
RM602,930 -> RM119,958 cheaper (VO "hampir RM120,000").
Retakes: "Kereta performa ... full loan" (55.42) -> second take 59.06; "Dah siap package ..." (119.24 and 124.80,
broken) -> full take 130.90. Dropped: "Guys, hari ni kita ada sebuah unit" (hook starts on the car).
Whisper fixes: "kaji" = gaji, "full on" = full loan, "Kau orang" = korang, "Formatik" = 4MATIC, "Bermasas" =
Burmester, "kategoran" = kata korang.
Order (poji padu): hook -> unit -> question -> maths -> answer -> engine/performance -> features -> CTA.
"""
R = "/home/user/drive_dl/cle53/Raw Video/"
W = "/home/user/work_cle53/"
SOURCES = {f"b{n % 100:02d}": R + f"IMG_{n}.MOV" for n in
           [1997, 1998, 1999, 2001, 2002, 2003, 2004, 2005, 2007, 2009, 2010, 2012, 2013, 2014, 2016, 2018, 2019]}
SOURCES.update({"p08": R + "IMG_2008.MOV", "p20": R + "IMG_2020.MOV"})
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


CARD = "p20"     # footage under full-screen cards is never seen
SEGMENTS = [
    # hook
    seg("hookA", 1.68, 4.28, "b01", 0.0, K(0.0, 1.08, CC, 1.15, 2.6), "'Mercedes-AMG CLE 53' — front 3/4, CLE 53 title behind the car."),
    seg("hookB", 4.28, 7.20, "p20", 0.5, K(0.5, 1.08, (0.5, 0.48), 1.15, 2.9), "'4MATIC+ tahun 2024' — POV, title settles and exits."),
    seg("murah", 7.90, 10.34, "b99", 0.0, K(0.0, 1.04, CC, 1.12, 2.4), "'Harga dia hampir RM120,000 lebih murah' (side)."),
    seg("murah2", 10.34, 12.94, "b04", 0.0, K(0.0, 1.04, CC, 1.12, 2.6), "'berbanding harga rasmi Mercedes Malaysia' (rear 3/4)."),
    # unit
    seg("unit", 13.84, 18.94, "p08", 0.0, K(0.0, 1.05, CC, 1.12, 5.0), "Recond from Japan, unregistered (POV rear 3/4)."),
    seg("grade", 19.18, 21.10, "b07", 0.0, K(0.0, 1.04, CC, 1.10, 1.9), "'Datang dengan grade 5A' (CLE 53 badge + exhaust)."),
    seg("mile1", 21.10, 22.42, "b09", 0.0, K(0.0, 1.04, CC, 1.10, 1.3), "'dan mileage original hanya' (rear wheel)."),
    seg("mile2", 22.42, 24.54, "b14", 0.2, K(0.2, 1.06, CC, 1.12, 2.1), "5,582 over the meter."),
    seg("mile3", 24.54, 25.60, "b12", 0.0, K(0.0, 1.04, CC, 1.08, 1.1), "'kilometer sahaja' (cabin)."),
    seg("soalan", 26.44, 29.54, "p08", 5.5, K(5.5, 1.05, CC, 1.12, 3.1), "Question: gaji berapa layak?"),
    # maths
    seg("harga", 30.40, 35.78, CARD, 0.0, K(0.0), "Card: body price RM598,000."),
    seg("kos", 36.80, 50.22, "p20", 4.0, K(4.0, 1.05, CC, 1.12, 12.0), "Ledger box: insurance, road tax, fee."),
    seg("otr", 50.68, 55.14, CARD, 0.0, K(0.0), "Card: OTR RM610,730."),
    seg("fullloan", 59.06, 61.16, "p08", 9.2, K(9.2, 1.05, CC, 1.12, 2.1), "Second take: no full loan."),
    seg("loan", 61.34, 74.94, CARD, 0.0, K(0.0), "Card: DP 20% RM119,600, loan RM491,130 @ 2.3%."),
    seg("tempoh", 74.94, 88.96, CARD, 0.0, K(0.0), "Card: 9 / 7 / 5 years + which one? (comment)."),
    seg("rule", 89.78, 93.66, "b97", 6.0, K(6.0, 1.04, CC, 1.12, 3.9), "1/3 rule (rear, lights on)."),
    seg("kali", 93.96, 95.64, "b05", 0.5, K(0.5, 1.04, CC, 1.10, 1.7), "'kalikan sahaja dengan 3' (rear, CLE 53)."),
    seg("gaji", 95.78, 101.12, CARD, 0.0, K(0.0), "Card: salary RM16,466 (9 years)."),
    # engine / performance
    seg("enjin", 102.38, 105.52, "b19", 0.0, K(0.0, 1.04, CC, 1.12, 3.2), "3.0 inline-6 turbo (engine bay)."),
    seg("hybrid", 105.52, 106.96, "b03", 0.0, K(0.0, 1.04, CC, 1.10, 1.5), "'dengan mild hybrid' (rear 3/4, quad exhaust)."),
    seg("kuasa", 107.86, 111.42, "b98", 0.0, K(0.0, 1.04, CC, 1.10, 3.6), "449 PS, 560 Nm (car drives away)."),
    seg("awd", 111.42, 118.38, "b18", 0.0, K(0.0, 1.06, CC, 1.14, 6.6), "AWD 4MATIC+, 0-100 4.2 s (AMG drive-mode dial)."),
    # features (full retake)
    seg("dynamic", 130.90, 133.70, "b03", 0.3, K(0.3, 1.06, CC, 1.12, 2.5), "AMG Dynamic Plus (rear 3/4)."),
    seg("axle", 133.70, 135.12, "b99", 2.5, K(2.5, 1.04, CC, 1.10, 1.5), "Rear-axle steering (side)."),
    seg("rim", 135.12, 137.40, "b02", 0.0, K(0.0, 1.04, CC, 1.10, 2.3), "AMG 20-inch rim."),
    seg("caliper", 137.40, 138.66, "b09", 0.3, K(0.3, 1.10, CC, 1.16, 1.3), "Red calipers."),
    seg("sunroof", 138.88, 142.28, "b13", 0.0, K(0.0, 1.04, CC, 1.10, 3.3), "Panoramic sunroof."),
    seg("burmester", 142.28, 143.52, "b10", 0.0, K(0.0, 1.06, (0.6, 0.4), 1.14, 1.3), "Burmester speaker (door)."),
    seg("hud", 143.62, 144.40, "b12", 0.0, K(0.0, 1.06, (0.65, 0.4), 1.12, 0.8), "Head-up display (cabin)."),
    seg("carbon", 144.52, 145.90, "b16", 0.0, K(0.0, 1.04, CC, 1.12, 1.4), "Carbon fibre trim."),
    seg("ambient", 146.00, 146.88, "b12", 1.0, K(1.0, 1.04, CC, 1.10, 0.9), "Ambient lighting."),
    seg("seatel", 146.88, 148.38, "b10", 1.3, K(1.3, 1.08, (0.4, 0.45), 1.14, 1.5), "Electric seat controls (door)."),
    seg("massage", 148.48, 150.68, CARD, 0.0, K(0.0), "Card: interior checklist, massage seat last."),
    # CTA
    seg("cta", 151.02, 154.88, "p20", 16.5, K(16.5, 1.04, CC, 1.12, 3.9), "CTA, ends on the front 3/4 (loops to the hook)."),
]

FRONT, CABIN = W + "still_front.png", W + "still_cabin.png"
F1 = "/home/user/fonts_dl/f1/Formula1-Bold.ttf"
MASK_MODEL = "birefnet-general-lite"
BEHIND = [
    dict(win=(1.68, 4.28), font=F1, top="MERCEDES-AMG", main="CLE *53*", bottom=655, width=920, top_scale=0.24, dim=0.42, enter="slam", exit=False),
    dict(win=(4.28, 7.20), font=F1, top="MERCEDES-AMG", main="CLE *53*", bottom=830, width=920, top_scale=0.24, dim=0.42, enter="settle", exit=True),
]

SHOWROOM = dict(
    cards=[
        dict(win=(30.40, 35.78), kicker="Mercedes-AMG CLE 53 4MATIC+", heading="HARGA BODY", head_fs=120, ghost="HARGA",
             photo=FRONT, box=(90, 470, 900, 620),
             items=[dict(kind="counter", at=33.74, to=598000, y=1330, fs=170, lab="Harga jual")],
             footer="Mercedes-AMG CLE 53 4MATIC+ · 2024 · grade 5A · 5,582 km"),
        dict(win=(50.68, 55.14), kicker="Kos on the road", heading="JUMLAH", head_fs=130, ghost="TOTAL",
             items=[dict(kind="tiles", y=520, tiles=[(50.74, "Harga body", "598,000"), (50.94, "Insurans", "7,800"),
                                                     (51.14, "Road tax", "2,130"), (51.34, "Processing", "2,800")]),
                    dict(kind="counter", at=52.26, to=610730, y=1200, fs=180, lab="On the road",
                         sub="598,000 + 7,800 + 2,130 + 2,800")]),
        dict(win=(61.34, 74.94), kicker="Kereta performance · tiada full loan", heading="DP *20%*", head_fs=130, ghost="LOAN",
             items=[dict(kind="counter", at=62.56, to=119600, y=680, fs=150, lab="Down payment 20%", sub="598,000 × 20%"),
                    dict(kind="chip", at=66.62, text="INSURANS + ROAD TAX + FEE MASUK LOAN", y=900, fs=30),
                    dict(kind="counter", at=70.70, to=491130, y=1170, fs=170, lab="Jumlah loan", sub="610,730 − 119,600"),
                    dict(kind="chip", at=73.92, text="INTEREST 2.30%", y=1420, solid=True)]),
        dict(win=(74.94, 88.96), kicker="Loan RM491,130 · interest 2.3%", heading="ANSURAN", head_fs=130, ghost="BULAN",
             items=[dict(kind="counter", at=77.30, to=5488.83, y=650, fs=130, lab="9 tahun", sub="RM5,488.83 sebulan"),
                    dict(kind="counter", at=79.84, to=6788.12, y=980, fs=130, lab="7 tahun", sub="RM6,788.12 sebulan"),
                    dict(kind="counter", at=83.72, to=9126.83, y=1310, fs=130, lab="5 tahun", sub="RM9,126.83 sebulan"),
                    dict(kind="chip", at=87.58, text="KORANG PILIH YANG MANA? KOMEN ↓", y=1560, solid=True)]),
        dict(win=(95.78, 101.12), kicker="Jawapan · loan 9 tahun", heading="GAJI LAYAK", head_fs=120, ghost="GAJI",
             items=[dict(kind="fraction", at=95.80, frac=1 / 3, text="1/3", unit="ANSURAN", y=720),
                    dict(kind="counter", at=99.00, to=16466, y=1170, fs=190, lab="Gaji sebulan",
                         sub="RM5,488.83 × 3 = RM16,466"),
                    dict(kind="chip", at=100.10, text="KORANG LAYAK? KOMEN ↓", y=1440, solid=True)]),
        dict(win=(148.48, 150.68), kicker="Bahagian dalam", heading="SIAP *DENGAN*", head_fs=120, ghost="DALAM",
             photo=CABIN, box=(90, 440, 900, 520),
             items=[dict(kind="checklist", y=1020, x=150,
                         items=[(148.50, "Panoramic sunroof"), (148.56, "Burmester sound"), (148.62, "Head-up display"),
                                (148.68, "Carbon fibre"), (148.74, "Ambient · seat elektrik"), (149.06, "Massage seat")])]),
    ],
    lowers=[
        # hook
        dict(at=1.74, until=7.18, kicker="Harga on the road", counter=dict(to=610730, dur=1.2), fs=150, y=1480),
        dict(at=8.50, until=12.92, kicker="Lebih murah dari harga rasmi", counter=dict(to=119958, dur=1.3), fs=150, y=1480,
             chips=[(11.20, "RASMI RM722,888", False)]),
        # unit
        dict(at=14.64, until=18.92, kicker="Status", big="RECOND *JEPUN*", chips=[(16.98, "BELUM REGISTER", True)]),
        dict(at=19.74, until=21.08, kicker="Grade", big="*5A*", fs=150),
        dict(at=21.10, until=25.58, kicker="Mileage original", odometer=5582, suffix="KM", keep=True),
        dict(at=26.44, until=29.52, kicker="Soalan hari ni", big="GAJI BERAPA *LAYAK?*", fs=120, thump=True),
        # maths
        dict(at=36.80, until=50.20, box="Kos on the road", box_h=460, y=1300,
             rows=[(37.18, "Insurans · NCD 55%", "RM7,800"), (41.64, "Road tax · 3.0L", "RM2,130"),
                   (47.66, "Processing fee", "RM2,800")]),
        dict(at=59.06, until=61.14, kicker="Kereta performance", big="TAK BOLEH *FULL LOAN*", fs=110, thump=True),
        dict(at=89.78, until=93.64, kicker="Rule paling simple", big="MAKS *1/3 GAJI*", fs=130),
        dict(at=93.96, until=95.62, kicker="Ansuran × 3", big="RM5,489 *× 3*", fs=140),
        # engine / performance
        dict(at=102.38, until=106.94, kicker="Enjin", big="3.0L *INLINE-6*", chips=["TURBO", (105.52, "MILD HYBRID", True)]),
        dict(at=107.86, until=111.40, kicker="Kuasa · tork", big="449 PS · *560 NM*", fs=120),
        dict(at=111.42, until=114.08, kicker="All-wheel drive", big="4MATIC*+*", fs=150),
        dict(at=114.10, until=118.36, kicker="0–100 km/j", big="*4.2* SAAT", fs=150),
        # features
        dict(at=132.28, until=133.68, kicker="Siap dengan · 01", big="AMG DYNAMIC *PLUS*", fs=110),
        dict(at=133.70, until=135.10, kicker="02", big="REAR-AXLE *STEERING*", fs=110),
        dict(at=135.12, until=136.90, kicker="03 · Rim AMG", big="*20* INCI", fs=150),
        dict(at=136.92, until=138.64, kicker="04 · Caliper", big="WARNA *MERAH*"),
        dict(at=140.98, until=142.26, kicker="Dalaman", big="PANORAMIC *SUNROOF*", fs=110),
        dict(at=142.28, until=143.50, kicker="Sound system", big="*BURMESTER*"),
        dict(at=143.62, until=144.38, kicker="Paparan", big="HEAD-UP *DISPLAY*", fs=120),
        dict(at=144.52, until=145.88, kicker="Trim", big="CARBON *FIBRE*"),
        dict(at=146.00, until=146.86, kicker="Lampu", big="AMBIENT *LIGHTING*", fs=120),
        dict(at=146.88, until=148.36, kicker="Seat", big="SEAT *ELEKTRIK*"),
        # CTA
        dict(at=151.02, until=154.86, kicker="Mercedes-AMG CLE 53", big="BERMINAT?",
             chips=[(153.68, "TEKAN LINK DI BIO", True)], thump=True),
    ],
)

MUSIC = dict(file="/home/user/drive_dl/porsche/Music/music.mp4", start=1.0, lufs=-29, duck_db=8, fade_out=1.8)
