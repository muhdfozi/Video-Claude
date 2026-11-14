"""Paper edit for the Honda Prelude 2025 walkaround (raw: IMG_1031.MOV, one 2:21 take).

All times are SOURCE seconds. Each segment keeps audio a=(in, out); video comes from the same
time unless `v` is given (B-roll / flash-forward). `keys` are zoom keyframes in SOURCE video time:
(t, scale, cx, cy[, ease]) where cx/cy are the crop centre (0..1 of the source frame) and
ease is "cut" (hard change at t) or "smooth" (eased from previous key, default).
`cut_pauses`: automatically remove internal silences > 0.3 s (jump cuts).
Every entry carries a `why` so each edit decision is explicit.
"""

F0 = (0.32, 0.49)     # presenter face, front of car, 0-27 s
F1 = (0.22, 0.46)     # 29-45 s
F_RIM = (0.38, 0.38)  # 56-58 s
F_DOOR = (0.31, 0.40)
F_IN = (0.27, 0.36)   # inside car
F_RE = (0.21, 0.44)   # rear of car

SEGMENTS = [
    dict(id="hook", a=(0.00, 2.95), v=104.05, cut_pauses=False,
         keys=[(104.05, 1.30, 0.64, 0.60), (107.0, 1.45, 0.64, 0.58)],
         why="Flash-forward: strongest visual (rear hatch + glass lifting) under the strongest line "
             "'First in Malaysia'. Visual + verbal + text hook in frame 1."),
    dict(id="intro", a=(2.95, 7.75),
         keys=[(2.95, 1.15, *F0), (5.78, 1.0, 0.5, 0.5, "cut")],
         why="Finish the hook sentence on camera (black interior), then a quick salam + name so the "
             "seller is trusted. Zoom change at the salam = visual beat."),
    dict(id="rare", a=(12.55, 15.95),
         keys=[(12.55, 1.20, *F0), (13.90, 1.38, *F0, "cut")],
         why="Scarcity claim. Dropped 'Hari ni kita ada...Hybrid' (repeats hook). Punch on 'sangat-sangat jarang'."),
    dict(id="price", a=(17.00, 19.85),
         keys=[(17.0, 1.0, 0.5, 0.5), (19.85, 1.10, *F0)],
         why="Price early = qualifies viewers fast. Dropped 'So yang ini' lead-in."),
    dict(id="coupe", a=(20.02, 23.65), keys=[(20.0, 1.15, *F0)],
         why="Key spec list, tight."),
    dict(id="recon", a=(23.80, 27.58),
         keys=[(23.8, 1.0, 0.5, 0.5), (25.50, 1.22, *F0, "cut")],
         why="New model but recon import: important buying context. Punch on 'Tapi'."),
    dict(id="hybrid", a=(29.45, 34.62),
         keys=[(29.45, 1.10, *F1), (32.60, 1.0, 0.5, 0.5, "cut")],
         why="Engine on/off because hybrid. Dropped 'kalau korang boleh dengar sedikit' (can't hear it on phone)."),
    dict(id="power", a=(34.95, 41.30),
         keys=[(34.95, 1.0, 0.5, 0.5), (37.2, 1.12, *F1, "cut")],
         why="Power figures (presenter's own hedge kept in subtitles). Cut the '200 lebih, 300 lebih' "
             "sum: motor + engine PS do not add up that way, so leaving it would mislead buyers."),
    dict(id="rim1", a=(45.12, 47.85), keys=[(45.0, 1.12, 0.50, 0.58), (47.85, 1.22, 0.55, 0.62)],
         why="Section change to wheels."),
    dict(id="caliper", a=(49.40, 52.40), keys=[(48.78, 1.85, 0.62, 0.74), (52.4, 2.0, 0.64, 0.74)],
         why="Detail cutaway from 4K: blue caliper with Prelude script. Free B-roll."),
    dict(id="sportrim", a=(52.44, 53.46), keys=[(52.44, 1.5, 0.62, 0.72)],
         why="Rim detail. Dropped hesitation 'full,'."),
    dict(id="gloss", a=(54.30, 55.66), keys=[(54.30, 1.0, 0.5, 0.5)],
         why="Wide shot to show the whole gloss-black wheel against white body."),
    dict(id="rimsize", a=(56.04, 58.40), keys=[(56.04, 1.18, *F_RIM)],
         why="Rim size (hedge kept)."),
    dict(id="door", a=(59.12, 64.92),
         keys=[(59.12, 1.0, 0.5, 0.5), (61.0, 1.65, 0.48, 0.70, "cut"), (63.25, 1.0, 0.5, 0.5, "cut")],
         why="'Paling menarik': zoom into the flush door handle while he names it, back to wide as the door opens."),
    dict(id="seats", a=(64.88, 67.52), keys=[(64.88, 1.12, *F_DOOR)],
         why="Section change to interior. Dropped 'tapi yang selesa...kereta 2 pintu' + repeat."),
    dict(id="front2", a=(74.43, 78.45),
         keys=[(74.43, 1.0, 0.5, 0.5), (77.85, 1.28, *F_IN, "cut")],
         why="Jump-cut straight to him seated (skips 4 s of climbing in). Honest con: rear seats not comfy."),
    dict(id="splus", a=(78.48, 81.24), keys=[(78.48, 1.30, 0.55, 0.52)],
         why="Gearbox S+ - framed on the console."),
    dict(id="paddle", a=(84.70, 88.18),
         keys=[(84.7, 1.0, 0.5, 0.5), (87.30, 1.65, 0.74, 0.47, "cut")],
         why="Dropped 'dekat sini yang dimana ini adalah sistem hybrid so' (already said). Zoom to wheel on 'paddle shifter'."),
    dict(id="meter", a=(88.56, 90.30), keys=[(88.56, 1.75, 0.72, 0.42)],
         why="Digital meter detail. Dropped stutter 'meter meter'."),
    dict(id="frameless", a=(93.86, 98.02), keys=[(93.86, 1.0, 0.5, 0.5)],
         why="Honest con (no frameless doors) builds trust before the payoff."),
    dict(id="sexy", a=(98.04, 101.42), keys=[(98.04, 1.0, 0.5, 0.5), (101.42, 1.15, 0.62, 0.50)],
         why="Pays off the open loop from the hook. Riser leads in, slow push builds anticipation."),
    dict(id="hatch", a=(103.10, 109.80), cut_pauses=False,
         keys=[(103.10, 1.0, 0.5, 0.5), (104.0, 1.0, 0.55, 0.55), (107.2, 1.22, 0.60, 0.56)],
         why="The money shot - kept continuous so the hatch+glass lift plays in full, in sync."),
    dict(id="fl5", a=(109.82, 115.18), keys=[(109.82, 1.15, *F_RE)],
         why="Car-nerd fact (hedge kept). Dropped the 5 s 'sebab Civic FL5...' repeat."),
    dict(id="boot", a=(120.30, 124.50), keys=[(120.3, 1.45, 0.64, 0.60), (124.5, 1.55, 0.66, 0.60)],
         why="Practicality: boot space + folding seats. Framed on the boot."),
    dict(id="oops", a=(124.50, 127.25),
         keys=[(124.50, 1.0, 0.5, 0.5), (126.10, 1.60, *F_RE, "cut")],
         why="Real blooper 'Honda Civic... sorry' kept as the comedic beat (punch-in + scratch)."),
    dict(id="cta", a=(127.30, 135.42),
         keys=[(127.30, 1.0, 0.5, 0.5), (132.10, 1.22, *F_RE, "cut")],
         why="Corrected line + price again + 'belum on the road' = the CTA."),
    dict(id="tail", a=(135.50, 139.55),
         keys=[(135.36, 1.40, 0.60, 0.66), (138.0, 1.50, 0.62, 0.66), (138.08, 1.25, 0.30, 0.45, "cut")],
         why="End on the full-width taillight + 'cantik gila' reaction; loops back to the rear-hatch hook."),
]

