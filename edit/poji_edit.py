#!/usr/bin/env python3
"""Car-dealer TikTok edit ("Poji Hebat" style) for the Toyota Alphard Z clip.

Style:
  * Bold pop-in captions (2-4 words) in Formula1 Bold, white with yellow keywords,
    thick black outline + soft drop shadow, matching the title already in the raw.
  * Punch-in zooms on sentence beats / shot changes, slow push between punches.
  * Price reveal: big yellow "RM259,000" stamp with white flash + camera shake + ding.
  * CTA pill "BERMINAT? TEKAN LINK DI BIO".
  * Music bed (Presto section) ducked under the voice, whoosh SFX on punch-ins.

Usage:
  python3 poji_edit.py --raw RAW.mov --music MUSIC.mp4 --font FONT.ttf --out OUT.mp4 [--preview]
"""
import argparse
import math
import subprocess
import wave

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W_FULL, H_FULL = 1080, 1920
FPS = 60.0
DURATION = 47.65
MUSIC_START = 886.0  # seconds into the music file (energetic Presto section)

YELLOW = (255, 210, 31)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# ---------------------------------------------------------------------------
# Captions: (start, end, text). Words wrapped in *...* are highlighted yellow.
# Timings come from Whisper word timestamps; wording corrected by hand.
# ---------------------------------------------------------------------------
CAPTIONS = [
    (0.00, 0.78, "*FREE BODYKIT*"),
    (0.78, 1.70, "UNTUK PELANGGAN"),
    (1.70, 2.36, "DI LUAR SANA"),
    (2.36, 3.50, "UNTUK SEBUAH UNIT"),
    (3.50, 4.90, "*TOYOTA ALPHARD Z*"),
    (4.90, 6.26, "TAHUN *2024*"),
    (6.26, 8.30, "DENGAN *GRADE 5A*"),
    (8.30, 8.96, "MILEAGE ORIGINAL"),
    (8.96, 9.98, "*5,000 KM* LEBIH"),
    (9.98, 10.54, "SAHAJA!"),
    (10.54, 11.30, "KERETA NI"),
    (11.30, 12.52, "MEMANG CUKUP *LENGKAP*"),
    (12.52, 13.64, "CUMA KURANG SATU"),
    (13.64, 14.40, "BODYKIT *MODELLISTA*"),
    (14.40, 15.72, "YANG KITA AKAN *TAMBAH*"),
    (15.72, 17.46, "UNTUK UNIT NI"),
    (17.46, 18.20, "BAHAGIAN DEPAN"),
    (18.20, 19.20, "DAH SAMPAI SIAP"),
    (19.20, 20.58, "DARIPADA *JEPUN*"),
    (20.58, 21.72, "ORIGINAL *DAYLIGHT*"),
    (21.72, 23.16, "*MODELLISTA* BAHAGIAN DEPAN"),
    (23.16, 24.28, "*RIM 18 INCI*"),
    (24.28, 25.58, "TAMBAHAN *CHROME*"),
    (25.58, 26.84, "BAHAGIAN FENDER TEPI"),
    (26.84, 28.34, "DAN JUGA PINTU"),
    (28.34, 29.42, "BAHAGIAN BELAKANG"),
    (29.42, 30.00, "DATANG DENGAN"),
    (30.00, 30.96, "*2 POWER DOOR*"),
    (30.96, 32.20, "*BLIND SPOT* MONITORING"),
    (32.20, 32.62, "*PARKING SENSOR*"),
    (32.62, 34.36, "DAN JUGA *TOYOTA T-MATE*"),
    (34.36, 35.64, "*MOONROOF* PUN DAH SIAP"),
    (35.64, 36.84, "*ROOF MONITOR* PUN DAH ADA"),
    (36.84, 37.88, "UNTUK ANAK-ANAK KORANG"),
    (37.88, 38.62, "DI BELAKANG"),
    (38.62, 39.74, "SO HARGANYA *BERAPA?*"),
    (39.74, 40.22, "HARGANYA..."),
    # 40.22 - 43.80 handled by the price stamp
    (43.80, 45.04, "HARGA YANG SANGAT *MURAH!*"),
    (46.36, 47.65, "ASSALAMUALAIKUM"),
]

