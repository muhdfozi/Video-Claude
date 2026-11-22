"""Toyota Alphard Z 2025 (unit 2: mileage 7,000, grade 4) — POJI PADU (showroom theme) + studio voice.
Raw (Drive "Raw Video", 4K 60p HLG, POV): IMG_1438 = intro (car, specs, hook question), IMG_1445 = the maths,
IMG_1446 = features walk-through; B-roll IMG_1447 front 3/4, 1448 front close, 1449 cabin + sunroof,
1450 dashboard, 1451 rear. The three talking clips' audio is concatenated into one track (all48k.wav,
offsets below) -> DeepFilterNet3 -> VOICE="studio". The cut-off "Untuk RM200..." at the end of IMG_1438 is dropped.
Exact totals (user rule): 283,000 + 840 + 3,900 + 2,800 = RM290,540 (presenter: "290,000 lebih");
rule 1/3: RM3,200 x 3 = RM9,600 (presenter: "darabkan dengan 3", no figure; monthly is his "3,200 lebih").
Whisper fixes: "Rock tax" = road tax, "JBR" = JBL, "sport orange 18 inci" = sport rim 18 inci (to confirm).
Order (poji padu): hook -> car -> maths -> answer -> features -> CTA. All times = COMBINED audio seconds.
"""
R = "/home/user/drive_dl/Raw Video 11/"
W = "/home/user/work11/"
SOURCES = {k: R + f"IMG_{n}.MOV" for k, n in [("m38", 1438), ("m45", 1445), ("m46", 1446), ("b47", 1447),
                                               ("b48", 1448), ("b49", 1449), ("b50", 1450), ("b51", 1451)]}
O45, O46 = 21.14, 21.14 + 36.286667
def A45(t): return O45 + t
def A46(t): return O46 + t

THEME = "showroom"
ACCENT = "E6C07B"
AUDIO = W + "all48k_df.wav"
VOICE = "studio"
GRAPHICS, KEYPOINTS = [], []
C = (0.5, 0.5)

def K(v, s=1.06, c=C, s2=None, d=4.0):
    return [(v, s, *c)] + ([(v + d, s2, *c)] if s2 else [])

def seg(id, a0, a1, src, v, keys, why):
    return dict(id=id, a=(a0, a1), vsrc=src, v=v, keys=keys, why=why)

SEGMENTS = [
    # hook: the question over the two hero front shots
    seg("hookA", 17.04, 18.14, "b47", 0.0, K(0.0, 1.04, C, 1.10, 1.2), "'Berapakah gaji yang layak' over the front 3/4."),
    seg("hookB", 18.14, 19.16, "b48", 0.2, K(0.2, 1.04, C, 1.10, 1.0), "'...untuk Alphard ni?' over the front close-up."),
    # car
    seg("intro", 0.00, 9.52, "m38", 0.0, K(0.0, 1.05, C, 1.15, 9.5), "New unit, Alphard Z 2025, 7,000 km, grade 4, lengkap."),
    seg("ada", 9.52, 12.72, "m38", 9.52, K(9.52), "JBL, HUD, sunroof, side step (checklist card)."),
    seg("kurang", 12.72, 16.40, "m38", 12.72, K(12.72, 1.08, C, 1.16, 3.6), "No Modelista body kit -> 'kita akan belanja'."),
    # maths
    seg("kira", A45(0.0), A45(14.14), "m45", 0.0, K(0.0, 1.05, C, 1.12, 14.0), "Jom kira: body, road tax, insurance, fee."),
    seg("total", A45(14.14), A45(19.16), "m45", 14.14, K(14.14), "Total on the road."),
    seg("loan", A45(19.16), A45(27.14), "m45", 19.16, K(19.16), "9-year full loan, no DP -> ~RM3,200."),
    seg("rule", A45(27.14), A45(30.82), "m45", 27.14, K(27.14, 1.08, C, 1.14, 3.6), "x3 = 1/3 of salary."),
    seg("answer", A45(30.82), A45(33.22), "m45", 30.82, K(30.82), "'Gaji inilah yang layak' -> RM9,600."),
    # features
    seg("led", A46(0.0), A46(1.45), "b48", 0.0, K(0.0, 1.06, (0.5, 0.45), 1.14, 1.4), "Full LED over the headlights close-up."),
    seg("f1", A46(1.45), A46(6.10), "m46", 1.45, K(1.45), "Sport rim 18, 360 camera, 2 power doors (POV)."),
    seg("boot", A46(6.10), A46(7.00), "b51", 0.2, K(0.2, 1.05), "Power boot over the rear shot."),
    seg("f2", A46(7.00), A46(16.30), "m46", 7.0, K(7.0), "Side step, moonroof, JBL, roof monitor, seats, digital meter."),
    seg("f3", A46(16.90), A46(22.05), "m46", 16.9, K(16.9), "'Nampak tu?' HUD, parking assist, Toyota Teammate."),
    # CTA
    seg("cta", A45(33.22), A45(35.32), "b47", 0.1, K(0.1, 1.04, C, 1.12, 2.1), "CTA over the hero front 3/4."),
]

