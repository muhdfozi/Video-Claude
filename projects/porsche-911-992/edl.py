"""Porsche 911 Carrera 992.2 2025 (Cartagena Yellow, grade 5A, 2,538 km, recond Japan, unregistered) — POJI PADU
(showroom theme) + studio voice.
Audio = separate VOICEOVER (Drive "Voiceover/Jalan 1-48G 38.m4a", 186.3 s) -> DeepFilterNet3 (vo_df.wav), then the
engine start-up from IMG_1952 (10.70-14.30 s, its own audio) is spliced in at 132.70 s, right after
"...bunyi exhaust dia." (vo_final.wav, 189.9 s). A(t) maps a voiceover time to the spliced track.
Video (Drive "Raw Video", 4K HLG): 1952 rear low close (engine start + taillights at 11 s), 1954 meter boot (2,538 km),
1955 rear, 1958 front 3/4, 1960 rear 3/4 pan, 1961 side, 1962 seat, 1963 cabin/steering, 1964 Sport Chrono clock,
1966 console (PDK, body-colour trim), 1967 yellow belt, 1968 headrest crest, 1971 rear 3/4 + wing, 1973 POV rear 3/4,
1975 front close, 1976 POV front 3/4, 1979 front wheel, 1980 rear wheel + wing, 1981 wing close.
Exact totals (user rule): OTR 888,000 + 11,000 + 2,130 + 2,800 = RM903,930 (VO "903,000 lebih");
loan 80% = 710,400, DP 20% = 177,600; 2.3% x 9 yrs = 147,052.80; (710,400 + 147,052.80) / 108 = RM7,939.38/month
(VO "7,900 lebih"); x3 = RM23,818 (VO: "inilah gaji", no figure). Official RM1.43 mil, same terms: RM12,785/month
-> RM38,356 (VO "38,000"). Difference vs official: 1,430,000 - 888,000 = RM542,000.
Dropped: "Guys, hari ni kita ada sebuah unit" (hook starts on the car), the restart "Trim dua laman berwarna",
the repeated "dan seat belt berwarna kuning", "Sekian".
Whisper fixes: "Ingin" = Enjin, "spot exhaust" = sports exhaust, "spot chrono" = Sport Chrono,
"akantara GT spot" = Alcantara GT Sport, "RM3.0 liter" = 3.0 liter.
Order (poji padu): hook -> car -> maths -> answer -> engine sound -> features -> CTA.
"""
R = "/home/user/drive_dl/porsche/Raw Video/"
W = "/home/user/work_porsche/"
SOURCES = {f"b{n % 100:02d}": R + f"IMG_{n}.MOV" for n in
           [1952, 1954, 1955, 1958, 1960, 1961, 1962, 1963, 1964, 1966, 1967, 1968, 1971, 1975, 1979, 1980, 1981]}
SOURCES.update({"p73": R + "IMG_1973.MOV", "p76": R + "IMG_1976.MOV"})
THEME = "showroom"
ACCENT = "E6C07B"
AUDIO = W + "vo_final.wav"
VOICE = "studio"
VAD_DB = -45
GRAPHICS, KEYPOINTS = [], []
CC = (0.5, 0.5)

INS, ENG = 132.70, 3.60          # engine start-up spliced into the voiceover here (seconds of the VO / its length)


def A(t):
    """Voiceover time -> time in the spliced track (vo_final.wav)."""
    return t + (ENG if t >= INS else 0.0)


def K(v, s=1.06, c=CC, s2=None, d=4.0):
    return [(v, s, *c)] + ([(v + d, s2, *c)] if s2 else [])


def seg(id, a0, a1, src, v, keys, why, **kw):
    return dict(id=id, a=(A(a0), A(a1)), vsrc=src, v=v, keys=keys, why=why, **kw)


