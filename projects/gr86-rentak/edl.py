"""GR86 "gaji layak" — STYLE RENTAK demo (the user's own style; see rentak_gfx.py).
110 BPM speed rule: music stretched to 110 BPM, every graphic lands on a beat. Same cut as gr86-glass.
Exact computed totals (user rule): OTR 145,880; 1,317 x 3 = 3,951 (presenter rounds to ~4,000).
Times = SOURCE seconds.
"""
THEME = "rentak"
ACCENT = "FF5A1F"
FACE = (0.47, 0.60)   # crop centre below the face: face sits in the top half, cards below

def k(t, s=1.22, c=FACE, mode=None):
    return (t, s, *c) + ((mode,) if mode else ())

SEGMENTS = [
    dict(id="hook", a=(1.50, 6.40), keys=[k(1.5, 1.36), k(6.4, 1.24)],
         why="Hook = the question itself. Dropped 'Hari ni saya nak share dekat korang semua'."),
    dict(id="variants", a=(9.50, 13.10), keys=[k(9.5, 1.18, FACE)],
         why="3 variants. Dropped 'So basically sebenarnya'."),
    dict(id="rc_sz", a=(13.10, 18.40), keys=[k(13.1, 1.26)], why="RC, SZ."),
    dict(id="rz1", a=(18.70, 21.85), keys=[k(18.7, 1.18, FACE)], why="RZ top spec..."),
    dict(id="rz2", a=(23.20, 24.10), keys=[k(23.2, 1.25)], why="...'spec RZ'. Dropped 'which is itu adalah'."),
    dict(id="price", a=(24.20, 35.60), keys=[k(24.2, 1.18, FACE), k(32.7, 1.38, FACE, "cut")],
         why="Mid spec ~RM140,000 (2022). Punch on the number."),
    dict(id="insurans", a=(36.10, 45.80), keys=[k(36.1, 1.26)], why="Insurance RM2,300 with 55% NCD."),
    dict(id="roadtax", a=(46.20, 57.00), keys=[k(46.2, 1.18, FACE)],
         why="Road tax RM780, 2.4 NA no turbo. Dropped the repeat 'So untuk road taxnya RM780'."),
    dict(id="fee", a=(60.10, 64.70), keys=[k(60.1, 1.26)],
         why="Processing fee RM2,800. Dropped the repeat 'itu adalah processing fee daripada company'."),
    dict(id="otr", a=(68.82, 77.50), keys=[k(68.82, 1.18, FACE), k(73.7, 1.38, FACE, "cut")],
         why="Total OTR RM145,880 = first payoff. Punch on the number."),
    dict(id="noloan", a=(78.20, 87.50), keys=[k(78.2, 1.26), k(82.0, 1.38, FACE, "cut"), k(83.3, 1.18, FACE, "cut")],
         why="No full loan, min 20% down payment. Punch on 'tak boleh'."),
    dict(id="dp", a=(87.70, 103.95), keys=[k(87.7, 1.26)], why="DP RM28,000, loan RM117,880."),
    dict(id="tenure", a=(104.80, 108.70), keys=[k(104.8, 1.18, FACE)],
         why="9-year loan. Dropped 109-123 s: two restarts of the same sentence + 'RM1300 lebih, macam tu'."),
    dict(id="monthly", a=(123.80, 127.95), keys=[k(123.8, 1.26), k(127.1, 1.38, FACE, "cut")],
         why="Monthly ~RM1,317. Dropped 'sekitar macam tu lah'."),
    dict(id="rule", a=(129.50, 141.85), keys=[k(129.5, 1.18, FACE)],
         why="1/3 salary rule: monthly x 3 = ~RM3,900. Dropped 'macam tu'."),
    dict(id="answer", a=(142.30, 152.80), keys=[k(142.3, 1.26), k(144.2, 1.38, FACE, "cut")],
         why="Payoff: round up to RM4,000 = the answer to the hook."),
]


GRAPHICS = []
KEYPOINTS = []
FACEBOX = (190, 340, 700, 560)

RENTAK = dict(bpm=110, chapters=[(1.50, "Soalan"), (9.50, "Spec"), (24.20, "Harga"), (36.10, "Kos OTR"),
                                  (78.20, "Loan"), (129.50, "Rule 1/3"), (142.30, "Jawapan")], items=[
    dict(kind="slam", at=1.56, words=["GAJI", "BERAPA", "LAYAK", "PAKAI", "GR86?"], acc=[4], fs=170, alpha="50", hold=2, y=1000),
    dict(kind="ledger", at=11.70, until=24.10, title="3 spec", rows=[(15.02, "Spec 1", "RC"), (17.46, "Spec 2", "SZ"),
                                                                    (23.60, "Spec 3 · top", "RZ")]),
    dict(kind="tag", at=26.16, dur=2.4, idx="SZ", text="Ambil spec *pertengahan*"),
    dict(kind="tag", at=29.68, dur=2.4, text="Anggaran tahun *2022*"),
    dict(kind="brackets", at=32.70, dur=2.6, box=FACEBOX, label="harga"),
    dict(kind="counter", at=32.80, dur=2.6, to=140000, label="Harga SZ 2022 · anggaran"),
    dict(kind="ledger", at=36.10, until=68.70, title="Kos on the road", rows=[(36.10, "Harga", "RM140,000"),
                                                                            (41.84, "Insurans · NCD 55%", "RM2,300"),
                                                                            (49.84, "Road tax · 2.4 NA", "RM780"),
                                                                            (63.20, "Processing fee", "RM2,800")]),
    dict(kind="slam", at=68.85, words=["TOTAL", "ON THE", "road"], acc=[2], hold=1),
    dict(kind="counter", at=73.84, dur=3.4, to=145880, label="On the road", sub="140,000 + 2,300 + 780 + 2,800", accent=True, flash=True),
    dict(kind="tag", at=82.06, dur=2.4, text="Tak boleh *full loan*"),
    dict(kind="tag", at=84.72, dur=3.0, idx="20%", text="Minimum *down payment*"),
    dict(kind="ledger", at=93.94, until=108.70, title="Kira loan", rows=[(93.94, "Down payment 20%", "RM28,000"),
                                                                        (101.92, "Jumlah loan", "RM117,880"),
                                                                        (107.98, "Tempoh", "9 tahun")]),
    dict(kind="brackets", at=125.90, dur=2.2, box=FACEBOX, label="bulanan"),
    dict(kind="counter", at=125.90, dur=2.2, to=1317, label="Bulanan · anggaran", sub="loan 9 tahun"),
    dict(kind="ledger", at=131.78, until=142.20, title="Rule 1/3 gaji", rows=[(135.24, "Bulanan", "RM1,317"),
                                                                             (137.04, "Darab", "× 3"),
                                                                             (139.64, "Gaji minimum", "RM3,951", "total")]),
    dict(kind="slam", at=142.30, words=["JAWAPAN"], acc=[], hold=1, fs=200),
    dict(kind="brackets", at=144.22, until=999, box=FACEBOX, label="gaji layak"),
    dict(kind="counter", at=144.22, until=999, to=3951, label="Gaji layak sebulan", sub="dibundarkan ≈ RM4,000", accent=True, flash=True),
])

MUSIC = dict(file="/home/user/drive_dl/Music/music1.mp4", start=1.6, lufs=-27, duck_db=8, fade_out=1.8)
