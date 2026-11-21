"""Synthesise the 110 BPM music bed + sound effects and mix with the voiceover.

Everything is generated from build/timeline.json so audio and picture share
the same clock: drum hits land on the beat grid the cuts use, reverse beeps
tick on the beat while trucks back in, breakdowns cut the music for a beat.
Output: build/mix.wav (48 kHz stereo).
"""
import json, os, subprocess
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
TL = json.load(open(os.path.join(ROOT, "build", "timeline.json")))
EV = TL["events"]
BEAT = EV["beat"]
DUR = TL["duration"]
N = int(DUR * SR) + SR // 2
rng = np.random.default_rng(7)


def t_axis(sec):
    return np.arange(int(sec * SR)) / SR


def place(buf, sig, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


def env_exp(sec, tau):
    return np.exp(-t_axis(sec) / tau)


def lowpass(x, cutoff):
    # one-pole low-pass
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc; y[i] = acc
    return y


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


def note(f):
    return 440.0 * 2 ** ((f - 69) / 12)


# ---------------------------------------------------------------- drums
def kick():
    t = t_axis(0.32)
    f = 48 + 95 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t / 0.13) + 0.3 * np.sin(ph * 2) * np.exp(-t / 0.02)


def clap():
    t = t_axis(0.22)
    n = rng.standard_normal(len(t))
    n = highpass(lowpass(n, 2600), 900)
    e = np.exp(-t / 0.06)
    for d in (0.0, 0.011, 0.022):              # three quick hand hits
        e += 0.6 * np.exp(-np.clip(t - d, 0, None) / 0.008) * (t >= d)
    return n * e * 0.9


def hat(open_=False):
    t = t_axis(0.18 if open_ else 0.05)
    n = highpass(rng.standard_normal(len(t)), 7000)
    return n * np.exp(-t / (0.06 if open_ else 0.014)) * 0.5


# ---------------------------------------------------------------- tonal
def pluck(freq, sec=0.45, bright=1.0):
    t = t_axis(sec)
    # marimba-ish: fundamental + 4th harmonic, fast decay on the overtone
    s = np.sin(2 * np.pi * freq * t) * np.exp(-t / 0.22)
    s += 0.35 * bright * np.sin(2 * np.pi * freq * 3.98 * t) * np.exp(-t / 0.03)
    s *= np.minimum(1, t / 0.002)
    return s


def bass(freq, sec):
    t = t_axis(sec)
    s = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 2 * t) + 0.12 * np.sin(2 * np.pi * freq * 3 * t)
    return s * np.minimum(1, t / 0.005) * np.exp(-t / 0.35) * np.minimum(1, (sec - t) / 0.02)


# chord progression per bar: I - vi - IV - V in C (playful, major)
CHORDS = [(48, [60, 64, 67, 72]), (45, [57, 60, 64, 69]), (41, [53, 57, 60, 65]), (43, [55, 59, 62, 67])]
ARP = [0, 2, 1, 3, 2, 1, 3, 2]                 # 8th-note arpeggio pattern

music = np.zeros(N)
drums = np.zeros(N)
breaks = EV["break"]
stop_at = 38.10                                 # "masih tak bergerak": the band stops
n_beats = int(DUR / BEAT)


def muted(t):
    # music drops out for one beat right after each breakdown
    return any(b <= t < b + BEAT * 1.0 for b in breaks) or t >= stop_at


for bi in range(n_beats):
    tb = bi * BEAT
    bar, beat_in_bar = divmod(bi, 4)
    root, chord = CHORDS[bar % 4]
    intro = bar < 1
    if not muted(tb):
        if beat_in_bar in (0, 2) or (beat_in_bar == 3 and bar % 2 == 1):
            place(drums, kick(), tb + (BEAT / 2 if beat_in_bar == 3 else 0), 0.55 if intro else 0.9)
        if beat_in_bar in (1, 3) and not intro:
            place(drums, clap(), tb, 0.45)
        for h in range(2):
            th = tb + h * BEAT / 2
            if not muted(th) and not intro:
                place(drums, hat(open_=(h == 1 and beat_in_bar == 3)), th, 0.22 if h else 0.14)
        # bass on the beat and the "and"
        place(music, bass(note(root), BEAT * 0.45), tb, 0.38)
        if beat_in_bar in (1, 3):
            place(music, bass(note(root + 12), BEAT * 0.3), tb + BEAT / 2, 0.22)
    for h in range(2):
        th = tb + h * BEAT / 2
        if not muted(th):
            n = chord[ARP[(beat_in_bar * 2 + h) % 8]]
            place(music, pluck(note(n + 12)), th, 0.16 if h else 0.2)

# drum fill into the big reveal (last bar before 34.36)
fill_start = 63 * BEAT - 4 * BEAT
for i in range(8):
    place(drums, clap(), fill_start + 2 * BEAT + i * BEAT / 4, 0.18 + i * 0.04)

# sad trombone after "masih tak bergerak"
def trombone(midi, sec, vib=False):
    t = t_axis(sec)
    f = note(midi) * (1 + (0.012 * np.sin(2 * np.pi * 6 * t) * np.minimum(1, t / 0.3) if vib else 0))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = sum((1 / h) * np.sin(ph * h) for h in range(1, 8))
    s = lowpass(s, 1400)
    return s * np.minimum(1, t / 0.04) * np.minimum(1, (sec - t) / 0.12)

tr = 39.27
for i, (m, d) in enumerate([(62, 0.42), (61, 0.42), (60, 0.42), (59, 1.3)]):
    place(music, trombone(m, d, vib=(i == 3)), tr + i * 0.43, 0.22)

# ---------------------------------------------------------------- sfx
sfx = np.zeros(N)


