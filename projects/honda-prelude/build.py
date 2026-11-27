"""Build the TikTok edit from edl.py.

usage:
  python3 build.py preview  --src mezz.mov  --audio audio48k.wav --words transcript.json --sfx sfxdir --out preview.mp4
  python3 build.py final    --src IMG_1031.MOV --audio audio48k.wav --words transcript.json --sfx sfxdir --out final.mp4

preview: 720x1280 30 fps from the SDR working copy.  final: 1080x1920 at source fps from the 4K original.
"""
import argparse, json, math, os, subprocess, sys, wave
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
_edl_path = sys.argv[sys.argv.index("--edl") + 1] if "--edl" in sys.argv else os.path.join(os.path.dirname(os.path.abspath(__file__)), "edl.py")
_spec = importlib.util.spec_from_file_location("edl", _edl_path); edl = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(edl)
SEGMENTS, GRAPHICS, KEYPOINTS = edl.SEGMENTS, edl.GRAPHICS, getattr(edl, "KEYPOINTS", [])
WORD_FIX, TOKEN_FIX, KEYWORDS = getattr(edl, "WORD_FIX", {}), getattr(edl, "TOKEN_FIX", {}), getattr(edl, "KEYWORDS", set())
MUSIC = getattr(edl, "MUSIC", None)
SOURCES = getattr(edl, "SOURCES", {})        # multi-clip edits: segment "vsrc" picks a file (default = --src)
AMBIENT = getattr(edl, "AMBIENT", None)      # dict(file=..., lufs=-34): real location sound under a separate voiceover
VOICE = getattr(edl, "VOICE", "")            # "studio": AI-cleaned source (AUDIO) + broadcast mic chain below
# "High-end mic in a studio": the noise is already removed by enhance_voice.py (DeepFilterNet3); this chain gives the
# tonal signature of a large-diaphragm condenser + broadcast processing: rumble cut, gentle warmth, de-box,
# presence and air, de-essing, two-stage compression (smooth leveller + fast peak control), loudness.
# "Recorded on location": voiceover from a quiet room made to sit in the footage — light cleanup, phone-mic-like
# tone (no hyped air), short early reflections of a covered car park / showroom, gentle compression.
LOCATION_CHAIN = ("highpass=f=85:poles=2,"
                  "equalizer=f=200:t=q:w=1.0:g=-1.5,"
                  "equalizer=f=3000:t=q:w=1.4:g=1.5,"
                  "lowpass=f=13500,"
                  "aecho=0.85:0.55:19|34|51:0.11|0.075|0.045,"
                  "deesser=i=0.35:m=0.5:f=0.5,"
                  "acompressor=threshold=0.125:ratio=2.5:attack=15:release=200:knee=4:makeup=1.3,"
                  "loudnorm=I=-15:TP=-2:LRA=8")
STUDIO_CHAIN = ("highpass=f=75:poles=2,"
                "equalizer=f=110:t=q:w=0.9:g=2.0,"          # chest / proximity warmth
                "equalizer=f=320:t=q:w=1.1:g=-3.0,"         # remove boxiness (car park / phone mic)
                "equalizer=f=900:t=q:w=1.4:g=-1.0,"         # tame honk
                "equalizer=f=4200:t=q:w=1.2:g=2.5,"         # presence / intelligibility
                "treble=g=2.5:f=11000:width_type=q:width=0.7,"  # air
                "deesser=i=0.45:m=0.5:f=0.5,"
                "acompressor=threshold=0.125:ratio=2.5:attack=20:release=250:knee=4:makeup=1.4,"
                "acompressor=threshold=0.35:ratio=6:attack=2:release=60:makeup=1.0,"
                "loudnorm=I=-15:TP=-2:LRA=7")
THEME = getattr(edl, "THEME", "clean")      # "clean" (Prelude look) or "paper" (collage look)
NO_ZOOM = getattr(edl, "NO_ZOOM", False)   # source has burned-in graphics: never crop/zoom
LAYOUT = getattr(edl, "LAYOUT", None)       # dict(kind="inset", box=(x,y,w,h) in 1080x1920, border=16): video as a photo on paper
AUDIO_SRC = getattr(edl, "AUDIO", None)    # optional cleaner audio file with identical timing     # dict(file=..., start=sec, lufs=-27, duck_db=6)

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
GRID = 60.0                      # timeline grid = source frame rate

ap = argparse.ArgumentParser()
ap.add_argument("mode", choices=["preview", "final", "plan"])
ap.add_argument("--src", required=True)
ap.add_argument("--audio", required=True)
ap.add_argument("--words", required=True)
ap.add_argument("--sfx", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--work", default=".")
ap.add_argument("--edl", default=None)
ap.add_argument("--hdr", action="store_true", help="final: keep original HLG/BT.2020 10-bit colour (no conversion)")
ap.add_argument("--keypoints", action="store_true", help="key-point stickers instead of running subtitles")
ap.add_argument("--limit", type=float, default=0, help="render only the first N seconds (test)")
args = ap.parse_args()

if args.mode == "final":
    _cs = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_space",
                          "-of", "csv=p=0", args.src], capture_output=True, text=True).stdout.strip()
    _fr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                          "-of", "csv=p=0", args.src], capture_output=True, text=True).stdout.strip()
    _n, _d = (_fr.split(",")[0].split("\n")[0].split("/") + ["1"])[:2]
    OW, OH, FPS, SRC_MATRIX = 1080, 1920, round(float(_n) / float(_d)), ("bt2020" if "2020" in _cs else "bt709")   # fps follows source
else:
    _cs = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_space",
                          "-of", "csv=p=0", args.src], capture_output=True, text=True).stdout.strip()
    OW, OH, FPS, SRC_MATRIX = 720, 1280, 30, ("bt2020" if "2020" in _cs else "bt709")

q = lambda t: round(t * GRID) / GRID          # quantise to source frame grid

# ---------------------------------------------------------------- audio + voice activity
def read_wav(p):
    with wave.open(p) as w:
        assert w.getframerate() == SR
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, w.getnchannels())
    return x.astype(np.float32) / 32768

voice_src = read_wav(AUDIO_SRC or args.audio)
mono = voice_src.mean(1)
HOP = 480                                           # 10 ms
nfr = len(mono) // HOP
rms_db = 20 * np.log10(np.sqrt((mono[:nfr * HOP].reshape(nfr, HOP) ** 2).mean(1)) + 1e-9)
THR = getattr(edl, "VAD_DB", None) or max(np.percentile(rms_db, 15) + 9, -46)   # EDL can override (boosted audio)
voiced = rms_db > THR
# close tiny holes (< 60 ms) inside words
for i in range(1, nfr - 6):
    if not voiced[i] and voiced[i - 1]:
        j = i
        while j < nfr and not voiced[j] and j - i < 6: j += 1
        if j < nfr and voiced[j] and j - i < 6: voiced[i:j] = True

