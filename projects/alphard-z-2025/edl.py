"""Toyota Alphard Z 2025 — "gaji berapa layak?" — STYLE KIRA DETAIL + studio voice.
Raw: Drive "Raw Video" (Nov 20): IMG_1615.MOV = 85 s presenter piece-to-camera in front of the car (4K-class HLG,
portrait), B-roll IMG_1592 (front 3/4), 1594 (captain seats + sunroof), 1595 (dashboard / JBL head unit),
1596 (meter cluster), 1601 (rear, tailgate open) and photos IMG_1604/1605/1606 (front / side / rear) turned into
2 s 9:16 panning clips (ph_*.mov, BT.2020-tagged so they go through the same colour path as the iPhone clips).
Voice (user): "direkod dengan high end microphone dan di dalam studio" -> DeepFilterNet3 + VOICE="studio".
Retakes removed: "harga bodinya RM300... sorry" (kept the RM298,000 take, spliced after the first "Pertama sekali")
and the doubled "untuk bulanan dia pula" (kept the second).
Exact totals (user rule): 298,000 + 4,100 + 840 + 2,800 = RM305,740 (presenter: "305,000 lebih");
rule 1/3: RM3,400 x 3 = RM10,200 (presenter gives the method, not the number).
Whisper fixes: "Rock tax" = road tax, "Alphazet" = Alphard Z, "Toyota T-MAT" = Toyota Teammate.
Order (user preference): hook -> car -> maths -> answer -> features review -> CTA.
"""
R = "/home/user/drive_dl/Raw Video 10/"
W = "/home/user/work10/"
SOURCES = {"b92": R + "IMG_1592.MOV", "b94": R + "IMG_1594.MOV", "b95": R + "IMG_1595.MOV", "b96": R + "IMG_1596.MOV",
           "b01": R + "IMG_1601.MOV", "pfront": W + "ph_IMG_1604.mov", "pside": W + "ph_IMG_1605.mov",
           "prear": W + "ph_IMG_1606.mov"}
THEME = "glass"
ACCENT = "C8102E"
AUDIO = W + "a48k_df.wav"   # DeepFilterNet3-cleaned
VOICE = "studio"
FACE = (0.37, 0.43)         # presenter stands left of centre, car behind

def K(v, s=1.08, c=(0.5, 0.5), s2=None, d=4.0):
    return [(v, s, *c)] + ([(v + d, s2, *c)] if s2 else [])

SEGMENTS = [
    # hook: the question, first over the hero front shot, then the presenter pointing at the car
    dict(id="hookA", a=(24.66, 27.14), vsrc="b92", v=0.15, keys=K(0.15, 1.04, (0.5, 0.5), 1.16, 2.5), why="Hook question over the hero front 3/4."),
    dict(id="hookB", a=(27.14, 29.62), keys=K(27.14, 1.18, FACE), why="'...Alphard yang ada dekat sebelah saya ni'."),
    # car
    dict(id="intro", a=(0.00, 9.76), keys=K(0.0, 1.10, FACE, 1.28, 9.0), why="Alphard Z 2025, fully loaded, grade 5A, 5,000+ km."),
    # maths
    dict(id="pertama", a=(30.04, 30.76), keys=K(30.04, 1.15, FACE), why="'Pertama sekali' (first take)."),
    dict(id="harga", a=(37.97, 43.18), keys=K(37.97, 1.15, FACE), why="Retake: '...untuk harga bodinya ... RM298,000 sahaja'."),
    dict(id="ins", a=(43.18, 47.10), keys=K(43.18, 1.15, FACE), why="Insurance NCD 55% RM4,100."),
    dict(id="road", a=(47.50, 53.50), keys=K(47.5, 1.15, FACE), why="Road tax RM840, processing fee RM2,800."),
    dict(id="total", a=(53.68, 58.66), keys=K(53.68, 1.12, FACE), why="Total on the road."),
    dict(id="loan", a=(62.95, 70.62), keys=K(62.95, 1.12, FACE), why="Second take of 'untuk bulanan dia pula' -> ~RM3,400."),
    dict(id="rule", a=(71.00, 72.50), keys=K(71.0, 1.12, FACE), why="'Berapakah gaji yang layak?'"),
    dict(id="rule2", a=(73.40, 75.58), keys=K(73.4, 1.2, FACE), why="'RM3,400 kalikan saja dengan 3' (filler 'haa' cut)."),
    dict(id="answer", a=(75.66, 80.64), keys=K(75.66, 1.12, FACE), why="'Itulah gaji yang selayaknya' -> RM10,200."),
    # features review
    dict(id="bodykit", a=(9.76, 12.52), keys=K(9.76, 1.0, (0.5, 0.55), 1.12, 2.8), why="Body kit Modelista: wide on presenter + car."),
    dict(id="depan", a=(12.52, 13.52), vsrc="pfront", v=0.0, keys=K(0.0, 1.0), why="'Bahagian depan' photo."),
    dict(id="tepi", a=(13.52, 14.36), vsrc="pside", v=0.0, keys=K(0.0, 1.0), why="'Bahagian tepi' photo (pan)."),
    dict(id="belakang", a=(14.36, 15.66), vsrc="prear", v=0.0, keys=K(0.0, 1.0), why="'Bahagian belakang' photo."),
    dict(id="jbl1", a=(15.66, 18.12), vsrc="b94", v=0.0, keys=K(0.0, 1.04, (0.5, 0.5), 1.12, 3.0), why="Sound system: cabin / captain seats."),
    dict(id="jbl2", a=(18.12, 20.86), vsrc="b95", v=0.0, keys=K(0.0, 1.04, (0.5, 0.5), 1.12, 3.0), why="'daripada JBL, Player JBL' over the dashboard."),
    dict(id="hud", a=(20.86, 21.50), vsrc="b96", v=0.3, keys=K(0.3, 1.06), why="Head-up display -> driver display shot."),
    dict(id="assist", a=(21.50, 24.24), keys=K(21.5, 1.22, FACE), why="Parking assist, Toyota Teammate."),
    # CTA
    dict(id="cta", a=(80.74, 82.96), vsrc="b01", v=0.0, keys=K(0.0, 1.04, (0.5, 0.55), 1.12, 2.2), why="CTA over the rear with tailgate open."),
]

