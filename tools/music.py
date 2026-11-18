"""Penjana muzik + SFX asli (sintesis numpy), dikunci pada BPM timeline.

Guna:  python3 tools/music.py projects/durian
Keluaran: <proj>/build/music.wav, <proj>/build/sfx.wav
"""
import json
import sys
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
RNG = np.random.default_rng(7)


# ---------------------------------------------------------------- util
def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def n(name):
    """'C4' / 'Bb3' / 'F#5' -> midi"""
    base = NOTE[name[0]]
    rest = name[1:]
    if rest[0] == "b":
        base -= 1
        rest = rest[1:]
    elif rest[0] == "#":
        base += 1
        rest = rest[1:]
    return base + 12 * (int(rest) + 1)


def tvec(dur):
    return np.arange(int(dur * SR)) / SR


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, btype="low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, btype="high", fs=SR, output="sos"), x)


def add(buf, sig, t0, gain=1.0):
    i = int(round(t0 * SR))
    if i >= len(buf) or i + len(sig) <= 0:
        return
    if i < 0:
        sig = sig[-i:]
        i = 0
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


def env_ad(n_samp, a=0.005, d=0.2):
    t = np.arange(n_samp) / SR
    e = np.exp(-t / d)
    na = max(1, int(a * SR))
    e[:na] *= np.linspace(0, 1, na)
    return e


def fade_tail(sig, ms=10):
    k = min(len(sig), int(ms / 1000 * SR))
    sig[-k:] *= np.linspace(1, 0, k)
    return sig


def reverb(x, secs=1.6, mix=0.2, damp=4000):
    t = tvec(secs)
    ir = RNG.standard_normal(len(t)) * np.exp(-t / (secs / 5))
    ir = lp(ir, damp)
    ir /= np.sqrt(np.sum(ir ** 2))
    wet = fftconvolve(x, ir)[: len(x)]
    return x * (1 - mix) + wet * mix * 0.9


# ---------------------------------------------------------------- instrumen
def marimba(f, dur=0.6, vel=1.0):
    t = tvec(dur)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.28)
    s += 0.35 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t / 0.05)
    s += 0.12 * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t / 0.015)
    na = int(0.002 * SR)
    s[:na] *= np.linspace(0, 1, na)
    return fade_tail(s * vel)


def bell(f, dur=1.4, vel=1.0, idx=2.2):
    t = tvec(dur)
    mod = idx * np.exp(-t / 0.25) * np.sin(2 * np.pi * f * 3.5 * t)
    s = np.sin(2 * np.pi * f * t + mod) * np.exp(-t / 0.55)
    s += 0.25 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t / 0.3)
    na = int(0.003 * SR)
    s[:na] *= np.linspace(0, 1, na)
    return fade_tail(s * vel)


def bass(f, dur, vel=1.0):
    t = tvec(dur + 0.05)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.12 * np.sin(2 * np.pi * 3 * f * t)
    s = np.tanh(1.6 * s) / np.tanh(1.6)
    e = np.ones_like(t)
    na, nr = int(0.006 * SR), int(0.05 * SR)
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] = np.linspace(1, 0, nr)
    e *= np.exp(-t / (dur * 2.5))
    return s * e * vel


def pad(freqs, dur, vel=1.0):
    t = tvec(dur)
    s = np.zeros_like(t)
    for f in freqs:
        for det in (-0.12, 0.0, 0.11):
            ff = f * 2 ** (det / 12)
            ph = RNG.uniform(0, 1)
            s += 2 * ((ff * t + ph) % 1.0) - 1
    s = lp(s / (len(freqs) * 3), 1400, 2)
    e = np.ones_like(t)
    na, nr = int(0.6 * SR), int(0.8 * SR)
    e[:na] = np.linspace(0, 1, na) ** 2
    e[-nr:] *= np.linspace(1, 0, nr)
    return s * e * vel


def kick(vel=1.0):
    t = tvec(0.35)
    f = 48 + 90 * np.exp(-t / 0.03)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t / 0.16)
    s += 0.3 * RNG.standard_normal(len(t)) * np.exp(-t / 0.004)
    return fade_tail(np.tanh(1.5 * s) * vel)


