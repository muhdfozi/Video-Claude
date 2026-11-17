"""Toyota Vellfire Z Premier 2024 — "gaji berapa layak?" — STYLE KIRA DETAIL, built from a SEPARATE VOICEOVER
("Jalan 1-48G 16.m4a", 71 s) + 8 iPhone clips (IMG_1452..1459, 4K HLG; 1454 = 62 s POV walkaround, others B-roll).
Audio times (a=) are VOICEOVER seconds; video comes from vsrc at v=. All pauses in the voiceover are cut.
"Natural, like recorded live at the showroom": VOICE="location" (light cleanup + early reflections, no studio sheen)
+ AMBIENT = the walkaround's real location sound under the voice; every line is matched to the shot it describes.
Exact totals (user rule): OTR 326,000 + 4,500 + 740 + 2,800 = RM334,040 (voiceover: "334,000 lebih");
rule 1/3: RM3,700 x 3 = RM11,100 (voiceover gives the method, not the number).
Whisper fixes: "Rock Tax" = road tax, "RM2.4, RM740" = enjin 2.4 -> road tax RM740.
Order (user preference): hook -> car -> jom kira -> maths -> answer -> car review -> CTA.
"""
R = "/home/user/drive_dl/Raw Video 9/"
SOURCES = {k: R + f"IMG_{n}.MOV" for k, n in
           [("w", 1454), ("b52", 1452), ("b53", 1453), ("b55", 1455), ("b56", 1456), ("b57", 1457), ("b58", 1458), ("b59", 1459)]}
THEME = "glass"
ACCENT = "C8102E"
AUDIO = "/home/user/work9/vo48k.wav"
VOICE = "location"
VAD_DB = -45
AMBIENT = dict(file=R + "IMG_1454.MOV", lufs=-33)
CAR = (0.47, 0.44)

def K(v, s=1.08, c=(0.5, 0.5), s2=None):
    return [(v, s, *c)] + ([(v + 4.0, s2, *c)] if s2 else [])

SEGMENTS = [
    dict(id="hookA", a=(20.00, 22.50), vsrc="b52", v=0.0, keys=K(0.0, 1.05, (0.5, 0.52), 1.18), why="Hook question over the hero front shot."),
    dict(id="hookB", a=(22.50, 25.10), vsrc="w", v=26.30, keys=K(26.3, 1.1, (0.5, 0.5)), why="Front 3/4 approach finishes the question."),
    dict(id="intro", a=(0.00, 8.80), vsrc="w", v=0.30, keys=K(0.3, 1.22, CAR, 1.3), why="Model, grade 5A, 4,000+ km over the live POV with his hand."),
    dict(id="jom", a=(25.40, 27.25), vsrc="w", v=9.20, keys=K(9.2, 1.25, CAR), why="'Jom kita buat kira-kira'."),
    dict(id="otr1", a=(27.30, 45.60), vsrc="w", v=11.0, keys=K(11.0, 1.15, CAR), why="Body price, insurance, road tax, processing fee."),
    dict(id="otr2", a=(45.65, 49.88), vsrc="w", v=27.2, keys=K(27.2), why="Total on the road (side of the car behind the glass)."),
    dict(id="loan", a=(49.90, 59.00), vsrc="w", v=31.6, keys=K(31.6), why="9-year loan, no DP, ~RM3,700+/month."),
    dict(id="rule", a=(59.75, 64.30), vsrc="w", v=44.8, keys=K(44.8), why="x3 = 1/3 rule."),
    dict(id="answer", a=(64.55, 66.45), vsrc="w", v=49.6, keys=K(49.6), why="'Itulah gaji yang layaknya' -> RM11,100."),
    dict(id="lengkap", a=(9.15, 10.95), vsrc="w", v=27.6, keys=K(27.6, 1.1), why="'Memang cukup lengkap' over the side profile."),
    dict(id="brown", a=(11.10, 12.62), vsrc="b57", v=0.4, keys=K(0.4, 1.05, (0.5, 0.5), 1.15), why="Brown interior = captain seats B-roll."),
    dict(id="sunroof", a=(12.64, 13.95), vsrc="w", v=36.2, keys=K(36.2, 1.1, (0.5, 0.35)), why="Sunroof = cabin ceiling."),
    dict(id="sidestep", a=(13.98, 15.62), vsrc="b59", v=0.0, keys=K(0.0, 1.05), why="Side step B-roll."),
    dict(id="sidestep2", a=(15.62, 15.92), vsrc="w", v=40.1, keys=K(40.1, 1.08), why="Rest of the word over the walkaround's own side-step shot."),
    dict(id="kemas", a=(15.95, 19.00), vsrc="w", v=41.4, keys=K(41.4, 1.08), why="'Dalaman yang kemas' over the front seats/dash."),
    dict(id="cta", a=(66.60, 69.60), vsrc="b55", v=0.0, keys=K(0.0, 1.05, (0.5, 0.55), 1.12), why="CTA over the rear with tailgate open."),
]

