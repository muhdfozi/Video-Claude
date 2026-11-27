"""Toyota Alphard Z 2025 (unit 3: black, grade 5A, 12,000+ km, Modelista body kit) — POJI PADU + 110 BPM speed rule.
Audio = separate VOICEOVER (Drive "Voiceover/Jalan 1-48G 23.m4a", 100.4 s) -> DeepFilterNet3 -> VOICE="studio".
Video (4K 60p HLG): IMG_1871 POV front walk-up (22 s), IMG_1872 POV rear (7 s), B-roll 1863/1864 front 3/4,
1865 rear, 1866 cabin + sunroof, 1867 side step, 1868 dashboard, 1869 meter, 1870 head-up display (30p).
Retakes removed (last complete take kept): "Jadi gaji berapakah yang layak untuk" (x2), a false start after "RM840",
"Dan inilah gaji yang selayaknya untuk masuk loan Toyota Alphard Z" (x4, kept 70.4-74.9). "Assalamualaikum" dropped.
Exact totals (user rule): 280,000 + 3,900 + 840 + 2,800 = RM287,540 (VO: "287,000 lebih");
rule 1/3: RM3,200 x 3 = RM9,600 (VO gives the method; monthly is his "3,200 lebih").
Whisper fixes: "Alphazard"/"Alpha Z" = Alphard Z, "RM12,000" mileage = 12,000 km, "Rotax" = road tax, "server lengkap" = serba lengkap.
Speed rule (user: "macam biasa 110 bpm"): RENTAK grid -> music stretched to 110 BPM, graphics snap to the beat.
Order (poji padu): hook -> car -> maths -> answer -> features -> CTA. All a= are VOICEOVER seconds.
"""
R = "/home/user/drive_dl/Raw Video 13/"
W = "/home/user/work13/"
SOURCES = {f"b{n % 100:02d}": R + f"IMG_{n}.MOV" for n in range(1863, 1871)}
SOURCES.update({"m71": R + "IMG_1871.MOV", "m72": R + "IMG_1872.MOV"})
THEME = "showroom"
ACCENT = "E6C07B"
AUDIO = W + "vo48k_df.wav"
VOICE = "studio"
VAD_DB = -40
RENTAK = dict(bpm=110)
GRAPHICS, KEYPOINTS = [], []
CC = (0.5, 0.5)

def K(v, s=1.06, c=CC, s2=None, d=4.0):
    return [(v, s, *c)] + ([(v + d, s2, *c)] if s2 else [])

def seg(id, a0, a1, src, v, keys, why):
    return dict(id=id, a=(a0, a1), vsrc=src, v=v, keys=keys, why=why)

