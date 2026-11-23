"""Honda Civic FL5 Type R 2025 (Rally Red, grade 5A, 44 km) — POJI PADU (showroom theme) + studio voice.
Audio = separate VOICEOVER (Drive "Voiceover/Jalan 1-48G 11.m4a", 77.7 s) -> DeepFilterNet3 -> VOICE="studio".
Video (Drive "Raw Video", 4K 60p HLG): IMG_1847 POV intro walk-up, IMG_1833 POV gesturing (maths take),
B-roll 1834 front 3/4, 1835 wheel + red caliper, 1836 meter (44 km), 1837 6-speed shifter (30p), 1838 dashboard,
1839 red seats, 1840 rear seats, 1841 rear, 1842 rear 3/4, 1843 POV pointing at the rear, 1844 front wheel.
All times a= are VOICEOVER seconds; video from vsrc at v=. All pauses cut; the doubled
"Jadi korang kalikan saja dengan 3" keeps the first take; "Assalamualaikum" dropped.
Exact totals (user rule): 253,000 + 3,600 + 380 + 2,800 = RM259,780 (VO: "259,000 lebih");
rule 1/3: RM2,800 x 3 = RM8,400 (VO: "kalikan dengan 3", no figure; monthly is his "2,800 lebih").
Whisper fixes: "CVFL5" = Civic FL5; "kapak warna merah" = karpet warna merah (to confirm).
Order (poji padu): hook -> car -> maths -> answer -> features -> CTA.
"""
R = "/home/user/drive_dl/Raw Video 12/"
W = "/home/user/work12/"
SOURCES = {f"b{n % 100:02d}": R + f"IMG_{n}.MOV" for n in [1834, 1835, 1836, 1837, 1838, 1839, 1840, 1841, 1842, 1843, 1844]}
SOURCES.update({"m33": R + "IMG_1833.MOV", "m47": R + "IMG_1847.MOV"})
THEME = "showroom"
ACCENT = "E6C07B"
AUDIO = W + "vo48k_df.wav"
VOICE = "studio"
VAD_DB = -45
GRAPHICS, KEYPOINTS = [], []
CC = (0.5, 0.5)

def K(v, s=1.06, c=CC, s2=None, d=4.0):
    return [(v, s, *c)] + ([(v + d, s2, *c)] if s2 else [])

def seg(id, a0, a1, src, v, keys, why):
    return dict(id=id, a=(a0, a1), vsrc=src, v=v, keys=keys, why=why)

SEGMENTS = [
    # hook
    seg("hookA", 13.88, 15.26, "b34", 0.2, K(0.2, 1.04, CC, 1.10, 1.4), "'Berapakah gaji yang layak untuk' over the front 3/4."),
    seg("hookB", 15.26, 17.06, "m47", 1.0, K(1.0, 1.06, CC, 1.12, 1.8), "'...memiliki Honda Civic FL5 ni?' POV pointing at the car."),
    # car
    seg("intro", 0.00, 5.12, "m47", 0.0, K(0.0, 1.05, CC, 1.12, 5.0), "Honda Civic FL5 Type R 2025."),
    seg("red", 5.12, 7.24, "b44", 0.0, K(0.0, 1.04, CC, 1.10, 1.7), "Rally Red over the front wheel/fender."),
    seg("grade", 7.24, 9.08, "m47", 6.0, K(6.0, 1.08), "Grade 5A."),
    seg("mile1", 9.08, 10.46, "m47", 8.0, K(8.0, 1.10), "'Mileage original hanya'."),
    seg("odo", 10.46, 13.08, "b36", 0.0, K(0.0, 1.03, CC, 1.10, 2.2), "'44 kilometer sahaja' over the meter."),
    # maths
    seg("jom", 17.14, 18.72, "m33", 0.0, K(0.0, 1.05), "Jom kira (POV)."),
    seg("harga", 18.72, 24.30, "m33", 0.6, K(0.6), "Body price RM253,000 (card)."),
    seg("kos", 24.28, 36.24, "m33", 6.0, K(6.0, 1.05, CC, 1.12, 12.0), "Insurance, road tax, processing fee (ledger box)."),
    seg("total", 36.24, 41.98, "m33", 13.0, K(13.0), "Total on the road (card)."),
    seg("loan", 41.96, 51.06, "m33", 18.4, K(18.4), "9-year loan, no DP, ~RM2,800 (card)."),
    seg("rule", 51.04, 53.76, "m33", 21.6, K(21.6, 1.08, CC, 1.14, 2.6), "'Kalikan dengan 3' (live gesture at the same moment)."),
    seg("answer", 56.08, 64.20, "m33", 24.0, K(24.0), "1/3 of salary -> RM8,400 (card)."),
    # features
    seg("unit", 64.18, 66.42, "b38", 0.0, K(0.0, 1.04, CC, 1.10, 2.2), "'Jadi untuk unit Honda Civic FL5 ni' over the dashboard."),
    seg("seats", 66.40, 68.26, "b39", 0.3, K(0.3, 1.04, CC, 1.10, 1.8), "Red interior = red bucket seats."),
    seg("manual", 68.24, 69.66, "b37", 0.0, K(0.0, 1.05, CC, 1.12, 1.4), "Manual 6-speed = shifter."),
    seg("carpet", 69.66, 70.76, "b40", 0.4, K(0.4, 1.05), "Red carpet over the cabin floor/rear seats."),
    seg("rear", 70.74, 72.50, "b42", 0.0, K(0.0, 1.04, CC, 1.10, 1.7), "'Bahagian belakang yang sangat seksi' = rear 3/4."),
    # CTA
    seg("cta", 72.48, 76.24, "b43", 0.6, K(0.6, 1.04, CC, 1.10, 3.6), "CTA over the POV pointing at the rear."),
]