FRONT, CABIN = W + "still_front.png", W + "still_cabin.png"
F1 = "/home/user/fonts_dl/f1/Formula1-Bold.ttf"
MASK_MODEL = "birefnet-general-lite"
BEHIND = [
    dict(win=(17.04, 18.14), font=F1, top="TOYOTA", main="ALPHARD *Z*", bottom=740, width=1050, top_scale=0.42, dim=0.38, enter="slam", exit=False),
    dict(win=(18.14, 19.16), font=F1, top="TOYOTA", main="ALPHARD *Z*", bottom=660, width=1050, top_scale=0.42, dim=0.38, enter="settle", exit=True),
]

FEATS = [(0.74, "FULL *LED*"), (1.72, "SPORT RIM *18\"*"), (3.14, "360 *CAMERA*"), (4.54, "2 POWER *DOOR*"),
         (6.22, "POWER *BOOT*"), (7.20, "SIDE *STEP*"), (8.16, "*MOONROOF*"), (9.30, "JBL *SOUND*"),
         (11.14, "ROOF *MONITOR*"), (12.44, "ELECTRONIC *SEAT*"), (13.84, "MEMORY *SEAT*"), (14.98, "METER *DIGITAL*"),
         (18.00, "HEAD-UP *DISPLAY*"), (19.58, "PARKING *ASSIST*"), (21.24, "TOYOTA *TEAMMATE*")]
_feat_lowers = []
for i, (t, txt) in enumerate(FEATS):
    nxt = FEATS[i + 1][0] if i + 1 < len(FEATS) else 22.02
    if i == 11: nxt = 16.28                       # pause before "Nampak tu?"
    _feat_lowers.append(dict(at=A46(t), until=A46(nxt), kicker=f"Feature {i + 1:02d} / {len(FEATS)}", big=txt, fs=118))