def vidx(t): return int(t * 100)

# ---------------------------------------------------------------- build sub-segments
subs = []           # dicts: seg, a0, a1, v0, punch
for si, seg in enumerate(SEGMENTS):
    a0, a1 = seg["a"]
    contig_prev = si > 0 and abs(SEGMENTS[si - 1]["a"][1] - a0) < 1e-6
    contig_next = si + 1 < len(SEGMENTS) and abs(SEGMENTS[si + 1]["a"][0] - a1) < 1e-6
    # tighten to speech
    # voiced runs inside the segment
    runs, i, e = [], vidx(a0), vidx(a1)
    while i < e:
        if voiced[i]:
            j = i
            while j < e and voiced[j]: j += 1
            runs.append((i, j)); i = j
        else:
            i += 1
    if runs:
        if not contig_prev: a0 = max(a0, runs[0][0] / 100 - 0.06)
        if not contig_next: a1 = min(a1, runs[-1][1] / 100 + 0.12)
    # internal pauses -> jump cuts (each kept piece >= 0.35 s)
    pieces = [(a0, a1)]
    if seg.get("cut_pauses", True):
        pieces, cur = [], a0
        for (r0, r1), (n0, n1) in zip(runs, runs[1:]):
            gap0, gap1 = r1 / 100, n0 / 100
            if gap1 - gap0 >= 0.28 and gap0 + 0.07 - cur >= 0.35 and a1 - (gap1 - 0.07) >= 0.35:
                pieces.append((cur, gap0 + 0.07)); cur = gap1 - 0.07
        pieces.append((cur, a1))
    for k, (p0, p1) in enumerate(pieces):
        p0, p1 = q(p0), q(p1)
        if p1 - p0 < 2 / GRID: continue
        v0 = seg.get("v", seg["a"][0]) + (p0 - seg["a"][0])
        subs.append(dict(seg=seg, si=si, a0=p0, a1=p1, v0=q(v0), punch=(k % 2 == 1)))

t = 0.0
for s in subs:
    s["o0"] = t; s["dur"] = s["a1"] - s["a0"]; t = q(t + s["dur"]); s["o1"] = t
TOTAL = t

def src2out(ts, prefer_next=True):
    for s in subs:
        if s["a0"] - 1e-6 <= ts < s["a1"]: return s["o0"] + ts - s["a0"]
    if prefer_next:                      # anchor fell in a removed gap: snap to the nearest later kept piece
        later = [s for s in subs if s["a0"] >= ts]
        if later: return min(later, key=lambda s: s["a0"])["o0"]
    return None

# ---------------------------------------------------------------- zoom curve
def ease(x): return x * x * (3 - 2 * x)

def zoom_at(seg, tv, punch):
    if NO_ZOOM: return 1.0, 0.5, 0.5
    keys = seg["keys"]
    k = keys[0]
    if tv <= keys[0][0]:
        s, cx, cy = k[1], k[2], k[3]
    else:
        s, cx, cy = keys[-1][1:4]
        for a, b in zip(keys, keys[1:]):
            if a[0] <= tv < b[0]:
                if len(b) > 4 and b[4] == "cut":
                    s, cx, cy = a[1:4]
                else:
                    x = ease((tv - a[0]) / (b[0] - a[0]))
                    s, cx, cy = [a[i] + (b[i] - a[i]) * x for i in (1, 2, 3)]
                break
    if punch and s < 1.5:            # alternate punch-in on automatic jump cuts
        s *= 1.10
    return s, cx, cy

# ---------------------------------------------------------------- report plan
plan = []
for s in subs:
    plan.append(f'{s["o0"]:7.2f}-{s["o1"]:7.2f}  src {s["a0"]:7.2f}-{s["a1"]:7.2f}'
                f'{" (video " + format(s["v0"], ".2f") + ")" if abs(s["v0"] - s["a0"]) > 0.01 else ""}'
                f'  [{s["seg"]["id"]}]{" punch" if s["punch"] else ""}')
open(os.path.join(args.work, "plan.txt"), "w").write("\n".join(plan) + f"\nTOTAL {TOTAL:.2f}s\n")
print("\n".join(plan)); print(f"TOTAL {TOTAL:.2f} s, threshold {THR:.1f} dB")

# ---------------------------------------------------------------- words -> subtitles
raw = json.load(open(args.words))
words = []
for sg in raw["segments"]:
    for w in sg["words"]:
        txt = w["word"].strip()
        for k, v in WORD_FIX.items():
            if abs(w["start"] - k) < 0.05: txt = v
        if not txt: continue
        words.append([w["start"], w["end"], txt])
merged = []
for w in words:
    if merged and w[2][0] in "-,." and not w[2][:2].isalpha():
        m = merged[-1]
        if w[2].startswith("-") and w[2][1:].lower() == m[2].lower().strip(",."):
            m[2] = m[2] + w[2]                     # sangat-sangat
        else:
            m[2] = m[2] + w[2]
        m[1] = w[1]
    else:
        merged.append(list(w))
for m in merged:
    for a, b in TOKEN_FIX.items():
        if m[2].lower().strip(",.") == a: m[2] = m[2].lower().replace(a, b)

kept = []
for st, en, txt in merged:
    # assign the word to the kept piece it overlaps most (whisper word edges are loose)
    best, bo = None, 0.0
    for s in subs:
        ov = min(en, s["a1"]) - max(st, s["a0"])
        if ov > bo: best, bo = s, ov
    if best is None or bo < min(0.10, 0.5 * (en - st)): continue
    s = best
    o0 = s["o0"] + max(st, s["a0"]) - s["a0"]
    o1 = s["o0"] + min(en, s["a1"]) - s["a0"]
    if kept and o0 < kept[-1]["o0"]: continue
    kept.append(dict(o0=o0, o1=o1, text=txt, si=s["si"]))

def norm(x): return x.upper().strip(",.?!")

chunks, cur = [], []
for w in kept:
    if cur:
        chars = sum(len(norm(c["text"])) for c in cur) + len(norm(w["text"]))
        prev = cur[-1]
        if (len(cur) >= 3 or chars > 17 or prev["text"][-1] in ",.?!" or prev["si"] != w["si"]
                or w["o0"] - prev["o1"] > 0.45):
            chunks.append(cur); cur = []
    cur.append(w)
if cur: chunks.append(cur)

