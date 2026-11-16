"""Reusable renderer for the neon-explainer car videos (110 BPM).

A project module describes one video (voiceover, captions, neon scenes, footage
shots, chips, CTA, SFX); this engine turns it into a storyboard or an mp4.

Look: black bg, #39FF14 glowing line art, Formula1 captions with green keywords,
ring reveal into tone-mapped iPhone HLG footage cut every 2 beats, KOMEN "NAK" CTA,
classical bed time-stretched to 110 BPM + soft kick/shaker pulse layer.
"""
import math
import os
import subprocess
import wave
from dataclasses import dataclass, field

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from neon_scenes import GREEN_T, H, W, Neon, Typo, background, clamp, ease, ease_io, glow

FPS = 30
BPM = 110.0
BEAT = 60.0 / BPM

TONEMAP = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,"
           "tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,"
           "eq=contrast=1.08:saturation=1.18:brightness=0.015")


# ---------------------------------------------------------------------------
# timing helpers
# ---------------------------------------------------------------------------
def sec(lt, a, b):
    return clamp((lt - a) / (b - a)) if b > a else float(lt >= a)


def snap(t):
    return round(t / BEAT) * BEAT


def bt(b):
    return b * BEAT


def ev(lt, t, a, d):
    """progress 0..1 of an event at local time a (snapped to the beat grid), length d."""
    st = t - lt
    s0 = snap(st + a) - st
    return sec(lt, s0, s0 + d)


def beat_pulse(t, down=0.38, other=0.16, decay=0.12):
    k = math.floor(t / BEAT + 1e-6)
    dt = t - k * BEAT
    return (down if k % 4 == 0 else other) * math.exp(-dt / decay)


def count_up(lt, t, a, d, v0, v1):
    """eased number count-up starting on the beat nearest local time a."""
    return v0 + (v1 - v0) * ease(ev(lt, t, a, d))


@dataclass
class Project:
    assets: str
    duration: float
    vo: str
    header_label: str
    header_title: str
    captions: list            # (start, end, "text with *keywords*")
    anim: list                # (start, end, fn(lt, t) -> (bg_rgb, Neon))
    ring: tuple               # (start_beat, end_beat)
    foot: list                # (clip, b0, b1, src_offset, zoom, cx, cy)
    clip_dur: dict
    chips: list               # (text, b0, b1)
    cta_beat: int
    sfx: list = field(default_factory=list)   # (kind, t) kinds: thud, shimmer, pop, coin
    music: str = "Music/v24044gl0000cthro1vog65gunpi1teg.mp4"
    music_start: float = 141.434   # first beat of the chosen passage
    music_src_bpm: float = 97.36
    font: str = "Font Type/Formula1-Bold_web_0.ttf"
    xfade: float = 0.45


# ---------------------------------------------------------------------------
# footage
# ---------------------------------------------------------------------------
class ClipReader:
    def __init__(self, path, src_dur, slot, offset=0.0):
        src = src_dur - offset
        self.speed = min(1.0, (src - 0.05) / slot)
        vf = (f"{TONEMAP},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
              f"setpts=(PTS-STARTPTS)/{self.speed:.4f},fps={FPS}")
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{offset:.3f}", "-i", path,
                                   "-an", "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                  stdout=subprocess.PIPE)
        self.idx, self.last = -1, None

    def frame(self, lt):
        want = max(0, int(lt * FPS + 1e-6))
        while self.idx < want:
            buf = self.p.stdout.read(W * H * 3)
            if len(buf) < W * H * 3:
                break
            self.last = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
            self.idx += 1
        return self.last

    def close(self):
        self.p.kill()