SHOWROOM = dict(
    cards=[
        dict(win=(9.50, 12.70), kicker="Everything lengkap", heading="SIAP DENGAN", head_fs=110, ghost="LENGKAP",
             photo=CABIN, box=(90, 450, 900, 520),
             items=[dict(kind="checklist", y=1060, x=150, items=[(10.08, "JBL sound system"), (10.86, "Head-up display"),
                                                                 (11.66, "Sunroof"), (12.24, "Side step")])]),
        dict(win=(A45(1.40), A45(5.14)), kicker="Alphard Z 2025", heading="HARGA BODY", head_fs=120, ghost="HARGA",
             photo=FRONT, box=(90, 470, 900, 620),
             items=[dict(kind="counter", at=A45(2.95), to=283000, y=1330, fs=170, lab="Harga jual")],
             footer="Toyota Alphard Z 2025 · grade 4 · 7,000 km"),
        dict(win=(A45(14.14), A45(19.16)), kicker="Kos on the road", heading="JUMLAH", head_fs=130, ghost="TOTAL",
             items=[dict(kind="tiles", y=520, tiles=[(A45(14.30), "Harga body", "283,000"), (A45(14.50), "Road tax", "840"),
                                                     (A45(14.70), "Insurans", "3,900"), (A45(14.90), "Processing", "2,800")]),
                    dict(kind="counter", at=A45(16.46), to=290540, y=1200, fs=180, lab="On the road",
                         sub="283,000 + 840 + 3,900 + 2,800")]),
        dict(win=(A45(19.16), A45(27.12)), kicker="Full loan · tanpa DP", heading="KIRA LOAN", head_fs=120, ghost="LOAN",
             items=[dict(kind="ring", at=A45(21.02), n=9, y=760, unit="TAHUN"),
                    dict(kind="chip", at=A45(22.70), text="TANPA DOWN PAYMENT", y=1055),
                    dict(kind="counter", at=A45(25.34), to=3200, y=1330, fs=160, pre="± ", lab="Bulanan (anggaran)")]),
        dict(win=(A45(30.82), A45(33.20)), kicker="Jawapan", heading="GAJI LAYAK", head_fs=120, ghost="GAJI",
             items=[dict(kind="fraction", at=A45(30.84), frac=1 / 3, text="1/3", unit="ANSURAN", y=720),
                    dict(kind="counter", at=A45(31.00), to=9600, y=1170, fs=190, lab="Sebulan",
                         sub="RM3,200 × 3 = RM9,600 (anggaran)")]),
    ],
    lowers=[
        # hook
        dict(at=17.04, until=18.12, kicker="Harga on the road", counter=dict(to=290540, dur=1.0), fs=150, y=1480),
        dict(at=18.14, until=19.14, kicker="Soalan hari ni", big="GAJI BERAPA *LAYAK?*", fs=120, y=1480, thump=True),
        # car
        dict(at=0.20, until=2.06, kicker="Baru sampai showroom", big="UNIT *BARU*"),
        dict(at=2.08, until=4.44, kicker="Toyota", big="ALPHARD *Z*", chips=["2025"]),
        dict(at=4.96, until=7.30, kicker="Mileage original", odometer=7000, suffix="KM"),
        dict(at=7.32, until=8.06, kicker="Grade", big="*4*", fs=160),
        dict(at=8.08, until=9.48, kicker="Serba lengkap", big="EVERYTHING *LENGKAP*"),
        dict(at=12.72, until=15.42, kicker="Kurang satu je", big="BODY KIT *MODELISTA*", fs=110),
        dict(at=15.44, until=16.40, kicker="Body kit Modelista", big="KITA *BELANJA!*", thump=True),
        # maths
        dict(at=A45(0.0), until=A45(1.38), kicker="Bab 01", big="JOM *KIRA*", thump=True),
        dict(at=A45(5.14), until=A45(14.12), box="Kos on the road", box_h=460, y=1300,
             rows=[(A45(6.12), "Road tax", "RM840"), (A45(9.94), "Insurans · NCD 55%", "RM3,900"), (A45(12.90), "Processing fee", "RM2,800")]),
        dict(at=A45(27.14), until=A45(30.80), kicker="Rule 1/3 gaji", big="RM3,200 *× 3*", fs=140),
        # features
        *_feat_lowers,
        # CTA
        dict(at=A45(33.26), until=A45(35.30), kicker="Alphard Z 2025", big="BERMINAT?", chips=[(A45(34.60), "TEKAN LINK", True)], thump=True),
    ],
)

MUSIC = dict(file="/home/user/drive_dl/Raw Video 10/music2.mp4", start=1.52, lufs=-29, duck_db=8, fade_out=1.8)