# ---------------------------------------------------------------- beat grid (THEME "rentak": speed rule)
BEATS = []
RENTAK = getattr(edl, "RENTAK", None)
if RENTAK and THEME in ("rentak", "showroom"):   # speed rule: beat grid (poji hebat, poji padu)
    BPM = RENTAK.get("bpm", 110); beat = 60.0 / BPM
    cuts = [s["o0"] for s in subs]
    def _hits(ph):
        return sum(1 for c in cuts if min((c - ph) % beat, beat - (c - ph) % beat) < 0.06)
    phase = max(np.arange(0, beat, 0.005), key=_hits)
    BEATS = [float(x) for x in np.arange(phase, TOTAL + beat, beat)]
    if MUSIC:
        import librosa
        _tw = os.path.join(args.work, "_music_tempo.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(MUSIC["start"]), "-t", "120", "-i", MUSIC["file"], "-vn",
                        "-ac", "1", "-ar", "22050", _tw], check=True)
        _y, _sr = librosa.load(_tw, sr=22050)
        _tempo, _bf = librosa.beat.beat_track(y=_y, sr=_sr)
        _t = float(np.atleast_1d(_tempo)[0])
        while _t < BPM * 0.75: _t *= 2
        while _t > BPM * 1.5: _t /= 2
        at = BPM / _t
        _bt = librosa.frames_to_time(_bf, sr=_sr)
        b0 = float(_bt[0]) if len(_bt) else 0.0
        # trim the music start so its (stretched) beats land on our phase
        x = (b0 - at * phase) % (beat * at)
        MUSIC["start"] = MUSIC["start"] + x
        MUSIC["atempo"] = at
        print(f"rentak: {BPM} bpm grid, phase {phase:.3f}s ({_hits(phase)}/{len(cuts)} cuts on beat), music {_t:.1f}->{BPM} bpm (atempo {at:.3f})")

# ---------------------------------------------------------------- ASS
GFX_GAIN = 0.80 if args.hdr else 1.0     # HLG: graphics white ~75-80% signal (BT.2408 ref white), not 100%
def C(hexrgb):
    r, g, b = (round(int(hexrgb[i:i + 2], 16) * GFX_GAIN) for i in (0, 2, 4))
    return f"&H00{b:02X}{g:02X}{r:02X}"
YEL, WHT, BLK, BLUE, INK, RED = C("FFD21F"), C("FFFFFF"), C("000000"), C("4F6EF7"), C("15171A"), C("E02020")
FONT = "Montserrat Black"

def ts(x):
    x = max(0, x); h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def rrect(w, h, r):
    return (f"m {r} 0 l {w-r} 0 b {w} 0 {w} 0 {w} {r} l {w} {h-r} b {w} {h} {w} {h} {w-r} {h} "
            f"l {r} {h} b 0 {h} 0 {h} 0 {h-r} l 0 {r} b 0 0 0 0 {r} 0")

ev = []
def add(t0, t1, text, layer=0, style="Sub"):
    ev.append(f"Dialogue: {layer},{ts(t0)},{ts(t1)},{style},,0,0,0,,{text}")

POP = r"\fscx70\fscy70\t(0,90,\fscx108\fscy108)\t(90,160,\fscx100\fscy100)"

for i, c in enumerate([] if args.keypoints else chunks):
    t0 = c[0]["o0"]
    nxt = chunks[i + 1][0]["o0"] if i + 1 < len(chunks) else TOTAL
    t1 = nxt if nxt - c[-1]["o1"] < 0.5 else c[-1]["o1"] + 0.25
    t1 = min(t1, TOTAL)
    hi_done, parts = False, []
    for w in c:
        n = norm(w["text"])
        if not hi_done and n in KEYWORDS:
            parts.append(r"{\c" + YEL + r"&}" + n + r"{\c" + WHT + r"&}"); hi_done = True
        else:
            parts.append(n)
    if t1 <= 1.3: continue
    add(max(t0, 1.3), t1, r"{\an5\pos(540,1300)\fad(0,40)" + POP + "}" + " ".join(parts), layer=5)

sfx_events = []                          # (time_out, name)
for g in (GRAPHICS if THEME == "clean" else []):
    t0 = src2out(g["at"])
    if t0 is None: continue
    d = g.get("dur", 0)
    t1 = min(t0 + d, TOTAL)
    k = g["kind"]
    if g.get("sfx"): sfx_events.append((t0, g["sfx"]))
    if k == "hooktext":
        lines = g["lines"]
        if all(isinstance(x, str) for x in lines):        # legacy: small white line + big yellow line
            lines = [(lines[0], 104, False), (lines[1], 150, True)]
        y = g.get("y", 450) - lines[0][1] / 2 + 52
        for li, (txt, fs, yel) in enumerate(lines):
            y += fs * 0.5
            col = (r"\c" + YEL + "&") if yel else ""
            add(t0 + 0.12 * li, t1, r"{\an5\pos(540," + str(int(y)) + r")\fad(0,120)\frz3\bord" + str(8 if fs < 130 else 10)
                + r"\shad0" + col + POP + r"\fs" + str(fs) + "}" + txt, 8)
            y += fs * 0.55
    elif k == "name":
        w, h = 330, 92
        add(t0, t1, r"{\an5\pos(540,1150)\p1\bord0\shad0\c" + YEL + r"&\fad(80,120)" + POP + "}" + rrect(w, h, 46), 6)
        add(t0, t1, r"{\an5\pos(540,1152)\bord0\shad0\c" + BLK + r"&\fs60\fsp3\fad(80,120)" + POP + "}" + g["text"], 7)
    elif k == "price":
        w, h, y = 860, 240, 560
        anim = (r"\fscx0\fscy0\t(0,140,\fscx112\fscy112)\t(140,230,\fscx100\fscy100)"
                r"\t(230,300,\frz-6)\t(300,370,\frz-1)\t(370,430,\frz-3)")
        add(t0, t1, r"{\an5\pos(540," + str(y) + r")\p1\bord0\shad6\4a&H80&\frz-3\c" + YEL + r"&\fad(0,150)" + anim + "}" + rrect(w, h, 40), 6)
        add(t0, t1, r"{\an5\pos(540," + str(y - 6) + r")\bord0\shad0\frz-3\c" + BLK + r"&\fs146\fad(0,150)" + anim + "}" + g["text"], 7)
        sw = 40 + 30 * len(g["sub"])
        add(t0 + 0.25, t1, r"{\an5\pos(540," + str(y + 150) + r")\p1\bord0\shad0\frz-3\c" + BLK + r"&\fad(80,150)" + POP + "}" + rrect(sw, 78, 39), 6)
        add(t0 + 0.25, t1, r"{\an5\pos(540," + str(y + 151) + r")\bord0\shad0\frz-3\c" + WHT + r"&\fs50\fsp2\fad(80,150)" + POP + "}" + g["sub"], 7)
    elif k == "spec":
        y = g.get("y0", 620) + 150 * g.get("slot", 0)
        label, val = g["rows"][0]
        from PIL import ImageFont
        _f = lambda fs: ImageFont.truetype(os.path.join(HERE, "fonts", "Montserrat-900.ttf"), fs)
        w = max(580, int(_f(48).getlength(label) * 1.08 + _f(88).getlength(val) + 34 + 30 + 50))
        h, xr = 130, 1040
        mv = lambda x0, yy: r"\move(" + f"{x0+420},{yy},{x0},{yy},0,200" + ")"
        add(t0, t1, r"{\an6" + mv(xr, y) + r"\p1\bord0\shad0\c" + BLK + r"&\1a&H40&\fad(60,150)}" + rrect(w, h, 28), 6)
        add(t0, t1, r"{\an4" + mv(xr - w + 34, y) + r"\bord0\shad0\c" + WHT + r"&\fs48\fsp2\fad(60,150)}" + label, 7)
        add(t0, t1, r"{\an6" + mv(xr - 30, y) + r"\bord0\shad0\c" + YEL + r"&\fs88\fad(60,150)}" + val, 7)
    elif k == "chip":
        w = 80 + 36 * len(g["text"])
        cy = g.get("y", 300)
        add(t0, t1, r"{\an5\pos(540," + str(cy) + r")\p1\bord0\shad0\c" + BLK + r"&\1a&H30&\fad(60,150)" + POP + "}" + rrect(w, 96, 48), 6)
        add(t0, t1, r"{\an5\pos(540," + str(cy + 2) + r")\bord0\shad0\c" + WHT + r"&\fs56\fsp4\fad(60,150)" + POP + "}" + g["text"], 7)
        add(t0, t1, r"{\an5\pos(540," + str(cy + 62) + r")\p1\bord0\shad0\c" + YEL + r"&\fad(60,150)\fscx0\t(80,300,\fscx100)}" + rrect(w - 120, 8, 4), 7)
    elif k == "oops":
        anim = r"\t(0,60,\frz12)\t(60,120,\frz4)\t(120,180,\frz10)\t(180,240,\frz6)"
        add(t0, t1, r"{\an5\pos(540,600)\frz8\bord9\shad0\3c" + RED + r"&\fs118\fad(0,100)" + POP + anim + "}" + g["text"], 8)
    elif k == "cta":
        w, h = 900, 128
        pulse = "".join(r"\t(%d,%d,\fscx105\fscy105)\t(%d,%d,\fscx100\fscy100)" % (a, a + 300, a + 300, a + 600)
                        for a in range(400, int((t1 - t0) * 1000), 1200))
        ty = g.get("y", 470)
        add(t0, t1, r"{\an5\pos(540," + str(ty) + r")\p1\bord0\shad5\4a&H90&\c" + YEL + r"&\fad(120,0)" + POP + pulse + "}" + rrect(w, h, 52), 6)
        add(t0, t1, r"{\an5\pos(540," + str(ty + 2) + r")\bord0\shad0\c" + BLK + r"&\fs68\fsp1\fad(120,0)" + POP + pulse + "}" + g["text"], 7)
    elif k == "sfx":
        pass