# Subtitle text fixes (word-level, matched by source start time of the word, +-0.05 s)
WORD_FIX = {
    48.28: "Prelude", 49.84: "Prelude-nya", 100.76: "Prelude", 80.28: "S+", 81.00: "",
    87.36: "paddle", 65.46: "dalamannya", 65.72: "", 124.74: "andai", 128.20: "andai",
    135.02: "on the", 135.20: "road", 82.06: "di mana",
}
TOKEN_FIX = {"bagian": "bahagian"}

# Words to colour as keyword (upper-case compare, punctuation stripped)
KEYWORDS = {"MALAYSIA", "PRELUDE", "2025", "HITAM", "FAUZI", "JARANG", "RM250,000", "RENDAH", "COUPE",
            "BARU", "RECON", "IMPORTED", "HYBRID", "MATI", "HIDUP", "181", "141", "CANTIK", "CALIPER", "BIRU",
            "GLOSS", "BLACK", "19-20", "MEWAH", "4", "TAK", "S+", "PADDLE", "DIGITAL", "FRAMELESS",
            "KEKURANGAN", "SEKSI", "TERANGKAT", "CERMIN", "FL5", "CIVIC", "DITURUNKAN", "SORRY", "ROAD",
            "BERCANTUM", "GILA", "DOOR", "HANDLE", "RUANGAN", "SPORT"}