PRICE_START, PRICE_SUB_START, PRICE_END = 40.22, 42.46, 43.80
CTA_START, CTA_END = 45.04, 46.36

# Zoom keyframes (time, zoom). Instant "punch" with a small overshoot, slow push between.
ZOOM_KEYS = [
    (0.00, 1.00), (4.23, 1.00), (6.55, 1.00), (9.48, 1.08), (12.52, 1.16),
    (15.72, 1.06), (18.53, 1.00), (20.62, 1.06), (23.16, 1.14), (26.84, 1.04),
    (30.96, 1.14), (33.88, 1.00), (36.45, 1.00), (38.38, 1.06), (40.22, 1.18),
    (40.70, 1.10), (43.80, 1.18), (45.04, 1.06),
]
PUSH_PER_SEC = 0.006
# Punches that get a whoosh (the ones that are not already hard cuts in the raw get the
# strongest effect, but a light whoosh on every zoom change keeps the rhythm).
WHOOSH_TIMES = [9.48, 12.52, 15.72, 20.62, 23.16, 26.84, 30.96, 38.38, 43.80]


def ease_out_cubic(x):
    return 1 - (1 - x) ** 3


def ease_out_back(x, k=1.9):
    x -= 1
    return 1 + (k + 1) * x ** 3 + k * x ** 2


def zoom_at(t):
    idx = 0
    for i, (kt, _) in enumerate(ZOOM_KEYS):
        if t >= kt:
            idx = i
    kt, kz = ZOOM_KEYS[idx]
    prev_z = ZOOM_KEYS[idx - 1][1] if idx > 0 else kz
    dt = t - kt
    z = kz + PUSH_PER_SEC * dt
    # overshoot on punch-in (only when zooming in)
    if idx > 0 and kz > prev_z and dt < 0.25:
        z += 0.035 * (1 - ease_out_cubic(dt / 0.25))
    return z


def shake_at(t, s):
    dt = t - PRICE_START
    if 0 <= dt < 0.35:
        amp = 14 * s * (1 - dt / 0.35)
        return amp * math.sin(dt * 95), amp * math.cos(dt * 77)
    return 0.0, 0.0


def flash_at(t):
    dt = t - PRICE_START
    if 0 <= dt < 0.14:
        return 0.55 * (1 - dt / 0.14)
    return 0.0


# ---------------------------------------------------------------------------
# Text rendering
# ---------------------------------------------------------------------------
def parse_markup(text):
    """'TAHUN *2024*' -> [('TAHUN', False), ('2024', True)]"""
    words, hl = [], False
    for tok in text.split(" "):
        start_hl = tok.startswith("*")
        if start_hl:
            hl = True
            tok = tok[1:]
        end_hl = tok.endswith("*")
        if end_hl:
            tok = tok[:-1]
        words.append((tok, hl))
        if end_hl:
            hl = False
    return words


