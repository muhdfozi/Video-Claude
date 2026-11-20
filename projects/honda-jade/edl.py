"""Paper edit: Honda Jade RS 1.5 VTEC Turbo walkaround (raw: IMG_1265.MOV, 1:25 POV take, 4K HLG 60 fps).

Style: TikTok Edit Style v1.0 (keypoint stickers, no running subtitles, original HDR colour).
All times are SOURCE seconds. See projects/honda-prelude/edl.py for field docs.
POV footage (no face): zoom targets are the car / hands / details.
"""

CAR_FAR = (0.38, 0.51)   # car in the background of the opening hand-talk shot (0-24 s)

SEGMENTS = [
    dict(id="hookA", a=(11.86, 14.95), v=72.55, cut_pauses=False,
         keys=[(72.55, 1.12, 0.50, 0.56), (75.6, 1.28, 0.50, 0.60)],
         why="Flash-forward to the best angle (rear 3/4 + spoiler) under the audience call-out "
             "'kereta family tapi tak nak nampak terlalu family man'."),
    dict(id="hookB", a=(14.95, 18.30),
         keys=[(14.95, 2.0, *CAR_FAR), (18.3, 2.2, *CAR_FAR)],
         why="Finish the hook line on the car itself (punched in from the wide hand-talk shot)."),
    dict(id="name", a=(0.00, 3.24),
         keys=[(0.0, 1.8, *CAR_FAR), (1.38, 2.15, *CAR_FAR, "cut")],
         why="Model + engine straight after the hook. Spec cards carry the words."),
    dict(id="reg", a=(5.16, 9.48), keys=[(5.16, 1.9, *CAR_FAR), (9.48, 2.1, *CAR_FAR)],
         why="Reg 2024 / year 2019. Dropped the unclear 'second hand used' line before it."),
    dict(id="wagon", a=(18.20, 20.10), keys=[(18.2, 2.0, *CAR_FAR)],
         why="Wagon concept = the reason it doesn't look like a 'family man' car."),
    dict(id="rs", a=(21.25, 29.10), keys=[(21.25, 1.0, 0.5, 0.5)],
         why="RS = 5 seater, other variants 6 seater. Dropped 'Dan untuk' lead-in."),
    dict(id="toback", a=(29.08, 32.04), keys=[(29.08, 1.0, 0.5, 0.5)],
         why="Door opens into the rear seats (section change)."),
    dict(id="interior", a=(32.04, 40.04),
         keys=[(32.04, 1.0, 0.5, 0.5), (33.6, 1.30, 0.50, 0.60, "cut"), (38.1, 1.0, 0.5, 0.5, "cut")],
         why="Semi-leather + polka-dot fabric: crop in on the seat while his hand shows it."),
    dict(id="price", a=(40.02, 44.05), keys=[(40.02, 1.0, 0.5, 0.5), (44.05, 1.12, 0.5, 0.5)],
         why="Price = biggest info moment."),
    dict(id="nego", a=(45.02, 50.60), keys=[(45.02, 1.0, 0.5, 0.5)],
         why="Direct nego with owner + owner's number = strong selling point."),
    dict(id="paddle", a=(52.84, 56.62),
         keys=[(52.84, 1.0, 0.5, 0.5), (53.65, 1.35, 0.50, 0.58, "cut"), (54.3, 1.0, 0.5, 0.5, "cut")],
         why="Paddle shifter + steering condition. Dropped hanging 'tak ada pun'."),
    dict(id="mileage", a=(60.30, 64.20),
         keys=[(60.30, 1.0, 0.5, 0.5), (60.9, 1.45, 0.60, 0.56, "cut")],
         why="Auto + original mileage 56,000 km: crop to the meter area. Dropped 'saya akan hantar detail'."),
    dict(id="pomen", a=(65.88, 68.56), keys=[(65.88, 1.0, 0.5, 0.5)],
         why="Confidence: check with any mechanic. Dropped the unclear first phrase."),
    dict(id="rear", a=(70.36, 74.10), keys=[(70.36, 1.0, 0.5, 0.5), (74.1, 1.15, 0.5, 0.58)],
         why="Payoff: 'yang best dia belakang'. Riser + slow push."),
    dict(id="boot", a=(76.10, 81.02), keys=[(76.1, 1.0, 0.5, 0.5)],
         why="Hatch opens: wagon = big boot. Kept continuous so the reveal plays."),
    dict(id="cta", a=(81.04, 84.30), keys=[(81.04, 1.0, 0.5, 0.5), (84.3, 1.08, 0.5, 0.55)],
         why="CTA over him walking away: full rear of the car, loops back to the hook angle."),
]

WORD_FIX = {49.32: "nombor"}

# Big elements (same look the user approved on the Prelude edit)
GRAPHICS = [
    dict(kind="hooktext", at=11.86, dur=2.9, sfx="pop",
         lines=[("KERETA FAMILY", 104, False), ("TAPI TAK NAMPAK", 84, False), ("FAMILY MAN", 150, True)],
         why="Text hook = the call-out, readable with sound off."),
    dict(kind="sfx", at=14.95, sfx="whoosh", why="Cut from B-roll to the car."),
    dict(kind="spec", at=0.42, dur=2.9, rows=[("HONDA", "JADE RS")], sfx="pop", why="Model name."),
    dict(kind="spec", at=1.38, dur=1.9, rows=[("ENJIN", "1.5 TURBO")], slot=1, sfx=None, why="Engine."),
    dict(kind="chip", at=29.08, dur=1.6, text="INTERIOR", sfx="whoosh", why="Section change."),
    dict(kind="price", at=41.92, dur=2.6, text="RM85,000", sub="HARGA OWNER", sfx="cash", why="Price."),
    dict(kind="spec", at=60.32, dur=3.6, rows=[("GEARBOX", "AUTO")], sfx="pop", why="Spec number on screen."),
    dict(kind="spec", at=60.90, dur=3.0, rows=[("MILEAGE", "56,000 KM")], slot=1, sfx=None, why="Original mileage."),
    dict(kind="chip", at=70.36, dur=1.8, text="BAHAGIAN BELAKANG", sfx="riser_in", why="Payoff section."),
    dict(kind="sfx", at=77.4, sfx="whoosh", why="Hatch swinging up."),
    dict(kind="cta", at=81.04, dur=99, text="TEKAN LINK UNTUK INFO", sfx=None, why="His own CTA as a button."),
]

# Key-point stickers only (no running subtitles) [user rule]
KEYPOINTS = [
    (5.16, 4.0, "Reg *2024* · kereta tahun 2019"),
    (18.96, 1.2, "Konsep *wagon*"),
    (24.30, 1.5, "RS = *5 seater*"),
    (27.80, 1.3, "Varian lain *6 seater*"),
    (32.76, 2.6, "*Semi leather* · corak polkadot"),
    (35.48, 2.5, "Ada warna *merah* & orange"),
    (38.90, 1.2, "Interior *sangat kemas*"),
    (46.58, 2.2, "Nego *terus* dengan owner"),
    (53.70, 1.0, "*Paddle shifter*"),
    (54.40, 2.2, "Steering *masih kemas*"),
    (66.10, 2.4, "Check dengan *mana-mana pomen*"),
    (71.80, 1.9, "*Cantik* · design wagon"),
    (79.02, 1.8, "Bonet belakang *luas*"),
]

MUSIC = dict(file="/home/user/drive_dl/Music/music1.mp4", start=887.86, lufs=-27, duck_db=7, fade_out=1.8)
