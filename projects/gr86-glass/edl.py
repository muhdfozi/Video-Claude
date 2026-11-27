"""GR86 "gaji layak" — GLASS theme (same cut as projects/gr86-gaji, different graphics).
Frosted-glass chapters (presenter blurred + washed white) carry the numbers; presenter full screen
with dark pills between chapters. No subtitles (user rule). Original HDR colour. Times = SOURCE seconds.
"""
THEME = "glass"
ACCENT = "C8102E"          # GR red
FACE = (0.47, 0.40)

def k(t, s=1.05, c=FACE, mode=None):
    return (t, s, *c) + ((mode,) if mode else ())

SEGMENTS = [
    dict(id="hook", a=(1.50, 6.40), keys=[k(1.5, 1.25), k(6.4, 1.1)],
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

GRAPHICS = []
KEYPOINTS = []

GLASS = [
    dict(win=(11.70, 24.15), items=[
        dict(kind="label", text="3 spec GR86"),
        dict(kind="timeline", rows=[(15.02, "RC", "spec 1"), (17.46, "SZ", "spec 2 · pertengahan"),
                                    (23.60, "RZ", "spec 3 · paling atas")]),
    ]),
    dict(win=(32.70, 45.85), items=[
        dict(kind="card", title="Kos on the road", rows=[(32.80, "Harga 2022 (anggaran)", "RM140,000"),
                                                       (41.84, "Insurans · NCD 55%", "RM2,300")]),
    ]),
    dict(win=(49.70, 64.75), items=[
        dict(kind="card", title="Kos on the road", rows=[(32.80, "Harga 2022 (anggaran)", "RM140,000"),
                                                       (41.84, "Insurans · NCD 55%", "RM2,300"),
                                                       (49.84, "Road tax · 2.4 NA", "RM780"),
                                                       (63.20, "Processing fee", "RM2,800")]),
    ]),
    dict(win=(73.60, 78.00), items=[
        dict(kind="label", text="Jumlah"),
        dict(kind="counter", at=73.84, to=145880, frm=0, dur=1.3, lab="On the road", sub="harga + insurans + road tax + fee", accent=True),
    ]),
    dict(win=(93.80, 108.75), items=[
        dict(kind="card", title="Kira loan", rows=[(93.94, "Down payment 20%", "RM28,000"),
                                                   (101.92, "Jumlah loan", "RM117,880"),
                                                   (107.98, "Tempoh", "9 tahun")]),
    ]),
    dict(win=(129.50, 142.00), items=[
        dict(kind="label", text="Rule 1/3 gaji"),
        dict(kind="cards", items=[(131.78, "01 · Rule", "Ansuran ≤ 1/3 gaji"),
                                  (137.04, "02 · Kira", "RM1,317 × 3"),
                                  (140.16, "03 · Hasil", "± RM3,900 sebulan")]),
    ]),
    dict(win=(144.10, 999), items=[
        dict(kind="label", text="Jawapan"),
        dict(kind="counter", at=144.22, to=4000, frm=0, dur=1.4, lab="Gaji layak", sub="untuk loan Toyota GR86", accent=True, y=920),
    ]),
]

OVERLAYS = [
    dict(kind="counter_pill", at=1.56, dur=4.6, to=145880, frm=0, dur_roll=1.4, lab="Toyota GR86 · on the road", sub="Gaji berapa layak?"),
    dict(kind="title", at=9.50, dur=2.0, chip="TOYOTA GR86", accent="Gaji layak?"),
    dict(kind="pill", at=26.16, dur=2.6, text="Ambil spec *pertengahan* (SZ)"),
    dict(kind="pill", at=29.68, dur=2.6, text="Anggaran tahun *2022*"),
    dict(kind="pill", at=82.06, dur=2.4, text="Tak boleh *full loan*"),
    dict(kind="pill", at=84.72, dur=3.2, text="Minimum *20%* down payment"),
    dict(kind="counter_pill", at=125.90, dur=2.4, to=1317, frm=0, dur_roll=1.2, lab="Bulanan · 9 tahun", sub="anggaran sebulan"),
]

MUSIC = dict(file="/home/user/drive_dl/Music/music1.mp4", start=1.6, lufs=-28, duck_db=8, fade_out=1.8)