if THEME == "paper":
    import paper_gfx
    paper_gfx.render(GRAPHICS, KEYPOINTS, src2out, add, TOTAL, C, sfx_events, args.keypoints)

GLASS_WIN = []
if THEME == "rentak":
    import rentak_gfx
    rentak_gfx.render(RENTAK or {}, src2out, add, TOTAL, C, sfx_events, FPS, BEATS, getattr(edl, "ACCENT", "FF5A1F"))
if THEME == "glass":
    import glass_gfx
    GLASS_WIN = glass_gfx.render(getattr(edl, "GLASS", []), getattr(edl, "OVERLAYS", []), src2out, add, TOTAL, C,
                                 sfx_events, FPS, getattr(edl, "ACCENT", "C8102E"))
for _bh in getattr(edl, "BEHIND", None) or []:          # title-behind-subject slam: sound (video is done later)
    if _bh.get("enter", "slam") == "slam" and src2out(_bh["win"][0]) is not None:
        sfx_events += [(src2out(_bh["win"][0]), "thump"), (src2out(_bh["win"][0]), "whoosh")]
CARDS, SCRIMS = [], []
if THEME == "showroom":
    import showroom_gfx
    CARDS, SCRIMS = showroom_gfx.render(getattr(edl, "SHOWROOM", {}), src2out, add, TOTAL, C, sfx_events, FPS,
                                        getattr(edl, "ACCENT", "E6C07B"), BEATS)

if args.keypoints and THEME == "clean":
    from PIL import ImageFont
    KFS = 58
    kfont = ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf", KFS)
    for n, (at, dur, txt) in enumerate(KEYPOINTS):
        t0 = src2out(at)
        if t0 is None: continue
        t1 = min(t0 + dur, TOTAL)
        plain = txt.replace("*", "")
        w = int(kfont.getlength(plain)) + 64
        h = 100
        tilt = (-2.5, 2.0)[n % 2]
        parts = txt.split("*")
        body = "".join((r"{\c" + BLUE + "&}" + p + r"{\c" + INK + "&}") if i % 2 else p for i, p in enumerate(parts))
        common = r"\an5\pos(540,1270)\frz" + str(tilt) + r"\fad(0,120)" + POP
        add(t0, t1, "{" + common + r"\p1\bord0\shad6\4c" + BLK + r"&\4a&HB0&\c" + WHT + "&}" + rrect(w, h, 22), 6)
        add(t0, t1, "{" + common + r"\bord0\shad0\fnInter Display\b1\fs" + str(KFS) + r"\c" + INK + "&}" + body, 7)

ASS = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: None

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{FONT},94,{WHT},{WHT},{BLK},&H64000000,0,0,0,0,100,100,1,0,1,8,4,5,40,40,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n"
ass_path = os.path.abspath(os.path.join(args.work, "edit.ass"))
open(ass_path, "w").write(ASS)
if args.mode == "plan":
    for c in chunks:
        print(f'{c[0]["o0"]:7.2f}  ' + " ".join(norm(w["text"]) for w in c))
    sys.exit(0)

# ---------------------------------------------------------------- audio build
n_total = int(round(TOTAL * SR))
voice = np.zeros((n_total, 2), np.float32)
FADE = int(0.008 * SR)
prev_a1 = None
for s in subs:
    i0, n = int(round(s["a0"] * SR)), int(round(s["dur"] * SR))
    o = int(round(s["o0"] * SR))
    clip = voice_src[i0:i0 + n].copy()
    if prev_a1 is None or abs(prev_a1 - s["a0"]) > 1e-6:
        clip[:FADE] *= np.linspace(0, 1, FADE)[:, None]
    nxt = subs[subs.index(s) + 1]["a0"] if s is not subs[-1] else None
    if nxt is None or abs(nxt - s["a1"]) > 1e-6:
        clip[-FADE:] *= np.linspace(1, 0, FADE)[:, None]
    voice[o:o + len(clip)] = clip[: n_total - o]
    prev_a1 = s["a1"]

def write_wav(p, x):
    with wave.open(p, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())