FRONT = W + "still_1834.png"; SEATS = W + "still_1839.png"
F1 = "/home/user/fonts_dl/f1/Formula1-Bold.ttf"
MASK_MODEL = "birefnet-general-lite"
BEHIND = [
    dict(win=(13.88, 15.26), font=F1, top="HONDA CIVIC", main="TYPE *R*", bottom=750, width=1000, top_scale=0.30, dim=0.45, enter="slam", exit=False),
    dict(win=(15.26, 17.06), font=F1, top="HONDA CIVIC", main="TYPE *R*", bottom=905, width=1000, top_scale=0.30, dim=0.45, enter="settle", exit=True),
]

SHOWROOM = dict(
    cards=[
        dict(win=(19.60, 24.30), kicker="Civic FL5 Type R 2025", heading="HARGA BODY", head_fs=120, ghost="HARGA",
             photo=FRONT, box=(90, 470, 900, 620),
             items=[dict(kind="counter", at=22.50, to=253000, y=1330, fs=170, lab="Harga jual")],
             footer="Honda Civic FL5 Type R 2025 · grade 5A · 44 km"),
        dict(win=(36.24, 41.98), kicker="Kos on the road", heading="JUMLAH", head_fs=130, ghost="TOTAL",
             items=[dict(kind="tiles", y=520, tiles=[(36.40, "Harga body", "253,000"), (36.60, "Insurans", "3,600"),
                                                     (36.80, "Road tax", "380"), (37.00, "Processing", "2,800")]),
                    dict(kind="counter", at=39.26, to=259780, y=1200, fs=180, lab="On the road",
                         sub="253,000 + 3,600 + 380 + 2,800")]),
        dict(win=(43.50, 51.04), kicker="Full loan · tanpa DP", heading="KIRA LOAN", head_fs=120, ghost="LOAN",
             items=[dict(kind="ring", at=44.56, n=9, y=760, unit="TAHUN"),
                    dict(kind="chip", at=46.30, text="TANPA DOWN PAYMENT", y=1055),
                    dict(kind="counter", at=48.68, to=2800, y=1330, fs=160, pre="± ", lab="Bulanan (anggaran)")]),
        dict(win=(56.08, 64.18), kicker="Jawapan", heading="GAJI LAYAK", head_fs=120, ghost="GAJI",
             items=[dict(kind="fraction", at=56.10, frac=1 / 3, text="1/3", unit="ANSURAN", y=720),
                    dict(kind="counter", at=58.92, to=8400, y=1170, fs=190, lab="Sebulan",
                         sub="RM2,800 × 3 = RM8,400 (anggaran)")]),
    ],
    lowers=[
        # hook
        dict(at=13.88, until=15.24, kicker="Harga on the road", counter=dict(to=259780, dur=1.1), fs=150, y=1480),
        dict(at=15.26, until=17.04, kicker="Soalan hari ni", big="GAJI BERAPA *LAYAK?*", fs=120, y=1480, thump=True),
        # car
        dict(at=1.74, until=5.10, kicker="Honda Civic FL5", big="TYPE *R*", chips=["2025"], fs=150),
        dict(at=5.84, until=7.22, kicker="Warna", big="RALLY *RED*"),
        dict(at=7.98, until=9.06, kicker="Grade", big="*5A*", fs=150),
        dict(at=9.10, until=13.06, kicker="Mileage original", odometer=44, suffix="KM", keep=True),
        # maths
        dict(at=17.16, until=18.70, kicker="Bab 01", big="JOM *KIRA*", thump=True),
        dict(at=18.72, until=19.58, kicker="Pertama sekali", big="HARGA *BODY*"),
        dict(at=24.28, until=36.22, box="Kos on the road", box_h=460, y=1300,
             rows=[(27.02, "Insurans · NCD 55%", "RM3,600"), (30.80, "Road tax · 2.0", "RM380"), (34.78, "Processing fee", "RM2,800")]),
        dict(at=41.96, until=43.48, kicker="Bab 02", big="KIRA *LOAN*", thump=True),
        dict(at=51.04, until=53.74, kicker="Rule 1/3 gaji", big="RM2,800 *× 3*", fs=140),
        # features
        dict(at=64.18, until=66.40, kicker="Civic FL5 Type R", big="APA *ADA?*"),
        dict(at=66.86, until=68.22, kicker="Dalaman", big="SERBA *MERAH*"),
        dict(at=68.24, until=69.64, kicker="Transmisi", big="MANUAL *6-SPEED*", fs=110),
        dict(at=69.70, until=70.74, kicker="Lantai", big="KARPET *MERAH*"),
        dict(at=70.80, until=72.46, kicker="Bahagian belakang", big="SANGAT *SEKSI*", thump=True),
        # CTA
        dict(at=72.50, until=76.22, kicker="Civic FL5 Type R", big="BERMINAT?", chips=[(75.02, "TEKAN LINK", True)], thump=True),
    ],
)

MUSIC = dict(file="/home/user/drive_dl/Raw Video 10/music2.mp4", start=1.52, lufs=-29, duck_db=8, fade_out=1.8)
