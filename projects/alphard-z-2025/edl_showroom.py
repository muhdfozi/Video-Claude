"""Toyota Alphard Z 2025 — SHOWROOM theme preview (inspired by, not copied from, a TikTok car explainer).
Same cut, studio voice and music as edl.py (style kira detail); only the graphics change:
full-screen night-showroom cards for the maths (~40% of the run) + lower-thirds on footage.
All times are SOURCE seconds (IMG_1615 / its audio).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edl import SOURCES, AUDIO, VOICE, SEGMENTS, MUSIC, R, W   # noqa: F401  (same cut as the kira-detail edit)

THEME = "showroom"
ACCENT = "E6C07B"          # champagne
GRAPHICS, KEYPOINTS = [], []
FRONT, DASH = R + "IMG_1604.JPG", W + "still_dash.png"

SHOWROOM = dict(
    cards=[
        dict(win=(37.97, 43.18), kicker="Alphard Z 2025", heading="HARGA BODY", head_fs=120, ghost="HARGA",
             photo=FRONT, box=(90, 470, 900, 620),
             items=[dict(kind="counter", at=40.26, to=298000, y=1330, fs=170, lab="Harga jual")],
             footer="Toyota Alphard Z 2025 · grade 5A"),
        dict(win=(53.68, 58.66), kicker="Kos on the road", heading="JUMLAH", head_fs=130, ghost="TOTAL",
             items=[dict(kind="tiles", y=520, tiles=[(53.80, "Harga body", "298,000"), (54.00, "Insurans", "4,100"),
                                                     (54.20, "Road tax", "840"), (54.40, "Processing", "2,800")]),
                    dict(kind="counter", at=55.64, to=305740, y=1200, fs=180, lab="On the road",
                         sub="298,000 + 4,100 + 840 + 2,800")]),
        dict(win=(64.40, 70.62), kicker="Full loan · tanpa DP", heading="KIRA LOAN", head_fs=120, ghost="LOAN",
             items=[dict(kind="ring", at=65.44, n=9, y=760, unit="TAHUN"),
                    dict(kind="chip", at=66.40, text="TANPA DOWN PAYMENT", y=1055),
                    dict(kind="counter", at=69.34, to=3400, y=1330, fs=160, pre="± ", lab="Bulanan (anggaran)", sfx="cash")]),
        dict(win=(75.68, 80.62), kicker="Jawapan", heading="GAJI LAYAK", head_fs=120, ghost="GAJI",
             items=[dict(kind="fraction", at=75.70, frac=1 / 3, text="1/3", unit="ANSURAN", y=720),
                    dict(kind="counter", at=75.90, to=10200, y=1170, fs=190, lab="Sebulan",
                         sub="RM3,400 × 3 = RM10,200")]),
        dict(win=(19.72, 24.24), kicker="Fully loaded", heading="SIAP DENGAN", head_fs=110, ghost="LENGKAP",
             photo=DASH, box=(90, 450, 900, 520),
             items=[dict(kind="checklist", y=1060, x=150, items=[(19.72, "Player JBL"), (20.94, "Head-up display"),
                                                                 (21.70, "Parking assist"), (22.78, "Toyota Teammate")])]),
    ],
    lowers=[
        # hook
        dict(at=24.66, until=27.12, kicker="Alphard Z 2025 · on the road", counter=dict(to=305740, dur=1.3), fs=150, y=1480),
        dict(at=27.14, until=29.62, kicker="Soalan hari ni", big="GAJI BERAPA *LAYAK?*", fs=120, y=1480, thump=True),
        # car
        dict(at=1.04, until=3.30, kicker="Toyota", big="ALPHARD *Z*", chips=["2025"]),
        dict(at=3.32, until=5.48, kicker="Serba lengkap", big="FULLY *LOADED*"),
        dict(at=6.26, until=7.24, kicker="Grade", big="*5A*", fs=150),
        dict(at=7.28, until=9.76, kicker="Mileage original", odometer=5000, suffix="KM+"),
        # maths
        dict(at=30.04, until=30.76, kicker="Bab 01", big="JOM *KIRA*", thump=True),
        dict(at=43.20, until=53.50, box="Kos on the road", box_h=460, y=1300,
             rows=[(45.50, "Insurans · NCD 55%", "RM4,100"), (48.98, "Road tax", "RM840"), (52.26, "Processing fee", "RM2,800")]),
        dict(at=62.95, until=64.40, kicker="Bab 02", big="KIRA *LOAN*", thump=True),
        dict(at=71.00, until=72.50, kicker="Rule 1/3 gaji", big="GAJI BERAPA *LAYAK?*", fs=120),
        dict(at=73.40, until=75.58, kicker="Ansuran × 3", big="RM3,400 *× 3*", fs=140),
        # features review
        dict(at=9.80, until=12.50, kicker="Siap dengan body kit", big="*MODELISTA*", fs=140),
        dict(at=12.52, until=13.50, kicker="01 · Modelista", big="DEPAN"),
        dict(at=13.52, until=14.34, kicker="02 · Modelista", big="TEPI"),
        dict(at=14.36, until=15.64, kicker="03 · Modelista", big="BELAKANG"),
        dict(at=15.70, until=19.30, kicker="Siap juga dengan", big="SOUND *SYSTEM*"),
        dict(at=19.36, until=19.70, kicker="Sound system", big="*JBL*", fs=160),
        # CTA
        dict(at=80.74, until=82.96, kicker="Alphard Z 2025", big="BERMINAT?", chips=[(81.30, "TEKAN LINK", True)], thump=True),
    ],
)