vraw = os.path.join(args.work, "voice_raw.wav"); vproc = os.path.join(args.work, "voice_proc.wav")
write_wav(vraw, voice)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vraw, "-af",
                (STUDIO_CHAIN if VOICE == "studio" else LOCATION_CHAIN if VOICE == "location" else
                "highpass=f=90,afftdn=nr=8:nf=-38,equalizer=f=250:t=q:w=1.2:g=-2.5,equalizer=f=3500:t=q:w=1.5:g=2,"
                "acompressor=threshold=0.08:ratio=3:attack=5:release=120:makeup=1.6,"
                "loudnorm=I=-15:TP=-2:LRA=9"), "-ar", str(SR), vproc], check=True)
mix = read_wav(vproc)[:n_total]
if len(mix) < n_total: mix = np.vstack([mix, np.zeros((n_total - len(mix), 2), np.float32)])
if AMBIENT:
    apath = os.path.join(args.work, "ambient_bed.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", AMBIENT["file"], "-t", f"{TOTAL:.3f}", "-vn",
                    "-af", f"highpass=f=60,lowpass=f=9000,loudnorm=I={AMBIENT.get('lufs', -34)}:TP=-9:LRA=6,afade=t=in:d=0.3,"
                           f"afade=t=out:st={max(0, TOTAL - 1.0):.3f}:d=1.0", "-ac", "2", "-ar", str(SR), apath], check=True)
    amb = read_wav(apath)[:n_total]
    if len(amb) < n_total: amb = np.vstack([amb, np.zeros((n_total - len(amb), 2), np.float32)])
    mix += amb
if MUSIC:
    mpath = os.path.join(args.work, "music_bed.wav")
    fade_out = MUSIC.get("fade_out", 1.5)
    _at = MUSIC.get("atempo", 1.0)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(MUSIC["start"]), "-t", f"{TOTAL * _at + 0.5:.3f}", "-i", MUSIC["file"], "-vn",
                    "-af", (f"atempo={_at:.5f}," if abs(_at - 1) > 1e-3 else "") + f"loudnorm=I={MUSIC.get('lufs', -27)}:TP=-3:LRA=11,afade=t=in:d=0.25,"
                           f"afade=t=out:st={max(0, TOTAL - fade_out):.3f}:d={fade_out}",
                    "-ac", "2", "-ar", str(SR), mpath], check=True)
    mus = read_wav(mpath)[:n_total]
    if len(mus) < n_total: mus = np.vstack([mus, np.zeros((n_total - len(mus), 2), np.float32)])
    # duck under speech: envelope of the edited voice, fast attack / slow release
    env = np.abs(mix.mean(1))
    blk = 480; nb = len(env) // blk
    lv = 20 * np.log10(np.sqrt((env[:nb * blk].reshape(nb, blk) ** 2).mean(1)) + 1e-9)
    talk = (lv > -42).astype(np.float32)
    g = np.ones(nb, np.float32); duck = 10 ** (-MUSIC.get("duck_db", 6) / 20); cur = 1.0
    for i in range(nb):
        tgt = duck if talk[max(0, i - 2):i + 3].any() else 1.0
        cur += (tgt - cur) * (0.35 if tgt < cur else 0.04)
        g[i] = cur
    gain = np.repeat(g, blk); gain = np.concatenate([gain, np.full(n_total - len(gain), gain[-1] if len(gain) else 1.0)])
    mix += mus * gain[:, None]

GAIN = dict(whoosh=0.20, pop=0.22, cash=0.30, riser=0.20, scratch=0.28, ding=0.25, thump=0.38, paper=0.16, click=0.30, soft=0.09)
for t0, name in sfx_events:
    base = {"riser_in": "riser", "soft": "whoosh"}.get(name, name)
    x = read_wav(os.path.join(args.sfx, base + ".wav"))
    start = t0 - (len(x) / SR if name == "riser_in" else 0.20 if base == "whoosh" else 0)
    i = max(0, int(start * SR)); x = x[: max(0, n_total - i)]
    mix[i:i + len(x)] += x * GAIN.get(name, GAIN.get(base, 0.2))
mix_path = os.path.join(args.work, "mix.wav")
write_wav(mix_path, mix)
final_audio = os.path.join(args.work, "mix_lim.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mix_path, "-af", "alimiter=limit=0.89:level=false",
                "-ar", str(SR), final_audio], check=True)
if args.mode == "final":
    # TikTok export standard: two-pass linear loudnorm to -14 LUFS / -1 dBTP
    _m = subprocess.run(["ffmpeg", "-hide_banner", "-i", final_audio, "-af", "loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json",
                         "-f", "null", "-"], capture_output=True, text=True).stderr
    _j = json.loads(_m[_m.rindex("{"):_m.rindex("}") + 1])
    _ln = os.path.join(args.work, "mix_tiktok.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", final_audio, "-af",
                    f"loudnorm=I=-14:TP=-1.0:LRA=11:measured_I={_j['input_i']}:measured_TP={_j['input_tp']}:"
                    f"measured_LRA={_j['input_lra']}:measured_thresh={_j['input_thresh']}:offset={_j['target_offset']}:linear=true",
                    "-ar", str(SR), _ln], check=True)
    final_audio = _ln

# ---------------------------------------------------------------- video render
probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height:stream_side_data=rotation", "-of", "json", args.src],
                                  capture_output=True, text=True).stdout)["streams"][0]
SW, SH = probe["width"], probe["height"]
rot = 0
for sd in probe.get("side_data_list", []):
    rot = sd.get("rotation", rot)
if abs(rot) == 90: SW, SH = SH, SW
print("source", SW, SH, "rot", rot)

PIX, NP, BPP = ("rgb48le", np.uint16, 6) if args.hdr else ("bgr24", np.uint8, 3)
if args.hdr:
    enc = ["-c:v", "libx265", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p10le", "-tag:v", "hvc1",
           "-x265-params", "log-level=error:colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited"
           ":vbv-maxrate=12000:vbv-bufsize=24000",
           "-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc", "-color_range", "tv",
           "-c:a", "aac", "-b:a", "320k"]
    VF_OUT = "scale=out_color_matrix=bt2020:out_range=tv,format=yuv420p10le"
elif args.mode == "final":
    enc = ["-c:v", "libx264", "-preset", "fast", "-crf", "12", "-c:a", "pcm_s16le"]       # intermediate (TikTok 2-pass below)
else:
    enc = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-c:a", "aac", "-b:a", "192k"]
if not args.hdr:
    enc += ["-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709"]
    VF_OUT = "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p"
