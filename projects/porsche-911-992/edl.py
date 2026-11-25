"""Porsche 911 Carrera 992.2 2025 (Cartagena Yellow, Japan spec, grade 5A, 2,538 km) — POJI PADU (showroom theme)
+ studio voice. VOICEOVER v2 (Drive "Voiceover/Jalan 1-48G 53.m4a", 141.1 s) -> DeepFilterNet3 (vo2_df.wav), then the
engine start-up from IMG_1952 (10.70-14.30 s, its own audio) is spliced in at 81.70 s, right after
"...bunyi exhaust dia." (vo2_final.wav). A(t) maps a voiceover time to the spliced track.
Video (Drive "Raw Video", 4K HLG): 1952 rear low close (engine start + taillights at 11 s), 1954 meter boot (2,538 km),
1955 rear, 1958 front 3/4, 1960 rear 3/4 pan, 1961 side, 1962 seat, 1963 cabin/steering, 1964 Sport Chrono clock,
1966 console (PDK, body-colour trim), 1967 yellow belt, 1968 headrest crest, 1971 rear 3/4 + wing, 1973 POV rear 3/4,
1975 front close, 1976 POV front 3/4, 1979 front wheel, 1980 rear wheel + wing, 1981 wing close.
Exact totals (user rule): OTR 888,000 + 11,000 + 2,130 + 2,800 = RM903,930 (VO "903,000 lebih");
loan 80% = 710,400, DP 20% = 177,600; 2.3% x 9 yrs = 147,052.80; (710,400 + 147,052.80) / 108 = RM7,939.38/month
(VO "7,900 lebih"); x3 = RM23,818 (VO: "inilah gaji", no figure).
Retakes: "tak boleh full loan / Hanya 80%..." (39.02-42.64, cut off) -> second take 46.28; "bahagian dalam ... sport
chrono" (116.04-118.92) -> second take 120.70; "dan seat belt berwarna kuring" (128.66-130.80) -> second take 131.74.
Dropped: "Guys, hari ni kita ada sebuah unit" (hook starts on the car), "Assalamualaikum".
Whisper fixes: "Japan Spike" = Japan spec, "RM2538" = 2,538 km, "rotex" = road tax, "akantara" = Alcantara.
Order (VO v2): hook -> unit -> question -> maths -> answer -> engine sound -> model/colour -> spec -> features -> CTA.
"""
R = "/home/user/drive_dl/porsche/Raw Video/"
W = "/home/user/work_porsche/"
SOURCES = {f"b{n % 100:02d}": R + f"IMG_{n}.MOV" for n in
           [1952, 1954, 1955, 1958, 1960, 1961, 1962, 1963, 1964, 1966, 1967, 1968, 1971, 1975, 1979, 1980, 1981]}
SOURCES.update({"p73": R + "IMG_1973.MOV", "p76": R + "IMG_1976.MOV"})
THEME = "showroom"
ACCENT = "E6C07B"
AUDIO = W + "vo2_final.wav"
VOICE = "studio"
VAD_DB = -45
GRAPHICS, KEYPOINTS = [], []
CC = (0.5, 0.5)

INS, ENG = 81.70, 3.60          # engine start-up spliced into the voiceover here (seconds of the VO / its length)


def A(t):
    """Voiceover time -> time in the spliced track (vo2_final.wav)."""
    return t + (ENG if t >= INS else 0.0)


def K(v, s=1.06, c=CC, s2=None, d=4.0):
    return [(v, s, *c)] + ([(v + d, s2, *c)] if s2 else [])


def seg(id, a0, a1, src, v, keys, why, **kw):
    return dict(id=id, a=(A(a0), A(a1)), vsrc=src, v=v, keys=keys, why=why, **kw)