CARD = "p76"     # footage under full-screen cards is never seen
SEGMENTS = [
    # hook
    seg("hookA", 1.56, 3.10, "b58", 0.0, K(0.0, 1.08, CC, 1.16, 1.6), "'Porsche 911 facelift' — front 3/4, 911 title behind the car."),
    seg("hookB", 3.10, 5.10, "p76", 0.3, K(0.3, 1.08, (0.5, 0.48), 1.15, 2.0), "'yang baru tahun 2025' — POV at the car, title settles and exits."),
    seg("hookC", 5.10, 8.50, "b60", 0.0, K(0.0, 1.04, CC, 1.12, 3.4), "'harganya lebih RM500,000' — rear 3/4 pan (counter RM542,000)."),
    seg("hookD", 8.50, 13.60, "p76", 3.0, K(3.0, 1.05, CC, 1.12, 5.0), "'murah berbanding harga rasmi Porsche Malaysia yang baru'."),
    seg("hookQ", 13.96, 18.02, "p73", 0.0, K(0.0, 1.05, CC, 1.12, 4.0), "Hook question: gaji berapa layak?"),
    seg("teka", 18.70, 22.64, "p73", 4.3, K(4.3, 1.08), "Teka dalam komen (interactive)."),
    # car
    seg("model", 23.26, 26.32, "b61", 0.0, K(0.0, 1.04, CC, 1.10, 3.0), "911 Carrera 992.2 over the side profile."),
    seg("model2", 26.32, 29.62, "b71", 0.0, K(0.0, 1.04, CC, 1.10, 3.2), "'facelift paling latest' over rear 3/4 + wing."),
    seg("colour", 29.74, 31.26, "b75", 0.3, K(0.3, 1.04, CC, 1.10, 1.5), "'Warnanya adalah warna' front close."),
    seg("colour2", 31.26, 33.08, "b55", 0.0, K(0.0, 1.04, CC, 1.10, 1.8), "Cartagena Yellow over the rear (lights on)."),
    seg("mileage", 33.08, 38.02, "b54", 4.3, K(4.3, 1.06, (0.5, 0.55), 1.14, 4.8), "Mileage 2,538 km over the meter."),
    seg("status", 38.34, 46.24, "p76", 8.4, K(8.4, 1.05, CC, 1.12, 7.8), "Grade 5A, recond Japan, unregistered (POV)."),
    # maths
    seg("jom", 47.66, 49.02, "p73", 8.6, K(8.6, 1.08), "Jom kira."),
    seg("harga", 49.02, 57.12, CARD, 0.0, K(0.0), "Card: body price RM888,000."),
    seg("rasmi", 57.86, 63.30, CARD, 0.0, K(0.0), "Card: official from RM1.43 mil."),
    seg("beza", 63.36, 66.90, CARD, 6.0, K(6.0), "Card: difference RM542,000."),
    seg("kos", 68.36, 80.34, "p76", 16.2, K(16.2, 1.05, CC, 1.12, 11.0), "Ledger box: insurance, road tax, fee."),
    seg("otr", 80.54, 84.74, CARD, 0.0, K(0.0), "Card: OTR RM903,930."),
    seg("performa", 88.50, 92.86, "p73", 15.8, K(15.8, 1.05, CC, 1.12, 4.4), "Performance car: no full loan."),
    seg("loan", 93.10, 104.66, CARD, 0.0, K(0.0), "Card: loan 80% / DP 20%."),
    seg("bulanan", 105.50, 112.82, CARD, 12.0, K(12.0), "Card: 9 years @ 2.3% -> RM7,939."),
    seg("rule", 112.94, 118.20, "b52", 0.5, K(0.5, 1.04, CC, 1.12, 5.3), "Rule 1/3 and x3 (rear close, lights off)."),
    seg("gaji", 118.66, 123.06, CARD, 0.0, K(0.0), "Card: salary RM23,818."),
    seg("gajirasmi", 123.60, 128.30, CARD, 5.0, K(5.0), "Card: official unit -> RM38,356."),
    # engine sound (spliced audio block is [INS, INS + ENG) of the spliced track, same clip/time as its video)
    seg("dengar", 128.92, INS - 1e-9, "b52", 6.92, K(6.92, 1.04, CC, 1.10, 3.8), "'jom kita dengarkan bunyi exhaust dia'."),
    dict(id="engine", a=(INS, INS + ENG), vsrc="b52", v=10.70, keys=K(10.70, 1.10, CC, 1.18, 3.6), cut_pauses=False,
         why="Engine start-up: taillights light up with the sound (no voice)."),
    # features
    seg("enjin", 133.56, 142.56, "b52", 14.30, K(14.30, 1.10, CC, 1.04, 9.0), "3.0 flat-six twin turbo, 394 PS, 450 Nm (idle, lights on)."),
    seg("pdk", 142.56, 145.20, "b66", 0.0, K(0.0, 1.04, (0.62, 0.45), 1.12, 2.6), "PDK 8-speed over the selector."),
    seg("sprint", 145.34, 148.60, "b60", 0.0, K(0.0, 1.10, CC, 1.02, 3.3), "0-100 in 3.9 s (rear 3/4 pan)."),
    seg("aero", 149.08, 151.60, "b58", 0.2, K(0.2, 1.04, CC, 1.12, 2.5), "Aero kit (front lip, wing)."),
    seg("spoiler", 151.60, 152.80, "b81", 0.6, K(0.6, 1.04, CC, 1.10, 1.2), "Spoiler / fixed wing close-up."),
    seg("exhaust", 152.80, 154.00, "b52", 22.80, K(22.80, 1.20, (0.45, 0.75), 1.26, 1.2), "Sports exhaust, black tips."),
    seg("rim20", 154.00, 155.62, "b79", 0.3, K(0.3, 1.04, CC, 1.10, 1.6), "Front rim 20 inch."),
    seg("rim21", 155.62, 157.90, "b80", 0.5, K(0.5, 1.04, CC, 1.10, 2.3), "Rear rim 21 inch."),
    seg("dalam", 157.90, 158.92, "b63", 0.0, K(0.0, 1.04), "'Bahagian dalam'."),
    seg("chrono", 158.92, 161.40, "b64", 0.2, K(0.2, 1.10, (0.5, 0.52), 1.22, 2.5), "Sport Chrono clock, yellow."),
    seg("stereng", 161.40, 163.42, "b63", 0.9, K(0.9, 1.08, (0.45, 0.45), 1.16, 2.0), "GT Sport steering (Alcantara)."),
    seg("seat", 163.42, 166.22, "b62", 0.0, K(0.0, 1.04, CC, 1.10, 2.8), "Seat."),
    seg("headrest", 166.22, 168.14, "b68", 0.0, K(0.0, 1.06, CC, 1.14, 1.9), "Porsche crest embossed on the headrest."),
    seg("belt", 168.58, 171.70, "b67", 0.0, K(0.0, 1.04, CC, 1.14, 3.1), "Yellow seat belts."),
    seg("trim", 176.70, 180.82, CARD, 0.0, K(0.0), "Card: interior checklist + trim in body colour."),
    # CTA
    seg("cta", 181.36, 185.34, "p76", 26.7, K(26.7, 1.04, CC, 1.12, 4.0), "CTA, ends on the front 3/4 (loops to the hook)."),
]