GRAPHICS = []
KEYPOINTS = []

GLASS = [
    dict(win=(27.30, 37.40), items=[
        dict(kind="card", title="Kos on the road", rows=[(30.12, "Harga body", "RM326,000"),
                                                       (35.76, "Insurans · NCD 55%", "RM4,500")]),
    ]),
    dict(win=(45.65, 49.86), items=[
        dict(kind="label", text="Jumlah"),
        dict(kind="counter", at=47.96, to=334040, frm=0, dur=1.2, lab="On the road", sub="326,000 + 4,500 + 740 + 2,800", accent=True),
    ]),
    dict(win=(49.90, 58.95), items=[
        dict(kind="card", title="Kira loan", rows=[(52.10, "Tempoh loan", "9 tahun"),
                                                   (53.22, "Down payment", "Tiada (full loan)"),
                                                   (55.68, "Bulanan (anggaran)", "± RM3,700+")]),
    ]),
    dict(win=(59.75, 64.28), items=[
        dict(kind="label", text="Rule 1/3 gaji"),
        dict(kind="cards", items=[(61.58, "01 · Rule", "Ansuran = 1/3 gaji"),
                                  (62.82, "02 · Kira", "RM3,700 × 3"),
                                  (63.58, "03 · Hasil", "RM11,100 sebulan")]),
    ]),
    dict(win=(64.55, 66.43), items=[
        dict(kind="label", text="Jawapan"),
        dict(kind="counter", at=64.60, to=11100, frm=0, dur=1.1, lab="Gaji layak", sub="RM3,700 × 3 = RM11,100 sebulan", accent=True),
    ]),
]

OVERLAYS = [
    dict(kind="counter_pill", at=20.02, dur=5.0, to=334040, frm=0, dur_roll=1.4, lab="Vellfire Z Premier · on the road", sub="Gaji berapa layak?"),
    dict(kind="pill", at=1.72, dur=2.6, text="Vellfire *Z Premier* 2024"),
    dict(kind="pill", at=5.26, dur=1.5, text="Grade *5A*"),
    dict(kind="pill", at=7.10, dur=1.8, text="Mileage *4,000+ km*"),
    dict(kind="title", at=25.46, dur=1.6, chip="JOM KIRA", accent="Gaji layak?"),
    dict(kind="pill", at=38.98, dur=3.2, text="Road tax · enjin 2.4 = *RM740*"),
    dict(kind="pill", at=44.46, dur=1.4, text="Processing fee *RM2,800*"),
    dict(kind="pill", at=10.00, dur=1.4, text="Memang *cukup lengkap*"),
    dict(kind="pill", at=12.14, dur=1.2, text="Dalaman *brown*"),
    dict(kind="pill", at=13.36, dur=1.0, text="*Sunroof*"),
    dict(kind="pill", at=15.18, dur=1.0, text="*Side step*"),
    dict(kind="pill", at=16.54, dur=2.2, text="Dalaman *kemas*"),
    dict(kind="pill", at=68.60, dur=1.4, text="Berminat? Tekan *link*"),
]

MUSIC = dict(file="/home/user/drive_dl/Music/music1.mp4", start=1.6, lufs=-29, duck_db=8, fade_out=1.8)
