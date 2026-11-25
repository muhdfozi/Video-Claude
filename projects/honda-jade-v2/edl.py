"""Honda Jade RS, v2: source = the user's version edited on another platform
(copy_15838EAB....mov, 1080x1920 SDR, persistent burned-in header "HONDA / JADE RS / 2019/2024 / RM85,000").

Rules for this source:
- NO_ZOOM: the header is burned into the pixels, so any crop/zoom would distort it.
- Colour exactly as the file (SDR BT.709, no grade).
- All my graphics sit BELOW the header (header spans ~y 290-750 of 1920).
- Header already shows model/year/price, so no model card, no "Reg 2024" key point, no price card
  (price becomes a key point + cash SFX).
- Audio: identical timing to raw IMG_1265 (lag 0), so the cleaner raw audio is used.
Same cut list as projects/honda-jade/edl.py otherwise. Times are SOURCE seconds.
"""
NO_ZOOM = True
AUDIO = "/home/user/work2/audio48k.wav"
K = [(0, 1.0, 0.5, 0.5)]

SEGMENTS = [
    dict(id="hookA", a=(11.86, 14.95), v=72.55, cut_pauses=False, keys=K,
         why="Best hook: audience call-out 'kereta family tapi tak nak nampak terlalu family man' over the "
             "best angle (rear 3/4 + spoiler) as a flash-forward."),
    dict(id="hookB", a=(14.95, 18.30), keys=K, why="Finish the hook line on the car."),
    dict(id="name", a=(0.00, 3.24), v=0.70, keys=K,
         why="Model + engine. Video offset 0.7 s to skip the header's intro animation (POV, no lip sync)."),
    dict(id="wagon", a=(18.20, 20.10), keys=K, why="Wagon concept."),
    dict(id="rs", a=(21.25, 29.10), keys=K, why="RS 5 seater / variants 6 seater."),
    dict(id="toback", a=(29.08, 32.04), keys=K, why="Into the rear seats."),
    dict(id="interior", a=(32.04, 40.04), keys=K, why="Semi leather, polka dot, colours, kemas."),
    dict(id="price", a=(40.02, 44.05), keys=K, why="Price line (header shows the number)."),
    dict(id="nego", a=(45.02, 50.60), keys=K, why="Direct nego with owner."),
    dict(id="paddle", a=(52.84, 56.62), keys=K, why="Paddle shifter, steering condition."),
    dict(id="mileage", a=(60.30, 64.20), keys=K, why="Auto + original mileage 56,000 km."),
    dict(id="pomen", a=(65.88, 68.56), keys=K, why="Check with any mechanic."),
    dict(id="rear", a=(70.36, 74.10), keys=K, why="Payoff: 'yang best dia belakang'."),
    dict(id="boot", a=(76.10, 81.02), keys=K, why="Hatch opens, big boot."),
    dict(id="cta", a=(81.04, 84.30), keys=K, why="CTA; ends before the header's exit glitch at 84.6 s."),
]

WORD_FIX = {49.32: "nombor"}

Y = 870   # top of my graphics zone, just under the burned-in header
GRAPHICS = [
    dict(kind="hooktext", at=11.86, dur=2.9, sfx="pop", y=Y + 10,
         lines=[("KERETA FAMILY", 96, False), ("TAPI TAK NAMPAK", 78, False), ("FAMILY MAN", 140, True)]),
    dict(kind="sfx", at=14.95, sfx="whoosh"),
    dict(kind="spec", at=1.38, dur=1.9, rows=[("ENJIN", "1.5 TURBO")], y0=Y, sfx="pop"),
    dict(kind="chip", at=29.08, dur=1.6, text="INTERIOR", y=Y, sfx="whoosh"),
    dict(kind="sfx", at=41.92, sfx="cash"),
    dict(kind="spec", at=60.32, dur=3.6, rows=[("GEARBOX", "AUTO")], y0=Y, sfx="pop"),
    dict(kind="spec", at=60.90, dur=3.0, rows=[("MILEAGE", "56,000 KM")], y0=Y, slot=1, sfx=None),
    dict(kind="chip", at=70.36, dur=1.8, text="BAHAGIAN BELAKANG", y=Y, sfx="riser_in"),
    dict(kind="sfx", at=77.4, sfx="whoosh"),
    dict(kind="cta", at=81.04, dur=99, text="TEKAN LINK UNTUK INFO", y=1110, sfx=None),
]

KEYPOINTS = [
    (18.96, 1.2, "Konsep *wagon*"),
    (24.30, 1.5, "RS = *5 seater*"),
    (27.80, 1.3, "Varian lain *6 seater*"),
    (32.76, 2.6, "*Semi leather* · corak polkadot"),
    (35.48, 2.5, "Ada warna *merah* & orange"),
    (38.90, 1.2, "Interior *sangat kemas*"),
    (41.92, 2.2, "Harga owner *RM85,000*"),
    (46.58, 2.2, "Nego *terus* dengan owner"),
    (53.70, 1.0, "*Paddle shifter*"),
    (54.40, 2.2, "Steering *masih kemas*"),
    (66.10, 2.4, "Check dengan *mana-mana pomen*"),
    (71.80, 1.9, "*Cantik* · design wagon"),
    (79.02, 1.8, "Bonet belakang *luas*"),
]

MUSIC = dict(file="/home/user/drive_dl/Music/music1.mp4", start=887.86, lufs=-27, duck_db=7, fade_out=1.8)