SEGMENTS = [
    # hook (second take of the question)
    seg("hookA", 15.74, 17.42, "b63", 0.1, K(0.1, 1.04, CC, 1.10, 1.6), "'Gaji berapakah yang layak untuk' over the front 3/4."),
    seg("hookB", 17.42, 19.56, "b64", 0.1, K(0.1, 1.04, CC, 1.10, 2.1), "'memiliki Toyota Alphard ni?' over the second front angle."),
    # car
    seg("intro", 0.00, 6.42, "m71", 0.0, K(0.0, 1.05, CC, 1.12, 6.4), "Alphard Z 2025 warna hitam (POV)."),
    seg("grade", 6.42, 10.16, "m71", 6.4, K(6.4, 1.08), "Grade 5A, mileage original..."),
    seg("mile", 10.16, 12.06, "b69", 0.0, K(0.0, 1.03, CC, 1.10, 1.6), "'12,000 lebih sahaja' over the meter."),
    # maths
    seg("jom", 19.64, 21.54, "m71", 10.2, K(10.2, 1.06), "Jom kira."),
    seg("harga", 22.04, 26.28, "m71", 12.0, K(12.0), "Body price RM280,000 (card)."),
    seg("kos1", 26.28, 34.90, "m71", 12.1, K(12.1, 1.05, CC, 1.12, 8.6), "Insurance, road tax 2.5 (ledger box)."),
    seg("kos2", 37.78, 41.80, "m72", 0.0, K(0.0, 1.05, CC, 1.10, 4.0), "Processing fee (false start before it removed)."),
    seg("total", 41.80, 47.12, "m72", 3.0, K(3.0), "Total on the road (card)."),
    seg("loan", 47.12, 55.06, "m72", 3.0, K(3.0), "9-year full loan, no DP -> ~RM3,200 (card)."),
    seg("rule", 55.06, 61.46, "m72", 3.0, K(3.0), "Rule paling simple: bulanan <= 1/3 gaji, darab 3 (card)."),
    seg("answer", 70.40, 74.92, "m72", 3.0, K(3.0), "Final take: 'Dan inilah gaji yang selayaknya...' (card)."),
    # features
    seg("unit", 75.74, 77.72, "b64", 0.1, K(0.1, 1.04, CC, 1.10, 2.0), "'Unit Toyota Alphard Z ni'."),
    seg("lengkap", 77.72, 79.14, "b68", 0.3, K(0.3, 1.04, CC, 1.10, 1.4), "Serba lengkap over the dashboard."),
    seg("bodykit", 79.14, 81.00, "b65", 0.1, K(0.1, 1.04, CC, 1.10, 1.9), "Body kit Modelista over the rear."),
    seg("doors", 81.00, 83.52, "b66", 0.0, K(0.0, 1.04, CC, 1.10, 2.4), "2 power door, pilot seat over the cabin."),
    seg("roofstep", 83.52, 85.72, "b67", 0.0, K(0.0, 1.04, CC, 1.10, 1.9), "Sunroof, side step over the side step."),
    seg("hud", 85.72, 87.46, "b70", 0.0, K(0.0, 1.04, CC, 1.10, 1.6), "Head-up display."),
    seg("assist", 87.46, 89.12, "b69", 0.0, K(0.0, 1.05, CC, 1.12, 1.6), "Toyota Teammate, parking assist over the meter."),
    seg("roofmon", 92.20, 94.14, "b66", 0.4, K(0.4, 1.10, (0.5, 0.35), 1.16, 1.9), "Roof monitor over the cabin ceiling."),
    # CTA
    seg("cta", 94.50, 98.30, "m72", 3.2, K(3.2, 1.04, CC, 1.10, 3.8), "CTA over the POV pointing at the rear."),
]

FRONT = W + "still_front.png"
F1 = "/home/user/fonts_dl/f1/Formula1-Bold.ttf"
MASK_MODEL = "birefnet-general-lite"
BEHIND = [
    dict(win=(15.74, 17.42), font=F1, top="TOYOTA", main="ALPHARD *Z*", bottom=640, width=1050, top_scale=0.42, dim=0.45, enter="slam", exit=False),
    dict(win=(17.42, 19.56), font=F1, top="TOYOTA", main="ALPHARD *Z*", bottom=725, width=1050, top_scale=0.42, dim=0.45, enter="settle", exit=True),
]

FEATS = [(76.46, "Unit ni", "SERBA *LENGKAP*", 78.32), (79.94, "Body kit", "*MODELISTA*", 81.00), (81.00, "Siap dengan", "2 POWER *DOOR*", 82.62),
         (82.64, "Siap dengan", "PILOT *SEAT*", 83.52), (83.52, "Siap dengan", "*SUNROOF*", 84.70), (84.72, "Siap dengan", "SIDE *STEP*", 85.70),
         (85.72, "Siap dengan", "HEAD-UP *DISPLAY*", 87.06), (87.08, "Siap dengan", "TOYOTA *TEAMMATE*", 88.28),
         (88.30, "Siap dengan", "PARKING *ASSIST*", 89.10), (93.28, "Dan juga", "ROOF *MONITOR*", 94.12)]