def whoosh(sec=0.32):
    t = t_axis(sec)
    n = rng.standard_normal(len(t))
    sweep = np.sin(np.pi * t / sec) ** 2
    return highpass(lowpass(n, 3500), 400) * sweep * 0.5


def beep(f=1050, sec=0.17):
    t = t_axis(sec)
    return np.sign(np.sin(2 * np.pi * f * t)) * 0.25 * np.minimum(1, (sec - t) / 0.01) * np.minimum(1, t / 0.003)


def ringback():
    # Malaysian ringback: 425 Hz, 0.4 on / 0.2 off / 0.4 on
    out = np.zeros(int(1.0 * SR))
    for st in (0.0, 0.6):
        t = t_axis(0.4)
        place(out, np.sin(2 * np.pi * 425 * t) * np.minimum(1, (0.4 - t) / 0.01), st, 1)
    return out


def engine(sec, rpm=1.0):
    t = t_axis(sec)
    f = 32 * rpm + 6 * np.sin(2 * np.pi * 0.7 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sign(np.sin(ph)) * 0.5 + 0.5 * np.sin(ph * 2)
    s = lowpass(s + 0.3 * rng.standard_normal(len(t)), 420)
    fade = np.minimum(1, t / 0.2) * np.minimum(1, (sec - t) / 0.25)
    return s * fade


def bang():
    t = t_axis(0.6)
    thump = np.sin(2 * np.pi * (60 + 80 * np.exp(-t / 0.03)) * t) * np.exp(-t / 0.12)
    crack = lowpass(rng.standard_normal(len(t)), 2500) * np.exp(-t / 0.05)
    return thump * 0.9 + crack * 0.7


def sputter():
    out = np.zeros(int(1.2 * SR))
    for i, d in enumerate([0.15, 0.32, 0.46, 0.7, 0.95]):
        t = t_axis(0.12)
        pop = lowpass(rng.standard_normal(len(t)), 900) * np.exp(-t / 0.03)
        place(out, pop, d, 0.7 / (1 + i * 0.35))
    return out


def hiss(sec=1.8):
    t = t_axis(sec)
    return highpass(rng.standard_normal(len(t)), 3000) * np.exp(-t / 0.7) * np.minimum(1, t / 0.05) * 0.35


def clank():
    t = t_axis(0.5)
    s = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, a, d in [(1240, 0.5, 0.12), (2470, 0.35, 0.08), (3710, 0.2, 0.05), (180, 0.6, 0.06)])
    return s * np.minimum(1, t / 0.001)


def winch(sec):
    t = t_axis(sec)
    f = 140 + 120 * t / sec
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = (2 * ((ph / (2 * np.pi)) % 1) - 1) * 0.3
    return lowpass(s, 1200) * np.minimum(1, t / 0.1) * np.minimum(1, (sec - t) / 0.1)


def pop():
    t = t_axis(0.12)
    return np.sin(2 * np.pi * (900 - 2500 * t) * t) * np.exp(-t / 0.035) * 0.6


for s in TL["shots"][1:]:
    place(sfx, whoosh(), s["start"] - 0.16, 0.22)
for c in EV["calls"]:
    place(sfx, pop(), c, 0.5)
    place(sfx, ringback(), c + 0.15, 0.09)
for i, (a, b) in enumerate(EV["arrive"]):
    place(sfx, engine(b - a + 0.6, 1.0 + i * 0.05), a, 0.45)
    # reverse beeper locked to the beat grid
    k = int(np.ceil(a / BEAT))
    while k * BEAT < b + 0.2:
        place(sfx, beep(), k * BEAT, 0.5)
        k += 1
for h in EV["hitch"]:
    if h:
        place(sfx, clank(), h, 0.55)
place(sfx, winch(EV["load"][1] - EV["load"][0]), EV["load"][0], 0.5)
for a, b, _ in EV["drive"]:
    place(sfx, engine(b - a + 0.3, 1.25), a, 0.5)
for i, bt in enumerate(breaks):
    place(sfx, bang(), bt, 0.7 + 0.06 * i)
    place(sfx, sputter(), bt + 0.05, 0.45)
    place(sfx, hiss(), bt + 0.1, 0.5)

# ---------------------------------------------------------------- voice + mix
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(ROOT, "assets", "voiceover.m4a"),
                      "-af", "highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,loudnorm=I=-15:TP=-1.5:LRA=7",
                      "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
vo = np.frombuffer(pcm, np.int16).astype(np.float64) / 32768
voice = np.zeros(N); voice[: min(N, len(vo))] = vo[:N]

# side-chain: duck music while the voice is talking
win = int(0.05 * SR)
level = np.sqrt(np.convolve(voice ** 2, np.ones(win) / win, mode="same"))
duck = 1 - 0.55 * np.clip(level / 0.06, 0, 1)
duck = lowpass(duck, 6)

bed = (music * 0.55 + drums * 0.5) * duck
mix = voice * 1.0 + bed * 0.55 + sfx * 0.42
mix[-int(0.15 * SR):] *= np.linspace(1, 0, int(0.15 * SR))
print("peaks voice %.2f bed %.2f sfx %.2f" % (np.abs(voice).max(), np.abs(bed*0.55).max(), np.abs(sfx*0.55).max()))
peak = np.max(np.abs(mix))
mix = np.tanh(mix * 1.05) / np.tanh(1.05) * 0.95      # soft limiter: keeps the voice loud, rounds off bangs
mix = mix[: int(DUR * SR)]
stereo = np.stack([mix, mix], axis=1)
out = (np.clip(stereo, -1, 1) * 32767).astype(np.int16)
import wave
with wave.open(os.path.join(ROOT, "build", "mix.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print(f"mix ok: {DUR:.2f}s, peak {peak:.2f}")