def render_words(lines, font, stroke, shadow_off, line_gap):
    """lines: list of list of (word, color). Returns RGBA image (tight-ish)."""
    space = font.getlength(" ")
    asc, desc = font.getmetrics()
    line_h = asc + desc
    widths = [sum(font.getlength(w) for w, _ in ln) + space * (len(ln) - 1) for ln in lines]
    pad = stroke + shadow_off + 12
    iw = int(max(widths) + 2 * pad)
    ih = int(len(lines) * line_h + (len(lines) - 1) * line_gap + 2 * pad)

    text = Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    d = ImageDraw.Draw(text)
    y = pad
    for ln, lw in zip(lines, widths):
        x = (iw - lw) / 2
        for w, col in ln:
            d.text((x, y), w, font=font, fill=col + (255,), stroke_width=stroke,
                   stroke_fill=BLACK + (255,))
            x += font.getlength(w) + space
        y += line_h + line_gap

    # soft drop shadow
    alpha = text.split()[3]
    shadow = Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    shadow.putalpha(alpha.point(lambda a: int(a * 0.55)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(max(1, shadow_off // 2)))
    out = Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    out.alpha_composite(shadow, (0, shadow_off))
    out.alpha_composite(text)
    return out


def layout_caption(text, font_path, size, max_w, stroke, shadow_off):
    words = [(w, YELLOW if hl else WHITE) for w, hl in parse_markup(text)]

    def width(font, ws):
        return sum(font.getlength(w) for w, _ in ws) + font.getlength(" ") * (len(ws) - 1)

    # 1) one line, allowing a little shrink (avoids orphan words like "ALPHARD / Z")
    for sz in (size, int(size * 0.92), int(size * 0.85)):
        font = ImageFont.truetype(font_path, sz)
        if width(font, words) <= max_w:
            return render_words([words], font, stroke, shadow_off, line_gap=int(sz * 0.08))
    if len(words) == 1:  # single long word: shrink until it fits
        while width(font, words) > max_w:
            size = int(size * 0.92)
            font = ImageFont.truetype(font_path, size)
        return render_words([words], font, stroke, shadow_off, line_gap=int(size * 0.08))
    # 2) two balanced lines, shrinking until it fits
    while True:
        font = ImageFont.truetype(font_path, size)
        best = min(range(1, len(words)),
                   key=lambda k: max(width(font, words[:k]), width(font, words[k:])))
        lines = [words[:best], words[best:]]
        if max(width(font, ln) for ln in lines) <= max_w:
            return render_words(lines, font, stroke, shadow_off, line_gap=int(size * 0.08))
        size = int(size * 0.92)


def render_pill(text, font_path, size, fg, bg, s):
    font = ImageFont.truetype(font_path, size)
    tw = font.getlength(text)
    asc, desc = font.getmetrics()
    px, py = int(34 * s), int(18 * s)
    w, h = int(tw + 2 * px), int(asc + desc + 2 * py)
    sh = int(10 * s)
    img = Image.new("RGBA", (w + 2 * sh, h + 3 * sh), (0, 0, 0, 0))
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([sh, sh * 2, sh + w, sh * 2 + h], radius=h // 2,
                                             fill=(0, 0, 0, 150))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(sh // 2 + 1)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([sh, sh, sh + w, sh + h], radius=h // 2, fill=bg + (255,),
                        outline=BLACK + (255,), width=max(2, int(5 * s)))
    d.text((sh + px, sh + py), text, font=font, fill=fg + (255,))
    return img


def to_np(img):
    a = np.asarray(img).astype(np.float32)
    return a[..., :3], a[..., 3:4] / 255.0


class Layer:
    """A pre-rendered RGBA element with a pop-in animation."""

    def __init__(self, img, start, end, cx, cy, pop_from=0.6, pop_dur=0.18):
        self.rgb, self.a = to_np(img)
        self.start, self.end, self.cx, self.cy = start, end, cx, cy
        self.pop_from, self.pop_dur = pop_from, pop_dur
        self.cache = {}

    def active(self, t):
        return self.start <= t < self.end

    def scale_at(self, t):
        dt = t - self.start
        if dt >= self.pop_dur:
            return 1.0
        return self.pop_from + (1 - self.pop_from) * ease_out_back(dt / self.pop_dur)

    def draw(self, frame, t):
        sc = round(self.scale_at(t), 3)
        if sc not in self.cache:
            if sc == 1.0:
                self.cache[sc] = (self.rgb, self.a)
            else:
                h, w = self.a.shape[:2]
                nw, nh = max(1, int(w * sc)), max(1, int(h * sc))
                self.cache[sc] = (cv2.resize(self.rgb, (nw, nh), interpolation=cv2.INTER_LINEAR),
                                  cv2.resize(self.a, (nw, nh), interpolation=cv2.INTER_LINEAR)[..., None])
        rgb, a = self.cache[sc]
        h, w = a.shape[:2]
        x0, y0 = int(self.cx - w / 2), int(self.cy - h / 2)
        fh, fw = frame.shape[:2]
        xa, ya, xb, yb = max(0, x0), max(0, y0), min(fw, x0 + w), min(fh, y0 + h)
        if xa >= xb or ya >= yb:
            return
        src_rgb = rgb[ya - y0:yb - y0, xa - x0:xb - x0]
        src_a = a[ya - y0:yb - y0, xa - x0:xb - x0]
        roi = frame[ya:yb, xa:xb]
        roi[:] = src_rgb * src_a + roi * (1 - src_a)


def build_layers(font_path, s, W, H):
    layers = []
    cap_y = int(1330 * s)
    for st, en, txt in CAPTIONS:
        img = layout_caption(txt, font_path, int(84 * s), int(930 * s), int(9 * s), int(8 * s))
        layers.append(Layer(img, st, en, W / 2, cap_y))

    # Price stamp group
    label = render_pill("HARGANYA", font_path, int(52 * s), BLACK, WHITE, s)
    layers.append(Layer(label, PRICE_START, PRICE_END, W / 2, int(1150 * s), pop_from=0.3))
    price = layout_caption("*RM259,000*", font_path, int(160 * s), int(1000 * s), int(14 * s), int(12 * s))
    layers.append(Layer(price, PRICE_START, PRICE_END, W / 2, int(1300 * s), pop_from=1.8, pop_dur=0.16))
    sub = render_pill("BELUM ON THE ROAD", font_path, int(46 * s), WHITE, (20, 20, 20), s)
    layers.append(Layer(sub, PRICE_SUB_START, PRICE_END, W / 2, int(1460 * s), pop_from=0.4))

    # CTA
    cta1 = layout_caption("BERMINAT?", font_path, int(84 * s), int(930 * s), int(9 * s), int(8 * s))
    layers.append(Layer(cta1, CTA_START, CTA_END, W / 2, int(1230 * s)))
    cta2 = render_pill("TEKAN LINK DI BIO", font_path, int(60 * s), BLACK, YELLOW, s)
    layers.append(Layer(cta2, CTA_START + 0.12, CTA_END, W / 2, int(1360 * s), pop_from=0.3))
    return layers


# ---------------------------------------------------------------------------
# SFX (synthesised, no external assets)
# ---------------------------------------------------------------------------
def make_sfx(path, sr=48000):
    n = int((DURATION + 1) * sr)
    out = np.zeros(n, np.float32)
    rng = np.random.default_rng(7)

    def add(sig, t):
        i = int(t * sr)
        j = min(n, i + len(sig))
        if i < n:
            out[i:j] += sig[: j - i]

    # whoosh: noise through a sweeping one-pole low-pass, peaking at the punch
    def whoosh(dur=0.32):
        m = int(dur * sr)
        noise = rng.standard_normal(m).astype(np.float32)
        x = np.linspace(0, 1, m)
        cutoff = 300 + 5000 * np.sin(np.pi * x) ** 2
        alpha = 1 - np.exp(-2 * np.pi * cutoff / sr)
        y = np.zeros(m, np.float32)
        acc = 0.0
        for k in range(m):
            acc += alpha[k] * (noise[k] - acc)
            y[k] = acc
        env = np.sin(np.pi * x) ** 1.5
        return y * env * 0.35

    for t in WHOOSH_TIMES:
        add(whoosh(), max(0, t - 0.2))

    # price: low impact + bright "ding"
    m = int(0.5 * sr)
    tt = np.arange(m) / sr
    impact = np.sin(2 * np.pi * (90 * tt - 40 * tt ** 2)) * np.exp(-tt * 9) * 0.6
    add(impact.astype(np.float32), PRICE_START)
    m = int(1.2 * sr)
    tt = np.arange(m) / sr
    ding = (np.sin(2 * np.pi * 1568 * tt) + 0.6 * np.sin(2 * np.pi * 2349 * tt)
            + 0.3 * np.sin(2 * np.pi * 3136 * tt)) * np.exp(-tt * 4.5) * 0.18
    add(ding.astype(np.float32), PRICE_START + 0.02)

    # soft pop for the CTA pill
    m = int(0.12 * sr)
    tt = np.arange(m) / sr
    pop = np.sin(2 * np.pi * (600 * tt + 2500 * tt ** 2)) * np.exp(-tt * 40) * 0.3
    add(pop.astype(np.float32), CTA_START + 0.12)

    out = np.clip(out, -1, 1)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((out * 32767).astype(np.int16).tobytes())


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--music", required=True)
    ap.add_argument("--font", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sfx", default="/tmp/poji_sfx.wav")
    ap.add_argument("--preview", action="store_true", help="half resolution, fast encode")
    args = ap.parse_args()

    s = 0.5 if args.preview else 1.0
    W, H = int(W_FULL * s), int(H_FULL * s)
    layers = build_layers(args.font, s, W, H)
    make_sfx(args.sfx)

    dec = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", args.raw, "-t", str(DURATION), "-vf", f"scale={W}:{H}",
         "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        stdout=subprocess.PIPE)

    music_filter = (
        f"[2:a]atrim=start={MUSIC_START}:duration={DURATION},asetpts=PTS-STARTPTS,"
        "aresample=48000,loudnorm=I=-26:TP=-6:LRA=11,aresample=48000,"
        f"afade=t=in:d=0.4,afade=t=out:st={DURATION - 1.2}:d=1.2,apad[mus];"
    )
    # loudnorm resamples internally; re-resample + apad so sidechaincompress/amix
    # don't end the mix ~3 s early. Final length is fixed by -t.
    filt = (
        "[1:a]aresample=48000,highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,"
        "loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000,apad,asplit=2[vo][key];"
        + music_filter +
        "[mus][key]sidechaincompress=threshold=0.04:ratio=5:attack=30:release=400[duck];"
        "[3:a]aresample=48000,volume=0.9,apad[sfx];"
        f"[vo][duck][sfx]amix=inputs=3:normalize=0:duration=first,atrim=0:{DURATION},"
        "alimiter=limit=0.95,apad[aout]"
    )
    venc = (["-c:v", "libx264", "-preset", "veryfast", "-crf", "26"] if args.preview
            else ["-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high"])
    # inputs: 0 = rendered frames (pipe), 1 = raw (voice), 2 = music, 3 = sfx
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-i", args.raw, "-i", args.music, "-i", args.sfx,
         "-filter_complex", filt,
         "-map", "0:v", "-map", "[aout]", *venc, "-pix_fmt", "yuv420p",
         "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", str(DURATION), args.out],
        stdin=subprocess.PIPE)

    frame_bytes = W * H * 3
    i = 0
    while True:
        buf = dec.stdout.read(frame_bytes)
        if len(buf) < frame_bytes:
            break
        t = i / FPS
        src = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        z = zoom_at(t)
        sx, sy = shake_at(t, s)
        M = np.float32([[z, 0, (1 - z) * W / 2 + sx], [0, z, (1 - z) * H / 2 + sy]])
        frame = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LINEAR,
                               borderMode=cv2.BORDER_REFLECT).astype(np.float32)
        for L in layers:
            if L.active(t):
                L.draw(frame, t)
        f = flash_at(t)
        if f > 0:
            frame = frame * (1 - f) + 255 * f
        enc.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
        i += 1
        if i % 300 == 0:
            print(f"  {i} frames ({t:.1f}s)", flush=True)
    enc.stdin.close()
    enc.wait()
    dec.wait()
    print(f"done: {i} frames -> {args.out}")


if __name__ == "__main__":
    main()