CARD = "p76"     # footage under full-screen cards is never seen
SEGMENTS = [
    # hook
    seg("hookA", 1.50, 3.14, "b58", 0.0, K(0.0, 1.08, CC, 1.16, 1.6), "'Porsche 911 facelift baru' — front 3/4, 911 title behind the car."),
    seg("hookB", 3.14, 4.80, "p76", 0.3, K(0.3, 1.08, (0.5, 0.48), 1.15, 1.7), "'tahun 2025' — POV at the car, title settles and exits."),
    # unit
    seg("spec", 4.88, 7.12, "b61", 0.0, K(0.0, 1.04, CC, 1.10, 2.3), "'Unit ni adalah Japan spec datang dengan' (side)."),
    seg("grade", 7.12, 9.32, "b75", 0.0, K(0.0, 1.04, CC, 1.10, 2.2), "'grade 5A, mileage original hanya' (front close)."),
    seg("mileage", 9.32, 12.54, "b54", 4.3, K(4.3, 1.06, (0.5, 0.55), 1.14, 3.2), "2,538 km over the meter."),
    seg("soalan", 13.20, 17.04, "p73", 0.0, K(0.0, 1.05, CC, 1.12, 3.9), "Question: gaji berapa layak?"),
    # maths
    seg("jom", 17.36, 18.24, "p73", 4.0, K(4.0, 1.08), "Jom kira."),
    seg("harga", 18.54, 22.64, CARD, 0.0, K(0.0), "Card: body price RM888,000."),
    seg("kos", 23.26, 33.60, "p76", 8.4, K(8.4, 1.05, CC, 1.12, 10.0), "Ledger box: insurance, road tax, fee."),
    seg("otr", 34.56, 38.70, CARD, 0.0, K(0.0), "Card: OTR RM903,930."),
    seg("fullloan", 46.28, 48.82, "p73", 8.0, K(8.0, 1.05, CC, 1.12, 2.6), "Second take: no full loan."),
    seg("loan", 49.00, 59.78, CARD, 0.0, K(0.0), "Card: loan 80% / DP 20%."),
    seg("bulanan", 60.40, 66.88, CARD, 12.0, K(12.0), "Card: 9 years @ 2.3% -> RM7,939."),
    seg("rule", 67.34, 73.74, "b52", 0.5, K(0.5, 1.04, CC, 1.12, 6.4), "Rule 1/3 and x3 (rear close, lights off)."),
    seg("gaji", 74.02, 78.12, CARD, 0.0, K(0.0), "Card: salary RM23,818."),
    # engine sound (spliced block [INS, INS + ENG) of the spliced track, same clip/time as its video)
    seg("dengar", 78.56, INS - 1e-9, "b52", 7.56, K(7.56, 1.04, CC, 1.10, 3.2), "'jom kita dengarkan bunyi exhaust dia'."),
    dict(id="engine", a=(INS, INS + ENG), vsrc="b52", v=10.70, keys=K(10.70, 1.10, CC, 1.18, 3.6), cut_pauses=False,
         why="Engine start-up: taillights light up with the sound (no voice)."),
    # model + colour
    seg("model", 82.32, 84.58, "b52", 14.30, K(14.30, 1.12, CC, 1.06, 2.3), "'Ini adalah Porsche 911 Carrera' (idle, lights on)."),
    seg("model2", 84.62, 87.86, "b71", 0.0, K(0.0, 1.04, CC, 1.10, 3.2), "'Model 992.2, facelift paling latest' (rear 3/4 + wing)."),
    seg("colour", 88.02, 90.48, "b55", 0.0, K(0.0, 1.04, CC, 1.10, 2.5), "Cartagena Yellow (rear, lights on)."),
    # spec
    seg("enjin", 90.88, 94.20, "b60", 0.0, K(0.0, 1.04, CC, 1.12, 3.3), "3.0L flat-six twin turbo (rear 3/4 pan)."),
    seg("kuasa", 94.28, 98.20, "b52", 16.60, K(16.60, 1.10, CC, 1.04, 3.9), "394 PS, 450 Nm (idle, lights on)."),
    seg("pdk", 98.52, 99.20, "b66", 0.0, K(0.0, 1.04, (0.62, 0.45), 1.12, 2.4), "'Gearbox' over the selector."),
    seg("pdk2", 100.70, 102.42, "b66", 0.62, K(0.0, 1.04, (0.62, 0.45), 1.12, 2.4), "'dia pula adalah PDK 8 speed' (long pause cut)."),
    seg("sprint", 102.70, 106.34, "p76", 19.0, K(19.0, 1.10, CC, 1.02, 3.6), "0-100 in 3.9 s."),
    # features
    seg("aero", 106.54, 109.46, "b58", 0.2, K(0.2, 1.04, CC, 1.12, 2.6), "Package: aero kit."),
    seg("spoiler", 109.46, 110.70, "b81", 0.6, K(0.6, 1.04, CC, 1.10, 1.2), "Spoiler / fixed wing close-up."),
    seg("exhaust", 110.80, 111.88, "b52", 22.80, K(22.80, 1.20, (0.45, 0.75), 1.26, 1.1), "Sports exhaust, black tips."),
    seg("rim20", 112.10, 113.80, "b79", 0.3, K(0.3, 1.04, CC, 1.10, 1.7), "Front rim 20 inch."),
    seg("rim21", 113.92, 115.82, "b80", 0.5, K(0.5, 1.04, CC, 1.10, 1.9), "Rear rim 21 inch."),
    seg("dalam", 120.70, 122.20, "b63", 0.0, K(0.0, 1.04), "Second take: 'Untuk bagian dalam pula'."),
    seg("chrono", 122.32, 124.26, "b64", 0.3, K(0.3, 1.10, (0.5, 0.52), 1.22, 2.0), "Sport Chrono clock, yellow."),
    seg("stereng", 124.58, 126.32, "b63", 1.0, K(1.0, 1.08, (0.45, 0.45), 1.16, 1.8), "GT Sport steering (Alcantara)."),
    seg("seat", 126.66, 127.58, "b62", 0.0, K(0.0, 1.04, CC, 1.10, 1.0), "'Logo Porsche' (seat)."),
    seg("headrest", 127.58, 128.66, "b68", 0.0, K(0.0, 1.06, CC, 1.14, 1.2), "'yang timbul dekat headrest'."),
    seg("belt", 131.74, 134.02, "b67", 0.0, K(0.0, 1.04, CC, 1.14, 2.3), "Second take: yellow seat belts."),
    seg("trim", 134.16, 137.14, CARD, 0.0, K(0.0), "Card: interior checklist + trim in body colour."),
    # CTA
    seg("cta", 137.42, 140.44, "p76", 27.2, K(27.2, 1.04, CC, 1.12, 3.1), "CTA, ends on the front 3/4 (loops to the hook)."),
]