FRONT, REAR, CONSOLE = W + "still_front.png", W + "still_rear.png", W + "still_console.png"
F1 = "/home/user/fonts_dl/f1/Formula1-Bold.ttf"
MASK_MODEL = "birefnet-general-lite"
BEHIND = [
    dict(win=(A(1.56), A(3.10)), font=F1, top="PORSCHE", main="*911*", bottom=770, width=820, top_scale=0.26, dim=0.42, enter="slam", exit=False),
    dict(win=(A(3.10), A(5.10)), font=F1, top="PORSCHE", main="*911*", bottom=935, width=820, top_scale=0.26, dim=0.42, enter="settle", exit=True),
]

SHOWROOM = dict(
    cards=[
        dict(win=(A(49.02), A(57.12)), kicker="Porsche 911 Carrera 992.2", heading="HARGA BODY", head_fs=120, ghost="HARGA",
             photo=FRONT, box=(90, 470, 900, 620),
             items=[dict(kind="counter", at=A(55.14), to=888000, y=1330, fs=170, lab="Harga jual")],
             footer="Porsche 911 Carrera 992.2 · 2025 · 2,538 km"),
        dict(win=(A(57.86), A(66.90)), kicker="Harga rasmi Porsche Malaysia", heading="VS *RASMI*", head_fs=130, ghost="BEZA",
             items=[dict(kind="counter", at=A(60.84), to=1430000, y=720, fs=150, lab="Unit baru · bermula",
                         sub="Harga pelancaran · April 2025"),
                    dict(kind="counter", at=A(65.04), to=542000, y=1210, fs=190, lab="Beza",
                         sub="1,430,000 − 888,000"),
                    dict(kind="chip", at=A(65.80), text="LEBIH MURAH", y=1460, solid=True)]),
        dict(win=(A(80.54), A(84.74)), kicker="Kos on the road", heading="JUMLAH", head_fs=130, ghost="TOTAL",
             items=[dict(kind="tiles", y=520, tiles=[(A(80.60), "Harga body", "888,000"), (A(80.80), "Insurans", "11,000"),
                                                     (A(81.00), "Road tax", "2,130"), (A(81.20), "Processing", "2,800")]),
                    dict(kind="counter", at=A(82.54), to=903930, y=1200, fs=180, lab="On the road",
                         sub="888,000 + 11,000 + 2,130 + 2,800")]),
        dict(win=(A(93.10), A(104.66)), kicker="Kereta performa · tiada full loan", heading="LOAN *80%*", head_fs=130, ghost="LOAN",
             items=[dict(kind="chip", at=A(94.60), text="DOWN PAYMENT 20%", y=540),
                    dict(kind="counter", at=A(99.42), to=177600, y=800, fs=150, lab="Down payment 20%", sub="888,000 × 20%"),
                    dict(kind="counter", at=A(103.40), to=710400, y=1230, fs=170, lab="Jumlah loan 80%", sub="888,000 × 80%")]),
        dict(win=(A(105.50), A(112.82)), kicker="9 tahun · interest 2.3%", heading="ANSURAN", head_fs=130, ghost="BULAN",
             items=[dict(kind="ring", at=A(105.86), n=9, y=760, unit="TAHUN"),
                    dict(kind="chip", at=A(107.50), text="INTEREST 2.30%", y=1055),
                    dict(kind="counter", at=A(109.76), to=7939, y=1330, fs=170, lab="Bulanan",
                         sub="(710,400 + 147,052.80) ÷ 108 bulan")]),
        dict(win=(A(118.66), A(123.06)), kicker="Jawapan", heading="GAJI LAYAK", head_fs=120, ghost="GAJI",
             items=[dict(kind="fraction", at=A(118.68), frac=1 / 3, text="1/3", unit="ANSURAN", y=720),
                    dict(kind="counter", at=A(119.36), to=23818, y=1170, fs=190, lab="Gaji sebulan",
                         sub="RM7,939.38 × 3 = RM23,818"),
                    dict(kind="chip", at=A(121.50), text="KORANG LAYAK? KOMEN ↓", y=1440, solid=True)]),
        dict(win=(A(123.60), A(128.30)), kicker="Kalau ambil unit baru", heading="UNIT *RASMI*", head_fs=130, ghost="RASMI",
             items=[dict(kind="tiles", y=520, tiles=[(A(123.96), "Harga", "1.43 JUTA"), (A(124.40), "Ansuran", "12,785")]),
                    dict(kind="counter", at=A(126.52), to=38356, y=1060, fs=190, lab="Gaji diperlukan",
                         sub="Loan 80% · 9 thn · 2.3% → RM12,785 × 3")]),
        dict(win=(A(176.70), A(180.82)), kicker="Bahagian dalam", heading="SIAP *DENGAN*", head_fs=120, ghost="DALAM",
             photo=CONSOLE, box=(90, 470, 900, 560),
             items=[dict(kind="checklist", y=1110, x=150,
                         items=[(A(176.80), "Sport Chrono kuning"), (A(177.10), "Stereng GT Sport"),
                                (A(177.40), "Logo timbul headrest"), (A(177.70), "Tali pinggang kuning"),
                                (A(179.08), "Trim warna badan")])]),
    ],
    lowers=[
        # hook
        dict(at=A(1.62), until=A(5.08), kicker="Harga on the road", counter=dict(to=903930, dur=1.2), fs=150, y=1480),
        dict(at=A(5.80), until=A(13.58), kicker="Lebih murah dari harga rasmi", counter=dict(to=542000, dur=1.3), fs=150, y=1480),
        dict(at=A(13.96), until=A(18.00), kicker="Soalan hari ni", big="GAJI BERAPA *LAYAK?*", fs=120, y=1480, thump=True),
        dict(at=A(18.70), until=A(22.62), kicker="Sebelum kira", big="TEKA DALAM *KOMEN*", fs=120,
             chips=[(A(21.18), "TULIS GAJI KORANG ↓", True)], thump=True),
        # car
        dict(at=A(24.10), until=A(29.60), kicker="Porsche 911", big="CARRERA *992.2*", chips=["2025", "FACELIFT"], fs=140),
        dict(at=A(31.26), until=A(33.06), kicker="Warna", big="*CARTAGENA* YELLOW"),
        dict(at=A(33.64), until=A(38.00), kicker="Mileage", odometer=2538, suffix="KM", keep=True),
        dict(at=A(38.34), until=A(39.82), kicker="Grade", big="*5A*", fs=150),
        dict(at=A(40.94), until=A(46.22), kicker="Status", big="RECOND *JEPUN*", chips=[(A(43.56), "BELUM REGISTER", True)]),
        # maths
        dict(at=A(47.66), until=A(49.00), kicker="Bab 01", big="JOM *KIRA*", thump=True),
        dict(at=A(68.36), until=A(80.32), box="Kos on the road", box_h=460, y=1300,
             rows=[(A(69.56), "Insurans · NCD 55%", "RM11,000"), (A(73.28), "Road tax · 3.0L", "RM2,130"),
                   (A(77.22), "Processing fee", "RM2,800")]),
        dict(at=A(88.50), until=A(92.84), kicker="Bab 02 · Kereta performa", big="TAK BOLEH *FULL LOAN*", fs=110, thump=True),
        dict(at=A(112.94), until=A(116.40), kicker="Rule paling simpel", big="MAKS *1/3 GAJI*", fs=130),
        dict(at=A(116.68), until=A(118.20), kicker="Ansuran × 3", big="RM7,939 *× 3*", fs=140),
        # engine sound
        dict(at=A(128.92), until=INS + ENG - 0.02, kicker="Kuatkan volume", big="BUNYI *EXHAUST*", fs=130,
             chips=[(INS, "VOLUME ↑", True)], thump=True),
        # features
        dict(at=A(133.56), until=A(137.14), kicker="Enjin", big="3.0L *FLAT-SIX*", chips=["TWIN TURBO"]),
        dict(at=A(137.56), until=A(142.54), kicker="Kuasa · tork", big="394 PS · *450 NM*", fs=120),
        dict(at=A(142.56), until=A(145.20), kicker="Gearbox", big="PDK *8-SPEED*"),
        dict(at=A(145.34), until=A(148.58), kicker="0–100 km/j", big="*3.9* SAAT", fs=150),
        dict(at=A(149.08), until=A(151.58), kicker="Siap dengan · 01", big="AERO *KIT*"),
        dict(at=A(151.82), until=A(152.78), kicker="02", big="*SPOILER*"),
        dict(at=A(152.96), until=A(153.98), kicker="03", big="SPORTS *EXHAUST*"),
        dict(at=A(154.14), until=A(155.60), kicker="04 · Rim depan", big="*20* INCI", fs=150),
        dict(at=A(155.86), until=A(157.88), kicker="05 · Rim belakang", big="*21* INCI", fs=150),
        dict(at=A(157.90), until=A(158.90), kicker="Bahagian dalam", big="APA *ADA?*"),
        dict(at=A(159.58), until=A(161.38), kicker="Jam", big="SPORT *CHRONO*", chips=["KUNING"]),
        dict(at=A(161.64), until=A(163.40), kicker="Stereng", big="*GT* SPORT", fs=140),
        dict(at=A(164.06), until=A(168.12), kicker="Headrest", big="LOGO *TIMBUL*"),
        dict(at=A(168.68), until=A(171.68), kicker="Seat belt", big="TALI PINGGANG *KUNING*", fs=110),
        # CTA
        dict(at=A(181.36), until=A(185.32), kicker="Porsche 911 Carrera 992.2", big="BERMINAT?",
             chips=[(A(184.08), "TEKAN LINK", True)], thump=True),
    ],
)

MUSIC = dict(file="/home/user/drive_dl/porsche/Music/music.mp4", start=1.0, lufs=-29, duck_db=8, fade_out=1.8)