def clap(vel=1.0):
    t = tvec(0.3)
    nz = RNG.standard_normal(len(t))
    e = np.exp(-t / 0.09)
    for off in (0.0, 0.011, 0.022):  # tepukan berlapis
        k = int(off * SR)
        e[k:k + int(0.006 * SR)] += 0.8
    s = bp(nz, 900, 3500) * e
    return fade_tail(s * vel * 1.4)


def hat(vel=1.0, open_=False):
    t = tvec(0.25 if open_ else 0.06)
    s = hp(RNG.standard_normal(len(t)), 7000) * np.exp(-t / (0.09 if open_ else 0.018))
    return fade_tail(s * vel)


def kompang(vel=1.0, high=False):
    """pukulan gendang bingkai: 'tung' (rendah) / 'pak' (tinggi)"""
    t = tvec(0.25)
    if high:
        s = bp(RNG.standard_normal(len(t)), 1200, 4000) * np.exp(-t / 0.025)
        s += 0.4 * np.sin(2 * np.pi * 420 * t) * np.exp(-t / 0.04)
    else:
        f = 150 + 70 * np.exp(-t / 0.02)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.13)
        s += 0.3 * bp(RNG.standard_normal(len(t)), 600, 2000) * np.exp(-t / 0.01)
    return fade_tail(s * vel)


def crash(vel=1.0):
    t = tvec(2.2)
    s = hp(RNG.standard_normal(len(t)), 4500) * np.exp(-t / 0.7)
    return fade_tail(s * vel * 0.5, 200)


def woodtick(vel=1.0):
    t = tvec(0.08)
    s = np.sin(2 * np.pi * 1800 * t) * np.exp(-t / 0.012)
    return fade_tail(s * vel)


def riser(dur, vel=1.0):
    t = tvec(dur)
    nz = RNG.standard_normal(len(t))
    out = np.zeros_like(t)
    seg = int(0.05 * SR)
    for i in range(0, len(t), seg):
        frac = i / len(t)
        fc = 400 + 6000 * frac ** 2
        chunk = nz[i:i + seg + 2000]
        f = bp(chunk, fc * 0.7, min(fc * 1.4, 18000))[: min(seg, len(t) - i)]
        out[i:i + len(f)] = f
    e = (t / dur) ** 2
    return out * e * vel


# ---------------------------------------------------------------- muzik
CHORDS = {
    "Fmaj7": ["F3", "A3", "C4", "E4"], "G6": ["G3", "B3", "D4", "E4"],
    "Em7": ["E3", "G3", "B3", "D4"], "Am7": ["A3", "C4", "E4", "G4"],
    "Dm7": ["D3", "F3", "A3", "C4"], "Bbmaj7": ["Bb2", "D3", "F3", "A3"],
    "E7": ["E3", "G#3", "B3", "D4"], "Cadd9": ["C3", "G3", "D4", "E4"],
    "G": ["G3", "B3", "D4", "G4"], "F": ["F3", "A3", "C4", "F4"],
}
ROOT = {"Fmaj7": "F2", "G6": "G2", "Em7": "E2", "Am7": "A2", "Dm7": "D2", "Bbmaj7": "Bb1",
        "E7": "E2", "Cadd9": "C2", "G": "G2", "F": "F2"}
LOOP = ["Fmaj7", "G6", "Em7", "Am7"]

MELODY = {  # bar: [(beat, nota, panjang beat)]
    18: [(0, "E5", 1), (1, "C5", .5), (1.5, "D5", .5), (2, "E5", 1), (3, "G5", 1)],
    19: [(0, "D5", 1.5), (1.5, "B4", .5), (2, "D5", .5), (2.5, "E5", 1.5)],
    20: [(0, "B4", 1), (1, "G4", .5), (1.5, "A4", .5), (2, "B4", 1), (3, "D5", 1)],
    21: [(0, "C5", 1.5), (1.5, "A4", .5), (2, "G4", .5), (2.5, "A4", 1.5)],
    22: [(0, "E5", .5), (0.5, "F5", .5), (1, "A5", 1), (2, "G5", 1), (3, "E5", 1)],
    23: [(0, "D5", 1), (1, "G5", 1), (2, "F5", .5), (2.5, "D5", .5), (3, "B4", 1)],
}
JINGLE = [(0, "E5", .5), (0.5, "G5", .5), (1, "C6", 1.5)]  # logo bunyi "Se-bab A-pa?"