FRONT, REAR, CONSOLE = W + "still_front.png", W + "still_rear.png", W + "still_console.png"
F1 = "/home/user/fonts_dl/f1/Formula1-Bold.ttf"
MASK_MODEL = "birefnet-general-lite"
BEHIND = [
    dict(win=(A(1.50), A(3.14)), font=F1, top="PORSCHE", main="*911*", bottom=770, width=820, top_scale=0.26, dim=0.42, enter="slam", exit=False),
    dict(win=(A(3.14), A(4.80)), font=F1, top="PORSCHE", main="*911*", bottom=935, width=820, top_scale=0.26, dim=0.42, enter="settle", exit=True),
]

SHOWROOM = dict(
    cards=[
        dict(win=(A(18.54), A(22.64)), kicker="Porsche 911 Carrera 992.2", heading="HARGA BODY", head_fs=120, ghost="HARGA",
             photo=FRONT, box=(90, 470, 900, 620),
             items=[dict(kind="counter", at=A(21.04), to=888000, y=1330, fs=170, lab="Harga jual")],
             footer="Porsche 911 Carrera 992.2 · 2025 · 2,538 km"),
        dict(win=(A(34.56), A(38.70)), kicker="Kos on the road", heading="JUMLAH", head_fs=130, ghost="TOTAL",
             items=[dict(kind="tiles", y=520, tiles=[(A(34.60), "Harga body", "888,000"), (A(34.80), "Insurans", "11,000"),
                                                     (A(35.00), "Road tax", "2,130"), (A(35.20), "Processing", "2,800")]),
                    dict(kind="counter", at=A(36.08), to=903930, y=1200, fs=180, lab="On the road",
                         sub="888,000 + 11,000 + 2,130 + 2,800")]),
        dict(win=(A(49.00), A(59.78)), kicker="Kereta performa · tiada full loan", heading="LOAN *80%*", head_fs=130, ghost="LOAN",
             items=[dict(kind="chip", at=A(49.42), text="LOAN 80%", y=540, solid=True),
                    dict(kind="chip", at=A(51.16), text="DOWN PAYMENT 20%", y=640),
                    dict(kind="counter", at=A(54.46), to=177600, y=870, fs=150, lab="Down payment 20%", sub="888,000 × 20%"),
                    dict(kind="counter", at=A(58.36), to=710400, y=1280, fs=170, lab="Jumlah loan 80%", sub="888,000 × 80%")]),
        dict(win=(A(60.40), A(66.88)), kicker="9 tahun · interest 2.3%", heading="ANSURAN", head_fs=130, ghost="BULAN",
             items=[dict(kind="ring", at=A(60.94), n=9, y=760, unit="TAHUN"),
                    dict(kind="chip", at=A(62.12), text="INTEREST 2.30%", y=1055),
                    dict(kind="counter", at=A(64.78), to=7939, y=1330, fs=170, lab="Bulanan",
                         sub="(710,400 + 147,052.80) ÷ 108 bulan")]),
        dict(win=(A(74.02), A(78.12)), kicker="Jawapan", heading="GAJI LAYAK", head_fs=120, ghost="GAJI",
             items=[dict(kind="fraction", at=A(74.04), frac=1 / 3, text="1/3", unit="ANSURAN", y=720),
                    dict(kind="counter", at=A(74.88), to=23818, y=1170, fs=190, lab="Gaji sebulan",
                         sub="RM7,939.38 × 3 = RM23,818"),
                    dict(kind="chip", at=A(76.66), text="KORANG LAYAK? KOMEN ↓", y=1440, solid=True)]),
        dict(win=(A(134.16), A(137.14)), kicker="Bahagian dalam", heading="SIAP *DENGAN*", head_fs=120, ghost="DALAM",
             photo=CONSOLE, box=(90, 470, 900, 560),
             items=[dict(kind="checklist", y=1110, x=150,
                         items=[(A(134.20), "Sport Chrono kuning"), (A(134.40), "Stereng GT Sport"),
                                (A(134.60), "Logo timbul headrest"), (A(134.80), "Tali pinggang kuning"),
                                (A(135.68), "Trim warna badan")])]),
    ],
    lowers=[
        # hook
        dict(at=A(1.56), until=A(4.78), kicker="Harga on the road", counter=dict(to=903930, dur=1.2), fs=150, y=1480),
        # unit
        dict(at=A(5.64), until=A(7.10), kicker="Spesifikasi", big="JAPAN *SPEC*"),
        dict(at=A(7.12), until=A(7.92), kicker="Grade", big="*5A*", fs=150),
        dict(at=A(7.94), until=A(12.52), kicker="Mileage original", odometer=2538, suffix="KM", keep=True),
        dict(at=A(13.48), until=A(17.02), kicker="Soalan hari ni", big="GAJI BERAPA *LAYAK?*", fs=120, thump=True),
        # maths
        dict(at=A(17.36), until=A(18.22), kicker="Bab 01", big="JOM *KIRA*", thump=True),
        dict(at=A(23.26), until=A(33.58), box="Kos on the road", box_h=460, y=1300,
             rows=[(A(24.14), "Insurans · NCD 55%", "RM11,000"), (A(27.84), "Road tax · 3.0L", "RM2,130"),
                   (A(31.10), "Processing fee", "RM2,800")]),
        dict(at=A(46.28), until=A(48.80), kicker="Bab 02 · Kereta performa", big="TAK BOLEH *FULL LOAN*", fs=110, thump=True),
        dict(at=A(67.34), until=A(71.80), kicker="Rule paling simpel", big="MAKS *1/3 GAJI*", fs=130),
        dict(at=A(71.96), until=A(73.72), kicker="Ansuran × 3", big="RM7,939 *× 3*", fs=140),
        # engine sound
        dict(at=A(78.56), until=INS + ENG - 0.02, kicker="Kuatkan volume", big="BUNYI *EXHAUST*", fs=130,
             chips=[(INS, "VOLUME ↑", True)], thump=True),
        # model + colour
        dict(at=A(83.24), until=A(87.84), kicker="Porsche 911", big="CARRERA *992.2*", chips=["2025", "FACELIFT"], fs=140, keep=True),
        dict(at=A(88.90), until=A(90.46), kicker="Warna", big="*CARTAGENA* YELLOW"),
        # spec
        dict(at=A(90.88), until=A(94.18), kicker="Enjin", big="3.0L *FLAT-SIX*", chips=["TWIN TURBO"]),
        dict(at=A(94.28), until=A(98.18), kicker="Kuasa · tork", big="394 PS · *450 NM*", fs=120),
        dict(at=A(98.52), until=A(102.40), kicker="Gearbox", big="PDK *8-SPEED*"),
        dict(at=A(102.70), until=A(106.32), kicker="0–100 km/j", big="*3.9* SAAT", fs=150),
        # features
        dict(at=A(106.54), until=A(109.44), kicker="Siap dengan · 01", big="AERO *KIT*"),
        dict(at=A(109.46), until=A(110.68), kicker="02", big="*SPOILER*"),
        dict(at=A(110.80), until=A(111.86), kicker="03", big="SPORTS *EXHAUST*"),
        dict(at=A(112.10), until=A(113.78), kicker="04 · Rim depan", big="*20* INCI", fs=150),
        dict(at=A(113.92), until=A(115.80), kicker="05 · Rim belakang", big="*21* INCI", fs=150),
        dict(at=A(120.70), until=A(122.20), kicker="Bahagian dalam", big="APA *ADA?*"),
        dict(at=A(122.72), until=A(124.24), kicker="Jam", big="SPORT *CHRONO*", chips=["KUNING"]),
        dict(at=A(124.58), until=A(126.30), kicker="Stereng", big="*GT* SPORT", fs=140),
        dict(at=A(126.66), until=A(128.64), kicker="Headrest", big="LOGO *TIMBUL*"),
        dict(at=A(131.74), until=A(134.00), kicker="Seat belt", big="TALI PINGGANG *KUNING*", fs=110),
        # CTA
        dict(at=A(137.42), until=A(140.42), kicker="Porsche 911 Carrera 992.2", big="BERMINAT?",
             chips=[(A(139.62), "TEKAN LINK", True)], thump=True),
    ],
)

MUSIC = dict(file="/home/user/drive_dl/porsche/Music/music.mp4", start=1.0, lufs=-29, duck_db=8, fade_out=1.8)