# Graphics & SFX anchored to SOURCE word times (resolved onto the output timeline).
# kind: hooktext, name, price, spec, chip, oops, cta ; sfx: whoosh, pop, cash, riser, scratch, ding
GRAPHICS = [
    dict(kind="hooktext", at=0.00, dur=2.6, lines=["FIRST IN", "MALAYSIA"], sfx="pop",
         why="Text hook readable with sound off."),
    dict(kind="sfx", at=2.95, sfx="whoosh", why="Cut from B-roll hook back to presenter."),
    dict(kind="name", at=6.86, dur=1.9, text="FAUZI", sfx="pop", why="Who is talking -> trust."),
    dict(kind="price", at=17.98, dur=2.2, text="RM250,000", sub="SAHAJA", sfx="cash",
         why="Biggest info moment, must be impossible to miss."),
    dict(kind="spec", at=33.42, dur=1.6, rows=[("2.0", "HYBRID")], sfx="pop", why="Restores the dropped '2.0 Hybrid' info visually."),
    dict(kind="spec", at=37.26, dur=4.0, rows=[("MOTOR", "181 PS")], sfx="pop", why="Numbers are easier read than heard."),
    dict(kind="spec", at=39.58, dur=1.6, rows=[("ENJIN", "141 PS")], slot=1, sfx=None, why="Second row."),
    dict(kind="chip", at=45.00, dur=1.6, text="EKSTERIOR", sfx="whoosh", why="Section change (progress cue)."),
    dict(kind="spec", at=57.34, dur=1.3, rows=[("RIM", "19-20\"")], sfx="pop", why="Number on screen."),
    dict(kind="chip", at=64.88, dur=1.6, text="INTERIOR", sfx="whoosh", why="Section change."),
    dict(kind="chip", at=98.04, dur=1.8, text="BAHAGIAN BELAKANG", sfx="riser_in", why="Payoff section; riser builds into it."),
    dict(kind="sfx", at=104.05, sfx="whoosh", why="Hatch rising - sound sells the motion."),
    dict(kind="oops", at=126.12, dur=1.1, text="EH? CIVIC??", sfx="scratch", why="Comedic beat on the real slip."),
    dict(kind="price", at=132.16, dur=3.2, text="RM250,000", sub="BELUM ON THE ROAD", sfx="cash",
         why="CTA price repeat with the on-the-road caveat."),
    dict(kind="cta", at=135.40, dur=99, text="DM UNTUK INFO LANJUT", sfx=None, why="Clear next action until the end."),
]
