"""Paper edit: "Gaji berapa layak pakai Toyota GR86?" (raw: IMG_1307.MOV, 2:35 selfie talking head,
4K HLG 30 fps). Theme: PAPER (collage) — receipt-style cards fill in as each number is spoken.
Selfie framing: face fills the top half, so every paper element lives in the lower half (y >= ~980).
All times are SOURCE seconds.
"""
THEME = "paper"
FACE = (0.47, 0.42)
# Video shown as a taped "photo" on cream paper (top), paper cards in the free space below.
LAYOUT = dict(kind="inset", box=(110, 150, 860, 860), border=16)

def k(t, s=1.05, c=FACE, mode=None):
    return (t, s, *c) + ((mode,) if mode else ())

SEGMENTS = [
    dict(id="hook", a=(1.50, 6.40), keys=[k(1.5, 1.3), k(6.4, 1.12)],
         why="Hook = the question itself. Dropped 'Hari ni saya nak share dekat korang semua'."),
    dict(id="variants", a=(9.50, 13.10), keys=[k(9.5, 1.0, FACE)],
         why="3 variants. Dropped 'So basically sebenarnya'."),
    dict(id="rc_sz", a=(13.10, 18.40), keys=[k(13.1, 1.12)], why="RC, SZ."),
    dict(id="rz1", a=(18.70, 21.85), keys=[k(18.7, 1.0, FACE)], why="RZ top spec..."),
    dict(id="rz2", a=(23.20, 24.10), keys=[k(23.2, 1.25)], why="...'spec RZ'. Dropped 'which is itu adalah'."),
    dict(id="price", a=(24.20, 35.60), keys=[k(24.2, 1.0, FACE), k(32.7, 1.3, FACE, "cut")],
         why="Mid spec ~RM140,000 (2022). Punch on the number."),
    dict(id="insurans", a=(36.10, 45.80), keys=[k(36.1, 1.12)], why="Insurance RM2,300 with 55% NCD."),
    dict(id="roadtax", a=(46.20, 57.00), keys=[k(46.2, 1.0, FACE)],
         why="Road tax RM780, 2.4 NA no turbo. Dropped the repeat 'So untuk road taxnya RM780'."),
    dict(id="fee", a=(60.10, 64.70), keys=[k(60.1, 1.12)],
         why="Processing fee RM2,800. Dropped the repeat 'itu adalah processing fee daripada company'."),
    dict(id="otr", a=(68.82, 77.50), keys=[k(68.82, 1.0, FACE), k(73.7, 1.3, FACE, "cut")],
         why="Total OTR RM145,880 = first payoff. Punch on the number."),
    dict(id="noloan", a=(78.20, 87.50), keys=[k(78.2, 1.12), k(82.0, 1.3, FACE, "cut"), k(83.3, 1.0, FACE, "cut")],
         why="No full loan, min 20% down payment. Punch on 'tak boleh'."),
    dict(id="dp", a=(87.70, 103.95), keys=[k(87.7, 1.12)], why="DP RM28,000, loan RM117,880."),
    dict(id="tenure", a=(104.80, 108.70), keys=[k(104.8, 1.0, FACE)],
         why="9-year loan. Dropped 109-123 s: two restarts of the same sentence + 'RM1300 lebih, macam tu'."),
    dict(id="monthly", a=(123.80, 127.95), keys=[k(123.8, 1.12), k(127.1, 1.3, FACE, "cut")],
         why="Monthly ~RM1,317. Dropped 'sekitar macam tu lah'."),
    dict(id="rule", a=(129.50, 141.85), keys=[k(129.5, 1.0, FACE)],
         why="1/3 salary rule: monthly x 3 = ~RM3,900. Dropped 'macam tu'."),
    dict(id="answer", a=(142.30, 152.80), keys=[k(142.3, 1.12), k(144.2, 1.3, FACE, "cut")],
         why="Payoff: round up to RM4,000 = the answer to the hook."),
]

WORD_FIX = {}

Y = 1075
GRAPHICS = [
    dict(kind="tape", at=0.0, dur=999, x=150, y=160, rot=-38, w=170),
    dict(kind="tape", at=0.0, dur=999, x=930, y=160, rot=38, w=170),
    dict(kind="hooktext", at=1.56, dur=4.3, y=Y + 20,
         lines=[("GAJI BERAPA", 120, False), ("layak pakai", 88, False), ("TOYOTA GR86?", 150, True)]),
    dict(kind="receipt", at=11.70, until=24.10, y=Y + 40, title="3 SPEC GR86", rows=[
        (15.02, "Spec 1", "RC"),
        (17.46, "Spec 2", "SZ"),
        (23.60, "Spec 3 · paling atas", "RZ"),
    ]),
    dict(kind="receipt", at=32.80, until=81.95, y=Y, title="KOS ON THE ROAD", rh=66, rows=[
        (32.80, "Harga 2022 (anggaran)", "RM140,000"),
        (41.84, "Insurans · NCD 55%", "RM2,300"),
        (49.84, "Road tax · 2.4 NA", "RM780"),
        (63.20, "Processing fee", "RM2,800"),
        (73.84, "ON THE ROAD", "RM145,880", "total"),
    ]),
    dict(kind="stamp", at=82.06, dur=2.0, text="TAK BOLEH FULL LOAN", y=1300, x=540, fs=88, rot=-6),
    dict(kind="receipt", at=93.94, until=128.40, y=Y, title="KIRA LOAN", rows=[
        (93.94, "Down payment 20%", "RM28,000"),
        (101.92, "Jumlah loan", "RM117,880"),
        (107.98, "Tempoh", "9 tahun"),
        (127.16, "BULANAN", "± RM1,317", "total"),
    ]),
    dict(kind="receipt", at=131.78, until=144.15, y=Y + 40, title="RULE 1/3 GAJI", rows=[
        (135.24, "Bulanan", "RM1,317"),
        (137.04, "Darab", "× 3"),
        (139.64, "Gaji minimum", "± RM3,900", "total"),
    ]),
    dict(kind="price", at=144.22, dur=99, text="RM4,000", sub="GAJI LAYAK", y=1230),
]

KEYPOINTS = [
    (26.16, 2.3, "Ambil spec *pertengahan*"),
    (29.68, 2.2, "Anggaran tahun *2022*"),
    (84.72, 7.0, "Minimum *20%* down payment"),
]

MUSIC = dict(file="/home/user/drive_dl/Music/music1.mp4", start=1.6, lufs=-28, duck_db=8, fade_out=1.8)