def chord_for_bar(bar):
    if 14 <= bar <= 17:
        return ["Dm7", "Dm7", "Bbmaj7", "E7"][bar - 14]
    if bar == 22:
        return "F"
    if bar == 23:
        return "G"
    if bar >= 24:
        return "Cadd9"
    return LOOP[bar % 4]


def build_music(tl):
    bpm = tl["bpm"]
    B = 60.0 / bpm
    total = tl["totalBeats"] * B + tl["tailSeconds"] + 2.0
    L = int(total * SR)
    drums = np.zeros(L)
    keys = np.zeros(L)
    bassb = np.zeros(L)
    padb = np.zeros(L)
    lead = np.zeros(L)
    kick_env = np.zeros(L)
    swing = 0.06 * B  # sedikit swing pada 8th lewat
    nbars = tl["totalBeats"] // 4

    def at(bar, beat):
        b = bar * 4 + beat
        if (beat * 2) % 2 == 1:  # 8th offbeat
            return b * B + swing
        return b * B

    for bar in range(nbars + 1):
        ch = chord_for_bar(bar)
        notes = [mtof(n(x)) for x in CHORDS[ch]]
        root = mtof(n(ROOT[ch]))
        brk = 14 <= bar <= 17
        intro = bar < 2
        final = bar >= 24

        if final:
            # pukulan akhir
            add(drums, kick(1.0), at(bar, 0))
            add(drums, crash(0.9), at(bar, 0))
            add(bassb, bass(root, 2.5 * B * 4 / 4, 0.9), at(bar, 0))
            for k, f in enumerate(notes + [notes[-1] * 2]):
                add(keys, marimba(f, 2.0, 0.45), at(bar, 0) + k * 0.025)
            for bt, nm, d in JINGLE:
                add(lead, bell(mtof(n(nm)), 1.8, 0.55), at(bar, bt))
            add(padb, pad([f * 2 for f in notes], 4 * B + 1.5, 0.35), at(bar, 0))
            break

        # ---- keys: arpeggio marimba 8th
        if not brk:
            pattern = [0, 2, 1, 3, 2, 1, 3, 2]
            for i, pi in enumerate(pattern):
                f = notes[pi] * 2
                vel = 0.55 if i % 2 == 0 else 0.38
                if intro and i % 2 == 1:
                    vel *= 0.6
                add(keys, marimba(f, 0.6, vel), at(bar, i * 0.5))
        else:
            add(padb, pad(notes, 4 * B + 0.6, 0.55), at(bar, 0))
            # tik-tok saspens
            for i in range(4):
                add(drums, woodtick(0.18 if i % 2 else 0.25), at(bar, i))
            if bar in (14, 16):
                add(lead, bell(mtof(n("A5")), 2.5, 0.22, idx=1.2), at(bar, 0))
            if bar == 15:
                add(lead, bell(mtof(n("F5")), 2.5, 0.2, idx=1.2), at(bar, 0))
            if bar == 17:
                add(lead, bell(mtof(n("G#5")), 2.5, 0.22, idx=1.2), at(bar, 0))

        # ---- bass
        if brk:
            add(bassb, bass(root, 4 * B + 0.04, 0.42), at(bar, 0))
            # degup jantung
            for bt in (0, 0.5) if bar < 17 else (0, 0.5, 2, 2.5):
                add(drums, kick(0.55), at(bar, bt))
                add(kick_env, np.exp(-tvec(0.25) / 0.08), at(bar, bt))
        else:
            fifth = root * 1.5
            pat = [(0, root, .9), (1.5, root, .45), (2.5, fifth, .45), (3, root * 2, .45), (3.5, root, .4)]
            if intro:
                pat = [(0, root, 1.8), (2.5, fifth, .45), (3, root, .9)]
            for bt, f, d in pat:
                add(bassb, bass(f, d * B, 0.8), at(bar, bt))

        # ---- dram
        if not brk:
            kpos = [0, 2, 2.75] if not intro else [0, 2]
            for bt in kpos:
                add(drums, kick(0.95 if bt in (0, 2) else 0.6), at(bar, bt))
                add(kick_env, np.exp(-tvec(0.25) / 0.08), at(bar, bt))
            if not intro:
                for bt in (1, 3):
                    add(drums, clap(0.55), at(bar, bt))
            for i in range(8):
                v = 0.10 if i % 2 == 0 else 0.17
                if intro:
                    v *= 0.6
                add(drums, hat(v), at(bar, i * 0.5))
            if not intro:
                # kompang: corak tung–pak berselang
                for bt, hi, v in [(0.75, False, .35), (1.5, True, .22), (2.5, False, .28), (3.25, True, .2), (3.75, True, .15)]:
                    add(drums, kompang(v, hi), at(bar, bt))
            if bar % 4 == 3 and bar not in (13,):
                add(drums, hat(0.18, True), at(bar, 3.5))

        # ---- melodi (bahagian kedua)
        if bar in MELODY:
            for bt, nm, d in MELODY[bar]:
                add(lead, bell(mtof(n(nm)), max(0.6, d * B * 2), 0.42), at(bar, bt))

        # ---- jingle logo di awal
        if bar == 0:
            for bt, nm, d in JINGLE:
                add(lead, bell(mtof(n(nm)), 1.4, 0.4), at(0, bt))

    # crash pada titik penting
    for bar in (2, 8, 18):
        add(drums, crash(0.55 if bar != 18 else 0.8), bar * 4 * B)
    # gulungan snare + riser masuk bar 18
    roll0 = (17 * 4 + 2) * B
    for i in range(16):
        add(drums, clap(0.15 + 0.5 * i / 16), roll0 + i * B / 8)
    add(drums, riser(2 * B, 0.35), roll0)

    # sidechain ringan pada keys/pad
    duck = 1 - 0.35 * np.clip(kick_env, 0, 1)
    keys *= duck
    padb *= 1 - 0.5 * np.clip(kick_env, 0, 1)

    keys = reverb(keys, 1.4, 0.22)
    lead = reverb(lead, 2.0, 0.3)
    padb = reverb(padb, 2.4, 0.3)
    drums = drums + 0.12 * reverb(hp(drums, 300), 1.0, 1.0)
    bassb = lp(bassb, 900)

    drums = hp(drums, 32)
    mix = 0.95 * drums + 0.8 * keys + 0.9 * bassb + 0.7 * padb + 0.75 * lead
    # stereo ringkas: keys sedikit kiri, lead sedikit kanan, + haas kecil
    d = int(0.012 * SR)
    left = mix + 0.12 * keys - 0.08 * lead
    right = mix - 0.12 * keys + 0.08 * lead
    right = np.concatenate([np.zeros(d), right[:-d]]) * 0.15 + right * 0.85
    left, right = hp(left, 30), hp(right, 30)
    st = np.stack([left, right], 1)
    # fade akhir
    end = int((tl["totalBeats"] * B + tl["tailSeconds"]) * SR)
    st = st[:end]
    nf = int(1.2 * SR)
    st[-nf:] *= np.linspace(1, 0, nf)[:, None]
    st = np.tanh(st / np.max(np.abs(st)) * 1.3) / np.tanh(1.3)
    return st * 0.89