SHOWROOM = dict(
    cards=[
        dict(win=(22.04, 26.28), kicker="Alphard Z 2025", heading="HARGA BODY", head_fs=120, ghost="HARGA",
             photo=FRONT, box=(90, 470, 900, 620),
             items=[dict(kind="counter", at=24.52, to=280000, y=1330, fs=170, lab="Harga jual")],
             footer="Toyota Alphard Z 2025 · grade 5A · 12,000+ km"),
        dict(win=(41.80, 47.12), kicker="Kos on the road", heading="JUMLAH", head_fs=130, ghost="TOTAL",
             items=[dict(kind="tiles", y=520, tiles=[(41.95, "Harga body", "280,000"), (42.15, "Insurans", "3,900"),
                                                     (42.35, "Road tax", "840"), (42.55, "Processing", "2,800")]),
                    dict(kind="counter", at=44.46, to=287540, y=1200, fs=180, lab="On the road",
                         sub="280,000 + 3,900 + 840 + 2,800")]),
        dict(win=(47.12, 55.06), kicker="Full loan · tanpa DP", heading="KIRA LOAN", head_fs=120, ghost="LOAN",
             items=[dict(kind="ring", at=48.92, n=9, y=760, unit="TAHUN"),
                    dict(kind="chip", at=49.78, text="TANPA DOWN PAYMENT", y=1055),
                    dict(kind="counter", at=52.70, to=3200, y=1330, fs=160, pre="± ", lab="Bulanan (anggaran)")]),
        dict(win=(55.06, 61.46), kicker="Rule paling simple", heading="BULANAN ≤ 1/3 GAJI", head_fs=100, ghost="RULE",
             items=[dict(kind="fraction", at=58.42, frac=1 / 3, text="1/3", unit="GAJI", y=740),
                    dict(kind="text", at=60.28, text="RM3,200 × 3", y=1180, fs=110, bold=True, accent=True),
                    dict(kind="text", at=60.40, text="bulanan darab 3 = gaji layak", y=1300, fs=40)]),
        dict(win=(70.40, 74.92), kicker="Jawapan", heading="GAJI LAYAK", head_fs=120, ghost="GAJI",
             items=[dict(kind="counter", at=70.90, to=9600, y=900, fs=220, lab="Sebulan",
                         sub="RM3,200 × 3 = RM9,600 (anggaran)"),
                    dict(kind="chip", at=72.90, text="ALPHARD Z 2025", y=1180, solid=True)]),
    ],
    lowers=[
        # hook
        dict(at=15.74, until=17.40, kicker="Harga on the road", counter=dict(to=287540, dur=1.1), fs=150, y=1480),
        dict(at=17.42, until=19.54, kicker="Soalan hari ni", big="GAJI BERAPA *LAYAK?*", fs=120, y=1480, thump=True),
        # car
        dict(at=1.80, until=4.38, kicker="Toyota", big="ALPHARD *Z*", chips=["2025"]),
        dict(at=4.40, until=6.40, kicker="Warna", big="*HITAM*", fs=140),
        dict(at=7.56, until=8.72, kicker="Grade", big="*5A*", fs=150),
        dict(at=8.74, until=12.04, kicker="Mileage original", odometer=12000, suffix="KM+", keep=True),
        # maths
        dict(at=19.66, until=21.52, kicker="Bab 01", big="JOM *KIRA*", thump=True),
        dict(at=26.28, until=41.78, box="Kos on the road", box_h=460, y=1300,
             rows=[(29.34, "Insurans · NCD 55%", "RM3,900"), (33.16, "Road tax · 2.5", "RM840"), (40.22, "Processing fee", "RM2,800")]),
        # features
        dict(at=75.76, until=76.44, kicker="Toyota Alphard Z", big="UNIT *NI*"),
        *[dict(at=a, until=u, kicker=k, big=b, fs=118) for a, k, b, u in FEATS],
        # CTA
        dict(at=94.52, until=98.28, kicker="Alphard Z 2025", big="BERMINAT?", chips=[(97.12, "TEKAN LINK", True)], thump=True),
    ],
)

MUSIC = dict(file="/home/user/drive_dl/Raw Video 10/music2.mp4", start=1.52, lufs=-29, duck_db=8, fade_out=1.8)