fontsdir = os.path.join(HERE, "fonts")
TIKTOK = args.mode == "final" and not args.hdr          # standard TikTok upload export
OUT_STAGE = os.path.join(args.work, "_master_tmp.mkv") if TIKTOK else args.out
writer = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", PIX, "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
     "-i", final_audio, "-vf", f"ass={ass_path}:fontsdir={fontsdir}," + VF_OUT,
     *enc, *(["-movflags", "+faststart"] if not TIKTOK else []), "-shortest", OUT_STAGE], stdin=subprocess.PIPE)

base = OW / SW

def glass_level(T, ramp=0.35):
    lv = 0.0
    for a, b in GLASS_WIN:
        if a - ramp < T < b + ramp:
            up = min(1.0, (T - a + ramp) / ramp) if T < a else 1.0
            dn = min(1.0, (b + ramp - T) / ramp) if T > b else 1.0
            x = max(0.0, min(up, dn)); lv = max(lv, x * x * (3 - 2 * x))
    return lv

GLASS_TOP = getattr(edl, "GLASS_TOP", 0)
if GLASS_TOP:
    _y0 = int(GLASS_TOP * OH / 1920); _f = int(70 * OH / 1920)
    GLASS_MASK = np.clip((np.arange(OH, dtype=np.float32) - _y0) / _f, 0, 1)[:, None] * np.ones((1, OW), np.float32)