def push(img, z, cx=0.5, cy=0.5):
    if abs(z - 1) < 1e-4:
        return img.astype(np.float32)
    px = clamp(cx, 0.5 / z, 1 - 0.5 / z) * W
    py = clamp(cy, 0.5 / z, 1 - 0.5 / z) * H
    M = np.float32([[z, 0, W / 2 - z * px], [0, z, H / 2 - z * py]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR).astype(np.float32)


_SHADE = {}


def shade(img):
    if "s" not in _SHADE:
        yy = np.linspace(0, 1, H)[:, None, None]
        s = np.clip((yy - 0.52) / 0.38, 0, 1) ** 1.2 * 0.75 + np.clip((0.18 - yy) / 0.18, 0, 1) * 0.35
        _SHADE["s"] = (1 - s).astype(np.float32)
    return img * _SHADE["s"]


# ---------------------------------------------------------------------------
# text layer
# ---------------------------------------------------------------------------
def parse(text):
    words, hl = [], False
    for tok in text.split():
        if tok.startswith("*"):
            hl, tok = True, tok[1:]
        end = "*" in tok
        words.append((tok.replace("*", ""), hl))
        if end:
            hl = False
    return words


def caption(d, typo, text, a, dy=0, size=54, y=1395):
    f = typo.font(size)
    words = parse(text)
    space = d.textlength(" ", font=f)

    def width(ws):
        return sum(d.textlength(w, font=f) for w, _ in ws) + space * (len(ws) - 1)

    if width(words) <= 900 or len(words) < 2:
        lines = [(words, width(words))]
    else:
        k = min(range(1, len(words)), key=lambda k: max(width(words[:k]), width(words[k:])))
        lines = [(words[:k], width(words[:k])), (words[k:], width(words[k:]))]
    lh = int(size * 1.32)
    y0 = y - len(lines) * lh / 2 + dy
    for i, (ln, lw) in enumerate(lines):
        x = (W - lw) / 2
        for w, h_ in ln:
            col = GREEN_T if h_ else (255, 255, 255)
            d.text((x + 2, y0 + i * lh + 4), w, font=f, fill=(0, 0, 0, int(a * 0.55)))
            d.text((x, y0 + i * lh), w, font=f, fill=col + (a,), stroke_width=3,
                   stroke_fill=(0, 0, 0, int(a * 0.8)))
            x += d.textlength(w, font=f) + space


def header(d, typo, a, label, title):
    f1, f2 = typo.font(30), typo.font(58)
    lab = " ".join(label)
    w1 = d.textlength(lab, font=f1)
    d.text(((W - w1) / 2, 250), lab, font=f1, fill=GREEN_T + (a,))
    w2 = d.textlength(title, font=f2)
    d.text(((W - w2) / 2, 298), title, font=f2, fill=(255, 255, 255, a))
    cy = 400
    d.line([(W / 2 - 150, cy), (W / 2 - 34, cy)], fill=(255, 255, 255, a // 2), width=2)
    d.line([(W / 2 + 34, cy), (W / 2 + 150, cy)], fill=(255, 255, 255, a // 2), width=2)
    d.rounded_rectangle([W / 2 - 22, cy - 5, W / 2 + 22, cy + 5], radius=5, fill=GREEN_T + (a,))


def chip(d, typo, text, a, sc, y=1520):
    f = typo.font(max(8, int(44 * sc)))
    tw = d.textlength(text, font=f)
    w, h = tw + 64 * sc, 84 * sc
    x0, y0 = W / 2 - w / 2, y + (84 - h) / 2
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=h / 2, fill=(10, 10, 10, int(a * 0.85)),
                        outline=GREEN_T + (a,), width=max(2, int(4 * sc)))
    d.text((W / 2 - tw / 2, y0 + 16 * sc), text, font=f, fill=(255, 255, 255, a))


def cta(d, typo, a, sc):
    txt = 'KOMEN "NAK"'
    f = typo.font(max(8, int(60 * sc)))
    tw = d.textlength(txt, font=f)
    bw, bh = tw + 120 * sc, 118 * sc
    cy = 1560
    d.rounded_rectangle([W / 2 - bw / 2, cy - bh / 2, W / 2 + bw / 2, cy + bh / 2], radius=bh / 2,
                        fill=GREEN_T + (a,))
    d.text((W / 2 - tw / 2, cy - 36 * sc), txt, font=f, fill=(10, 10, 10, a))
    f2 = typo.font(34)
    sub = "SAYA DM KORANG"
    w2 = d.textlength(sub, font=f2)
    d.text((W / 2 - w2 / 2, cy + 82), sub, font=f2, fill=(255, 255, 255, a))


def pop(dt, dur=0.22, k=1.8):
    if dt >= dur:
        return 1.0
    x = dt / dur - 1
    return 0.5 + 0.5 * (1 + (k + 1) * x ** 3 + k * x ** 2)


# ---------------------------------------------------------------------------
# renderer
# ---------------------------------------------------------------------------
class Renderer:
    def __init__(self, P: Project):
        self.P = P
        self.typo = Typo(os.path.join(P.assets, P.font))
        self.readers = {}
        self.txt_cache = {}
        self.ring_start, self.ring_end = bt(P.ring[0]), bt(P.ring[1])
        self.cta_t = bt(P.cta_beat)

    # --- neon section
    def neon(self, t):
        P, X = self.P, self.P.xfade
        active = [(st, en, fn) for st, en, fn in P.anim if st - X / 2 <= t < en + X / 2]
        if len(active) == 1:
            st, _, fn = active[0]
            f, n = fn(t - st, t)
            return f, n.mask()
        (s1, _, f1), (s2, _, f2) = active[:2]
        x = sec(t, s2 - X / 2, s2 + X / 2)
        if x < 0.5:
            f, n = f1(t - s1, t)
            k = ease_io(1 - 2 * x)
        else:
            f, n = f2(t - s2, t)
            k = ease_io(2 * x - 1)
        bg = background()
        return bg + (f - bg) * k, n.mask() * k

    # --- footage section
    def reader(self, i):
        if i not in self.readers:
            clip, b0, b1, off = self.P.foot[i][:4]
            self.readers[i] = ClipReader(os.path.join(self.P.assets, "Raw Video", clip + ".MOV"),
                                         self.P.clip_dur[clip], bt(b1) - bt(b0), off)
        return self.readers[i]

    def footage(self, t):
        foot = self.P.foot
        i = next((k for k, f in enumerate(foot) if bt(f[1]) <= t + 1e-6 < bt(f[2])), len(foot) - 1)
        _, b0, b1, _, z0, cx, cy = foot[i]
        st, en = bt(b0), bt(b1)
        punch = 0.06 * (1 - ease(sec(t, st, st + 0.2))) if i > 0 else 0.0
        z = z0 * (1.0 + 0.03 * sec(t, st, en) + punch + 0.05 * beat_pulse(t))
        img = push(self.reader(i).frame(t - st), z, cx, cy)
        if t >= self.cta_t - 0.3:  # dim slightly under the CTA button
            img = img * (1 - 0.18 * sec(t, self.cta_t - 0.3, self.cta_t + 0.3))
        return img

    # --- text
    def text_layer(self, t):
        P = self.P
        items = []
        ha = 1 - sec(t, self.ring_start, self.ring_start + 0.45)
        if ha > 0:
            items.append(("h", round(ha, 2)))
        for i, (st, en, _) in enumerate(P.captions):
            if st <= t < en:
                a = sec(t, st, st + 0.18) * (1 - sec(t, en - 0.1, en))
                items.append(("c", i, round(a, 2), round((1 - ease(sec(t, st, st + 0.25))) * 18)))
        for txt, b0, b1 in P.chips:
            cs, en = bt(b0), bt(b1)
            if cs <= t < en:
                items.append(("chip", txt, round(sec(t, cs, cs + 0.08), 2),
                              round(pop(t - cs, 0.18) * (1 + 0.25 * beat_pulse(t)), 2)))
        if t >= self.cta_t:
            pul = 1 + 0.25 * beat_pulse(t) if t > self.cta_t + 0.3 else 1
            items.append(("cta", round(sec(t, self.cta_t, self.cta_t + 0.1), 2),
                          round(pop(t - self.cta_t, 0.3) * pul, 3)))
        key = tuple(items)
        if key in self.txt_cache:
            return self.txt_cache[key]
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        for it in items:
            if it[0] == "h":
                header(d, self.typo, int(255 * it[1]), P.header_label, P.header_title)
            elif it[0] == "c":
                caption(d, self.typo, P.captions[it[1]][2], int(255 * it[2]), dy=it[3])
            elif it[0] == "chip":
                chip(d, self.typo, it[1], int(255 * it[2]), it[3])
            elif it[0] == "cta":
                cta(d, self.typo, int(255 * it[1]), it[2])
        arr = np.asarray(img).astype(np.float32)
        val = (arr[..., :3], arr[..., 3:4] / 255.0)
        if len(self.txt_cache) > 64:
            self.txt_cache.clear()
        self.txt_cache[key] = val
        return val

    def frame(self, t):
        mask = None
        if t < self.ring_start:
            base, mask = self.neon(t)
        elif t < self.ring_end:
            p = sec(t, self.ring_start, self.ring_end)
            bg, mask = self.neon(t)
            fo = shade(self.footage(t))
            r = 40 + ease_io(p) * 1150
            m = np.zeros((H, W), np.float32)
            cv2.circle(m, (W // 2, int(H * 0.48)), int(r), 1.0, -1, cv2.LINE_AA)
            m = m[..., None]
            base = fo * m + bg * (1 - m)
            ring = Neon()
            ring.c.arc(W / 2, H * 0.48, r, 0, 2 * math.pi)
            ring.stroke(1.0 - 0.7 * p, 8)
            mask = mask * (1 - m[..., 0]) + ring.mask()
        else:
            base = shade(self.footage(t))
        out = base + glow(mask * (1 + beat_pulse(t))) if mask is not None else base
        out = np.clip(out, 0, 255)
        trgb, ta = self.text_layer(t)
        return (trgb * ta + out * (1 - ta)).astype(np.uint8)

    def close(self):
        for r in self.readers.values():
            r.close()


# ---------------------------------------------------------------------------
# audio
# ---------------------------------------------------------------------------
def make_sfx(P: Project, path, sr=48000):
    n = int((P.duration + 1) * sr)
    out = np.zeros(n, np.float32)
    rng = np.random.default_rng(5)

    def add(sig, t):
        i = int(t * sr)
        j = min(n, i + len(sig))
        if 0 <= i < n:
            out[i:j] += sig[: j - i].astype(np.float32)

    # 110 BPM pulse layer
    tt = np.arange(int(0.28 * sr)) / sr
    kick = np.sin(2 * np.pi * (48 * tt + 90 * (1 - np.exp(-tt * 30)) / 30)) * np.exp(-tt * 14)
    m = int(0.05 * sr)
    shaker = rng.standard_normal(m)
    shaker = np.diff(shaker, prepend=0) * np.exp(-np.arange(m) / sr * 70)
    for k in range(int(P.duration / BEAT)):
        tb = bt(k)
        if tb > P.duration - 1.2:
            break
        add(kick * (0.30 if k % 4 == 0 else 0.20), tb)
        add(shaker * 0.035, tb + BEAT / 2)

    for kind, t in P.sfx:
        if kind == "thud":
            tt = np.arange(int(0.6 * sr)) / sr
            add(np.sin(2 * np.pi * (70 * tt - 25 * tt ** 2)) * np.exp(-tt * 7) * 0.5, t)
        elif kind == "shimmer":
            m = int(0.9 * sr)
            noise = np.convolve(rng.standard_normal(m), np.ones(6) / 6, mode="same")
            x = np.linspace(0, 1, m)
            tt = np.arange(m) / sr
            chime = sum(np.sin(2 * np.pi * f * tt) for f in (1318.5, 1975.5, 2637)) / 3
            add((noise * 0.08 + chime * 0.12) * np.sin(np.pi * x) ** 2, t - 0.1)
        elif kind == "pop":
            tt = np.arange(int(0.15 * sr)) / sr
            add(np.sin(2 * np.pi * (520 * tt + 2200 * tt ** 2)) * np.exp(-tt * 30) * 0.3, t)
        elif kind == "coin":
            tt = np.arange(int(0.35 * sr)) / sr
            add((np.sin(2 * np.pi * 2093 * tt) + 0.5 * np.sin(2 * np.pi * 3136 * tt))
                * np.exp(-tt * 12) * 0.10, t)
    out = np.clip(out, -1, 1)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((out * 32767).astype(np.int16).tobytes())


def audio_filter(P: Project):
    ratio = BPM / P.music_src_bpm
    D = P.duration
    return (
        "[1:a]aresample=48000,highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,"
        "loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000,apad,asplit=2[vo][key];"
        f"[2:a]atrim=start={P.music_start}:duration={D * ratio + 1:.3f},"
        f"asetpts=PTS-STARTPTS,aresample=48000,rubberband=tempo={ratio:.5f}:transients=crisp,"
        f"atrim=0:{D},loudnorm=I=-24:TP=-6:LRA=11,aresample=48000,"
        f"afade=t=in:d=0.3,afade=t=out:st={D - 1.5}:d=1.5,apad[mus];"
        "[mus][key]sidechaincompress=threshold=0.05:ratio=3:attack=40:release=500[duck];"
        "[3:a]aresample=48000,apad[sfx];"
        f"[vo][duck][sfx]amix=inputs=3:normalize=0:duration=first,atrim=0:{D},"
        "volume=4.2dB,aresample=192000,alimiter=limit=0.79:attack=2:release=60:level=false,"
        "aresample=48000,apad[aout]"
    )


def render(P: Project, out, preview, sfx_path):
    make_sfx(P, sfx_path)
    R = Renderer(P)
    ow, oh = (540, 960) if preview else (W, H)
    venc = (["-c:v", "libx264", "-preset", "veryfast", "-crf", "24"] if preview
            else ["-c:v", "libx264", "-preset", "slow", "-crf", "16", "-profile:v", "high"])
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-i", os.path.join(P.assets, P.vo), "-i", os.path.join(P.assets, P.music), "-i", sfx_path,
         "-filter_complex", audio_filter(P) + f";[0:v]scale={ow}:{oh}:flags=lanczos[v]",
         "-map", "[v]", "-map", "[aout]", *venc, "-pix_fmt", "yuv420p",
         "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", str(P.duration), out],
        stdin=subprocess.PIPE)
    nframes = int(round(P.duration * FPS))
    for i in range(nframes):
        enc.stdin.write(R.frame(i / FPS).tobytes())
        if i % 150 == 0:
            print(f"  {i}/{nframes}", flush=True)
    enc.stdin.close()
    enc.wait()
    R.close()
    print("done ->", out)


def storyboard(P: Project, times, outdir):
    """times: list of (t, name, note), must be in increasing t (footage streams forward)."""
    os.makedirs(outdir, exist_ok=True)
    R = Renderer(P)
    shots = []
    for t, name, note in times:
        img = R.frame(t)
        Image.fromarray(img).save(os.path.join(outdir, name.replace(" ", "_").lower() + ".png"))
        shots.append((name, note, img))
    R.close()
    font = os.path.join(P.assets, P.font)
    tw, th, cols = 300, 533, 7
    rows = math.ceil(len(shots) / cols)
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * 14, rows * (th + 78) + 14), (22, 22, 22))
    d = ImageDraw.Draw(sheet)
    f1, f2 = ImageFont.truetype(font, 22), ImageFont.truetype(font, 17)
    for i, (name, note, img) in enumerate(shots):
        r, c = divmod(i, cols)
        x, y = 14 + c * (tw + 14), 14 + r * (th + 78)
        d.text((x, y + 4), name, font=f1, fill=GREEN_T)
        d.text((x, y + 36), note, font=f2, fill=(190, 190, 190))
        sheet.paste(Image.fromarray(img).resize((tw, th), Image.LANCZOS), (x, y + 66))
    sheet.save(os.path.join(outdir, "storyboard_sheet.jpg"), quality=92)
    print("storyboard ->", outdir)