# ---------------------------------------------------------------- SFX
def sfx_sound(kind, B):
    t = None
    if kind == "pop":
        t = tvec(0.12)
        f = 420 + 900 * (t / 0.12)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.035)
        return s * 0.55
    if kind == "bubble":
        t = tvec(0.15)
        f = 600 + 1400 * (t / 0.15) ** 0.5
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.04) * 0.35
    if kind == "boing":
        t = tvec(0.45)
        f = 220 + 80 * np.sin(2 * np.pi * 14 * t) * np.exp(-t / 0.2) + 150 * t
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.15) * 0.5
    if kind in ("whoosh", "swish"):
        dur = 0.55 if kind == "whoosh" else 0.3
        t = tvec(dur)
        nz = RNG.standard_normal(len(t))
        out = np.zeros_like(t)
        seg = int(0.02 * SR)
        for i in range(0, len(t), seg):
            fr = i / len(t)
            fc = 300 + 3500 * np.sin(np.pi * fr)
            ch = bp(nz[i:i + seg + 1500], fc * 0.6, fc * 1.6)[: min(seg, len(t) - i)]
            out[i:i + len(ch)] = ch
        e = np.sin(np.pi * t / dur) ** 2
        return out * e * (0.9 if kind == "whoosh" else 0.5)
    if kind == "crack":
        t = tvec(0.3)
        s = hp(RNG.standard_normal(len(t)), 1500) * np.exp(-t / 0.03)
        s += 0.6 * np.sin(2 * np.pi * 180 * t) * np.exp(-t / 0.05)
        for k in (0.04, 0.08):
            add(s, hp(RNG.standard_normal(int(0.03 * SR)), 2000) * np.exp(-tvec(0.03) / 0.008), k)
        return s * 0.6
    if kind == "ding":
        s = bell(mtof(n("E6")), 1.5, 0.45)
        s[: int(1.2 * SR)] += bell(mtof(n("B6")), 1.2, 0.2)
        return s
    if kind == "riser4":
        return riser(4 * B, 0.25)
    if kind == "riser3":
        return riser(3 * B, 0.22)
    if kind == "stamp":
        t = tvec(0.35)
        s = np.sin(2 * np.pi * (70 + 60 * np.exp(-t / 0.02)) * t) * np.exp(-t / 0.09)
        s += 0.5 * bp(RNG.standard_normal(len(t)), 300, 2500) * np.exp(-t / 0.03)
        return s * 0.8
    if kind == "thud":
        t = tvec(0.3)
        s = np.sin(2 * np.pi * np.cumsum(55 + 40 * np.exp(-t / 0.03)) / SR) * np.exp(-t / 0.1)
        return s * 0.55
    if kind == "drop":
        t = tvec(0.6)
        f = 1400 * np.exp(-t / 0.35) + 300
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
        s[-int(0.1 * SR):] *= np.linspace(1, 0, int(0.1 * SR))
        add(s, sfx_sound("thud", B) * 1.2, 0.5)
        return s
    if kind == "munch":
        s = np.zeros(int(0.7 * SR))
        for k in range(4):
            seg = bp(RNG.standard_normal(int(0.09 * SR)), 400, 2500) * np.exp(-tvec(0.09) / 0.03)
            add(s, seg, k * 0.15)
        return s * 0.6
    if kind == "hit":
        t = tvec(1.2)
        s = kick(1.0)
        s = np.pad(s, (0, len(t) - len(s)))
        s += 0.5 * hp(RNG.standard_normal(len(t)), 3000) * np.exp(-t / 0.35)
        s += bell(mtof(n("C6")), 1.2, 0.35)[: len(t)]
        return s * 0.6
    if kind == "sparkle":
        s = np.zeros(int(1.0 * SR))
        for k, nm in enumerate(["C7", "G6", "E7", "C7", "G7"]):
            add(s, bell(mtof(n(nm)), 0.5, 0.18, idx=1.0), k * 0.06 + RNG.uniform(0, 0.02))
        return s
    if kind == "boom":
        t = tvec(2.0)
        s = np.sin(2 * np.pi * np.cumsum(38 + 50 * np.exp(-t / 0.08)) / SR) * np.exp(-t / 0.6)
        s += 0.2 * lp(RNG.standard_normal(len(t)), 300) * np.exp(-t / 0.5)
        return reverb(s, 2.0, 0.35) * 0.9
    if kind == "buzz":
        s = np.zeros(int(0.5 * SR))
        for k in (0, 0.2):
            tt = tvec(0.15)
            sq = np.sign(np.sin(2 * np.pi * 190 * tt)) * 0.25
            sq = lp(sq, 2500)
            sq[-200:] *= np.linspace(1, 0, 200)
            add(s, sq, k)
        return s
    if kind == "zip":
        t = tvec(0.35)
        f = 300 + 2200 * (t / 0.35)
        s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.12
        return lp(s, 4000) * np.sin(np.pi * t / 0.35)
    raise ValueError(kind)


def build_sfx(tl):
    B = 60.0 / tl["bpm"]
    total = tl["totalBeats"] * B + tl["tailSeconds"]
    buf = np.zeros(int(total * SR) + SR * 3)
    for beat, kind in tl["sfx"]:
        add(buf, sfx_sound(kind, B), beat * B)
    buf = buf[: int(total * SR)]
    buf = reverb(buf, 0.8, 0.12)
    st = np.stack([buf, buf], 1)
    return st / np.max(np.abs(st)) * 0.85


def write_wav(path, st):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (np.clip(st, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    proj = Path(sys.argv[1] if len(sys.argv) > 1 else "projects/durian")
    tl = json.loads((proj / "timeline.json").read_text())
    write_wav(proj / "build" / "music.wav", build_music(tl))
    write_wav(proj / "build" / "sfx.wav", build_sfx(tl))
    print("ok")