WHITE_VAL = (65535 if args.hdr else 255) * (0.80 if args.hdr else 0.96)
def apply_glass(img, lv):
    """Frosted glass: strong blur (via 1/8 downscale) + wash to white, both scaled by lv (0..1)."""
    h, w = img.shape[:2]
    small = cv2.resize(img, (w // 8, h // 8), interpolation=cv2.INTER_AREA).astype(np.float32)
    small = cv2.GaussianBlur(small, (0, 0), 1.0 + 6.0 * lv)
    blur = cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)
    a = min(1.0, lv * 1.6)
    out = img.astype(np.float32) * (1 - a) + blur * a
    wsh = 0.80 * lv
    out = out * (1 - wsh) + WHITE_VAL * wsh
    out += np.random.standard_normal(out.shape[:2]).astype(np.float32)[:, :, None] * (0.9 * lv * (257 if args.hdr else 1))
    if GLASS_TOP:                                   # keep a burned-in header sharp: glass only below it, feathered
        m = GLASS_MASK[:, :, None] if out.ndim == 3 else GLASS_MASK
        out = img.astype(np.float32) * (1 - m) + out * m
    return out.astype(img.dtype)
PANEL = None
if LAYOUT and LAYOUT.get("kind") == "inset":
    sc = OW / 1080
    bx, by, bw, bh = [int(round(v * sc)) for v in LAYOUT["box"]]
    brd = int(round(LAYOUT.get("border", 16) * sc))
    gain = GFX_GAIN
    rng = np.random.default_rng(3)
    # cream paper: base colour + fine grain + soft low-frequency mottling
    paper = np.array([242, 236, 223], np.float32) / 255.0
    lo = cv2.resize(rng.standard_normal((24, 14)).astype(np.float32), (OW, OH), interpolation=cv2.INTER_CUBIC)
    grain = rng.standard_normal((OH, OW)).astype(np.float32)
    lum = 1.0 + 0.018 * lo + 0.006 * grain
    bg = paper[None, None, :] * lum[:, :, None]
    # soft drop shadow under the photo
    sh = np.zeros((OH, OW), np.float32)
    sh[by - brd + int(14 * sc): by + bh + brd + int(14 * sc), bx - brd + int(6 * sc): bx + bw + brd + int(6 * sc)] = 1
    sh = cv2.GaussianBlur(sh, (0, 0), 18 * sc)
    bg *= (1 - 0.30 * sh)[:, :, None]
    bg[by - brd: by + bh + brd, bx - brd: bx + bw + brd] = np.array([251, 250, 247], np.float32) / 255.0   # white photo border
    bg = np.clip(bg * gain, 0, 1)
    if args.hdr:
        BG = (bg * 65535).astype(np.uint16)                     # RGB order (rgb48le)
    else:
        BG = (bg[:, :, ::-1] * 255).astype(np.uint8)            # BGR order (bgr24)
    PANEL = (bx, by, bw, bh)
if CARDS or SCRIMS:
    # THEME "showroom": full-screen card background (night showroom: spotlight + glossy floor + horizon line),
    # framed photos with a specular light sweep, and a bottom scrim under lower-thirds on footage.
    _s = OW / 1080
    _y = (np.arange(OH, dtype=np.float32) / OH)[:, None]; _x = (np.arange(OW, dtype=np.float32) / OW)[None, :]
    _acc = np.array([int(getattr(edl, "ACCENT", "E6C07B")[i:i + 2], 16) for i in (4, 2, 0)], np.float32)   # BGR
    _base = np.array([15, 12, 12], np.float32) * (1 - _y[..., None]) + np.array([6, 5, 5], np.float32) * _y[..., None]
    _d = np.sqrt(((_x - 0.5) / 0.62) ** 2 + ((_y - 0.0) / 0.50) ** 2)
    _spot = np.clip(1 - _d, 0, 1) ** 2.0
    _bg = _base + _spot[..., None] * (_acc * 0.15 + 6)
    _hz = 0.835
    _dr = np.sqrt(((_x - 0.5) / 0.48) ** 2 + ((_y - _hz - 0.025) / 0.05) ** 2)
    _refl = np.clip(1 - _dr, 0, 1) ** 1.6
    _floor = (_y > _hz).astype(np.float32)[..., None] * np.ones((1, OW, 1), np.float32)
    _bg = _bg * (1 - 0.35 * _floor) + _floor * _refl[..., None] * _acc * 0.20
    _span = np.clip(1 - np.abs(_x - 0.5) / 0.5, 0, 1)
    _bg += (np.exp(-((_y - _hz) * OH / (2.2 * _s)) ** 2) * _span ** 0.5)[..., None] * _acc * 0.60
    _bg += (np.exp(-((_y - _hz) * OH / (30 * _s)) ** 2) * _span)[..., None] * _acc * 0.10
    _bg *= np.clip(1 - 0.6 * (((_x - 0.5) / 0.75) ** 2 + ((_y - 0.45) / 0.85) ** 2), 0.3, 1)[..., None]
    CARD_BG = np.clip(_bg, 0, 255).astype(np.float32)
    _rng = np.random.default_rng(7)
    GRAIN = [_rng.normal(0, 2.2, (OH, OW, 1)).astype(np.float32) for _ in range(4)]
    SCRIM = (np.clip((_y - 0.50) / 0.50, 0, 1) ** 1.3 * 0.80)[..., None].astype(np.float32)
    _photos = {}
    def _photo(path, bw, bh):
        k = (path, bw, bh)
        if k not in _photos:
            im = cv2.imread(path, cv2.IMREAD_COLOR)
            ih, iw = im.shape[:2]; ar = bw / bh
            if iw / ih > ar: nw = int(ih * ar); im = im[:, (iw - nw) // 2:(iw - nw) // 2 + nw]
            else: nh = int(iw / ar); im = im[(ih - nh) // 2:(ih - nh) // 2 + nh]
            _photos[k] = cv2.resize(im, (int(bw * 1.08), int(bh * 1.08)), interpolation=cv2.INTER_AREA).astype(np.float32)
        return _photos[k]
    def card_frame(cd, T, fi):
        img = CARD_BG + GRAIN[fi % 4]
        if cd.get("photo") and cd.get("box"):
            bx, by, bw, bh = [int(round(v * _s)) for v in cd["box"]]
            src = _photo(cd["photo"], bw, bh)
            p = (T - cd["a"]) / max(0.5, cd["b"] - cd["a"])
            z = 1.0 + 0.07 * (1 - p)                                   # slow push-out (Ken Burns)
            sw, sh = int(bw * z), int(bh * z)
            im = cv2.resize(src, (sw, sh), interpolation=cv2.INTER_LINEAR)
            ox, oy = (sw - bw) // 2, (sh - bh) // 2
            im = im[oy:oy + bh, ox:ox + bw]
            al = min(1.0, max(0.0, (T - cd["a"] - 0.12) / 0.30)); al = al * al * (3 - 2 * al)
            ty = by + int(round(30 * _s * (1 - al)))
            u = (T - cd["a"] - 0.45) / 0.85                             # specular light sweep across the photo
            if -0.1 < u < 1.2:
                gx = (np.arange(bw, dtype=np.float32) / bw)[None, :]; gy = (np.arange(bh, dtype=np.float32) / bh)[:, None]
                c = (gx + 0.35 * gy) / 1.35
                band = 0.42 * np.exp(-((c - (u * 1.4 - 0.2)) / 0.055) ** 2)
                im = im + band[..., None] * (255 - im)
            y0, y1 = max(0, ty), min(OH, ty + bh)
            if y1 > y0:
                img[y0:y1, bx:bx + bw] = img[y0:y1, bx:bx + bw] * (1 - al) + im[y0 - ty:y1 - ty] * al
        return np.clip(img, 0, 255).astype(np.uint8)
    def win_level(wins, T, ramp=0.18):
        lv = 0.0
        for a, b in wins:
            if a - ramp < T < b + ramp:
                up = min(1.0, (T - a + ramp) / ramp) if T < a else 1.0
                dn = min(1.0, (b + ramp - T) / ramp) if T > b else 1.0
                lv = max(lv, max(0.0, min(up, dn)))
        return lv
BEHIND_OUT = []
if getattr(edl, "BEHIND", None):
    # Big title placed BEHIND the subject (presenter / car): the title is composited over the footage and the
    # subject is pasted back on top using a per-frame segmentation mask (BiRefNet via rembg, cached per source frame).
    from PIL import Image, ImageDraw, ImageFilter, ImageFont as _IF
    def _title_layer(bh):
        W0, H0 = 1080, 1920
        font_path = bh["font"]
        main_txt = bh["main"]; plain = main_txt.replace("*", "")
        size = 400
        while size > 40:
            f = _IF.truetype(font_path, size); bb = f.getbbox(plain)
            if bb[2] - bb[0] <= bh.get("width", 1000): break
            size -= 4
        fm = _IF.truetype(font_path, size); bbm = fm.getbbox(plain); cap = bbm[3] - bbm[1]
        bottom = bh["bottom"]; main_top = bottom - cap
        fs_top = max(20, int(size * bh.get("top_scale", 0.40)))
        ft = _IF.truetype(font_path, fs_top); trk = int(fs_top * 0.32)
        top_txt = bh.get("top", "")
        tw_ = sum(ft.getlength(c) for c in top_txt) + trk * max(0, len(top_txt) - 1)
        bbt = ft.getbbox("T"); cap_t = bbt[3] - bbt[1]
        top_bottom = main_top - int(cap * 0.16)
        rgba = Image.new("RGBA", (W0, H0), (0, 0, 0, 0)); dr = ImageDraw.Draw(rgba)
        acc = tuple(int(getattr(edl, "ACCENT", "E6C07B")[i:i + 2], 16) for i in (0, 2, 4))
        # main line: centred, *word* in the accent colour
        x = (W0 - (bbm[2] - bbm[0])) / 2 - bbm[0]
        for k, part in enumerate(main_txt.split("*")):
            if not part: continue
            dr.text((x, main_top - bbm[1]), part, font=fm, fill=(acc + (255,)) if k % 2 else (255, 255, 255, 255))
            x += fm.getlength(part)
        x = (W0 - tw_) / 2
        for c in top_txt:
            dr.text((x, top_bottom - cap_t - bbt[1]), c, font=ft, fill=(255, 255, 255, 235)); x += ft.getlength(c) + trk
        a = np.array(rgba).astype(np.float32) / 255.0
        sh = Image.fromarray((a[..., 3] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(18))
        sh = np.roll(np.array(sh).astype(np.float32) / 255.0, 10, axis=0) * 0.55
        a = cv2.resize(a, (OW, OH), interpolation=cv2.INTER_AREA); sh = cv2.resize(sh, (OW, OH), interpolation=cv2.INTER_AREA)
        return dict(rgb=a[..., [2, 1, 0]] * 255.0, A=a[..., 3], S=sh,
                    cy=(top_bottom - cap_t + bottom) / 2 * OH / 1920, bottom=bottom * OH / 1920)
    for bh in edl.BEHIND:
        a = src2out(bh["win"][0]); b = src2out(bh["win"][1] - 0.04)
        if a is None or b is None: continue
        it = dict(bh, a=a, b=b + 0.04); it.update(_title_layer(bh)); BEHIND_OUT.append(it)
    _mask_dir = os.path.join(args.work, "_masks"); os.makedirs(_mask_dir, exist_ok=True)
    _rb = {}
    def subject_mask(src, tv, frame):
        key = os.path.join(_mask_dir, f"{os.path.basename(src)}_{int(round(tv * 60)):06d}.png")
        if os.path.exists(key):
            m = cv2.imread(key, 0)
        else:
            if "s" not in _rb:
                from rembg import new_session, remove
                _rb["s"] = new_session(getattr(edl, "MASK_MODEL", "birefnet-general-lite")); _rb["remove"] = remove
            m = np.array(_rb["remove"](Image.fromarray(frame[..., ::-1]), session=_rb["s"], only_mask=True))
            cv2.imwrite(key, m)
        if m.shape[:2] != frame.shape[:2]:                 # masks may be precomputed at a lower resolution
            m = cv2.resize(m, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_LINEAR)
        return m.astype(np.float32) / 255.0
    def behind_title(out, mk, bh, T):
        e = min(1.0, max(0.0, (T - bh["a"]) / 0.35)); e = 1 - (1 - e) ** 3
        if bh.get("enter", "slam") != "slam": e = 1.0 - 0.6 * (1 - e)
        fo = min(1.0, max(0.0, (bh["b"] - T) / 0.22)) if bh.get("exit", True) else 1.0
        al = min(1.0, e * 1.3) * fo
        sc = 1.0 + 0.12 * (1 - e)
        rgb, A, S = bh["rgb"], bh["A"], bh["S"]
        if sc > 1.001:
            M = np.float32([[sc, 0, (1 - sc) * OW / 2], [0, sc, (1 - sc) * bh["cy"]]])
            rgb = cv2.warpAffine(rgb, M, (OW, OH)); A = cv2.warpAffine(A, M, (OW, OH)); S = cv2.warpAffine(S, M, (OW, OH))
        f = out.astype(np.float32)
        yy = np.arange(OH, dtype=np.float32)[:, None]
        dim = (bh.get("dim", 0.35) * al * np.clip(1 - (yy - bh["bottom"]) / (260 * OH / 1920), 0, 1))[..., None]
        bg = f * (1 - dim) * (1 - (S * al)[..., None])
        A3 = (A * al)[..., None]
        comp = bg * (1 - A3) + rgb * A3
        m = mk[..., None]
        return np.clip(comp * (1 - m) + f * m, 0, 255).astype(np.uint8)
n_frames = int(round((min(TOTAL, args.limit) if args.limit else TOTAL) * FPS))
fi = 0
for s in subs:
    first = math.ceil(s["o0"] * FPS - 1e-6)
    last = min(math.ceil(s["o1"] * FPS - 1e-6), n_frames)
    cnt = last - first
    if cnt <= 0:
        if first >= n_frames: break
        continue
    off = first / FPS - s["o0"]
    _src = SOURCES.get(s["seg"].get("vsrc"), args.src) if s["seg"].get("vsrc") else args.src
    rd = subprocess.Popen(["ffmpeg", "-v", "quiet", "-ss", f"{s['v0'] + off:.4f}", "-i", _src, "-an",
                           "-frames:v", str(cnt + 2), "-vf",
                           (f"fps={FPS},colorspace=all=bt709:iall=bt2020:itrc=bt709:fast=0:format=yuv420p,"
                            f"scale=in_color_matrix=bt709:in_range=tv,format=" + PIX) if (SRC_MATRIX == "bt2020" and not args.hdr) else
                           f"fps={FPS},scale=in_color_matrix={SRC_MATRIX}:in_range=tv,format=" + PIX,
                           "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    fsz = SW * SH * BPP
    frame = None
    for j in range(cnt):
        b = rd.stdout.read(fsz)
        if len(b) == fsz:
            frame = np.frombuffer(b, NP).reshape(SH, SW, 3)
        if TIKTOK and len(b) == fsz:                      # light unsharp on footage only (graphics stay crisp)
            frame = cv2.addWeighted(frame, 1.30, cv2.GaussianBlur(frame, (0, 0), 1.4), -0.30, 0)
        tv = s["v0"] + off + j / FPS
        z, cx, cy = zoom_at(s["seg"], tv, s["punch"])
        if PANEL:
            bx, by, bw, bh = PANEL
            k = bw * z / SW                                     # z = 1: full source width fills the photo
            rw, rh = max(bw, round(SW * k)), max(bh, round(SH * k))
            img = cv2.resize(frame, (rw, rh), interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_LINEAR)
            x0 = int(round(min(max(cx * rw - bw / 2, 0), rw - bw)))
            y0 = int(round(min(max(cy * rh - bh / 2, 0), rh - bh)))
            canvas = BG.copy()
            canvas[by:by + bh, bx:bx + bw] = img[y0:y0 + bh, x0:x0 + bw]
            writer.stdin.write(canvas.tobytes())
        else:
            k = base * z
            rw, rh = max(OW, round(SW * k)), max(OH, round(SH * k))
            img = cv2.resize(frame, (rw, rh), interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_LINEAR)
            x0 = int(round(min(max(cx * rw - OW / 2, 0), rw - OW)))
            y0 = int(round(min(max(cy * rh - OH / 2, 0), rh - OH)))
            out = img[y0:y0 + OH, x0:x0 + OW]
            lv = glass_level(fi / FPS) if GLASS_WIN else 0.0
            if lv > 0.001: out = apply_glass(out, lv)
            if BEHIND_OUT:
                _T = fi / FPS
                _bh = next((b for b in BEHIND_OUT if b["a"] <= _T < b["b"]), None)
                if _bh is not None and frame is not None:
                    _m = subject_mask(_src, tv, frame)
                    _m = cv2.resize(_m, (rw, rh), interpolation=cv2.INTER_LINEAR)[y0:y0 + OH, x0:x0 + OW]
                    out = behind_title(np.ascontiguousarray(out), _m, _bh, _T)
            if CARDS or SCRIMS:
                _T = fi / FPS
                _cd = next((c for c in CARDS if c["a"] <= _T < c["b"]), None)
                if _cd is not None:
                    out = card_frame(_cd, _T, fi)
                else:
                    _lv = win_level(SCRIMS, _T)
                    if _lv > 0.001: out = (out.astype(np.float32) * (1 - _lv * SCRIM)).astype(np.uint8)
            writer.stdin.write(np.ascontiguousarray(out).tobytes())
        fi += 1
    rd.stdout.close(); rd.kill(); rd.wait()
    print(f"\r{fi}/{n_frames} frames", end="", flush=True)
writer.stdin.close(); writer.wait()
if TIKTOK:
    # TikTok upload standard: H.264 High, 1080x1920, source fps, SDR BT.709, 2-pass VBR sized to stay < 95 MB
    # (GitHub delivery) and <= 16 Mbps, GOP 2 s, AQ mode 3 (protects flat/dark gradients), AAC 320k 48 kHz.
    vk = int(min(16000, ((95e6 * 8 / TOTAL) - 330e3) / 1000 * 0.97))
    common = ["-c:v", "libx264", "-preset", "slow", "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p",
              "-b:v", f"{vk}k", "-maxrate", f"{int(vk * 1.6)}k", "-bufsize", f"{int(vk * 2)}k",
              "-g", str(FPS * 2), "-keyint_min", str(FPS), "-bf", "2", "-x264-params", "aq-mode=3",
              "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv"]
    plog = os.path.join(args.work, "_x264_2pass")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", OUT_STAGE, *common, "-pass", "1", "-passlogfile", plog, "-an", "-f", "mp4", "/dev/null"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", OUT_STAGE, *common, "-pass", "2", "-passlogfile", plog,
                    "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", args.out], check=True)
    os.remove(OUT_STAGE)
    print(f"\nTikTok export: H.264 {vk} kbps, {FPS} fps, -14 LUFS")
print("\ndone", args.out, f"{TOTAL:.2f}s")