GRAPHICS = []
KEYPOINTS = []

GLASS = [
    dict(win=(39.40, 53.46), items=[
        dict(kind="card", title="Kos on the road", rows=[(40.26, "Harga body", "RM298,000"),
                                                       (45.50, "Insurans · NCD 55%", "RM4,100"),
                                                       (48.98, "Road tax", "RM840"),
                                                       (52.26, "Processing fee", "RM2,800")]),
    ]),
    dict(win=(53.70, 58.62), items=[
        dict(kind="label", text="Jumlah"),
        dict(kind="counter", at=55.64, to=305740, frm=0, dur=1.2, lab="On the road", sub="298,000 + 4,100 + 840 + 2,800", accent=True),
    ]),
    dict(win=(64.40, 70.58), items=[
        dict(kind="card", title="Kira loan", rows=[(65.30, "Tempoh loan", "9 tahun"),
                                                   (66.40, "Down payment", "Tiada (full loan)"),
                                                   (69.34, "Bulanan (anggaran)", "± RM3,400")]),
    ]),
    dict(win=(71.02, 75.54), items=[
        dict(kind="label", text="Rule 1/3 gaji"),
        dict(kind="cards", items=[(71.60, "01 · Rule", "Ansuran = 1/3 gaji"),
                                  (73.44, "02 · Kira", "RM3,400 × 3"),
                                  (74.80, "03 · Hasil", "RM10,200 sebulan")]),
    ]),
    dict(win=(75.70, 80.58), items=[
        dict(kind="label", text="Jawapan"),
        dict(kind="counter", at=75.76, to=10200, frm=0, dur=1.1, lab="Gaji layak", sub="RM3,400 × 3 = RM10,200 sebulan", accent=True),
    ]),
]

OVERLAYS = [
    dict(kind="counter_pill", at=24.70, dur=4.8, to=305740, frm=0, dur_roll=1.4, lab="Alphard Z 2025 · on the road", sub="Gaji berapa layak?"),
    dict(kind="title", at=30.06, dur=1.4, chip="JOM KIRA", accent="Gaji layak?"),
    dict(kind="pill", at=1.04, dur=2.2, text="Toyota Alphard *Z* 2025"),
    dict(kind="pill", at=3.32, dur=2.0, text="*Fully loaded*"),
    dict(kind="pill", at=6.26, dur=1.0, text="Grade *5A*"),
    dict(kind="pill", at=7.30, dur=2.3, text="Mileage *5,000+ km*"),
    dict(kind="pill", at=10.90, dur=1.5, text="Body kit *Modelista*"),
    dict(kind="pill", at=12.60, dur=2.9, text="Depan · tepi · *belakang*"),
    dict(kind="pill", at=18.16, dur=2.5, text="Sound system *JBL*"),
    dict(kind="pill", at=20.92, dur=0.6, text="*Head-up* display"),
    dict(kind="pill", at=21.56, dur=1.1, text="Parking *assist*"),
    dict(kind="pill", at=22.78, dur=1.4, text="Toyota *Teammate*"),
    dict(kind="pill", at=81.30, dur=1.5, text="Berminat? Tekan *link*"),
]

MUSIC = dict(file="/home/user/drive_dl/Raw Video 10/music2.mp4", start=1.52, lufs=-29, duck_db=8, fade_out=1.8)
