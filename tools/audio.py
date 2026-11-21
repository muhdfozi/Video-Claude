"""Synthesise the relaxed music bed (tempo from video/config.json) + sound effects and mix with the voiceover.

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


# ---------------------------------------------------------------- drums (soft, lo-fi)
def kick():
    t = t_axis(0.4)
    f = 42 + 60 * np.exp(-t / 0.04)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t / 0.16) * np.minimum(1, t / 0.004)


def snap():
    # finger snap / rim: short band-limited click
    t = t_axis(0.12)
    n = highpass(lowpass(rng.standard_normal(len(t)), 4200), 1400)
    return n * np.exp(-t / 0.018) * 0.9


def shaker():
    t = t_axis(0.09)
    n = highpass(rng.standard_normal(len(t)), 6000)
    return n * np.sin(np.pi * np.minimum(1, t / 0.09)) ** 2 * 0.35


# ---------------------------------------------------------------- tonal
def rhodes(freq, sec):
    """Warm electric-piano-ish tone with a soft bell attack and slow tremolo."""
    t = t_axis(sec)
    s = np.sin(2 * np.pi * freq * t)
    s += 0.22 * np.sin(2 * np.pi * 2 * freq * t) * np.exp(-t / 0.5)
    s += 0.10 * np.sin(2 * np.pi * 7.02 * freq * t) * np.exp(-t / 0.04)
    env = np.exp(-t / 1.4) * np.minimum(1, t / 0.006) * np.minimum(1, (sec - t) / 0.15)
    return s * env * (1 + 0.1 * np.sin(2 * np.pi * 4.1 * t))


def bass(freq, sec):
    t = t_axis(sec)
    s = np.sin(2 * np.pi * freq * t) + 0.18 * np.sin(2 * np.pi * freq * 2 * t)
    return s * np.minimum(1, t / 0.02) * np.exp(-t / 0.9) * np.minimum(1, (sec - t) / 0.06)


# relaxed jazzy loop, one chord per bar: Fmaj7 - Em7 - Dm7 - Cmaj7
CHORDS = [(41, [53, 57, 60, 64]), (40, [52, 55, 59, 62]), (38, [50, 53, 57, 60]), (36, [48, 52, 55, 59])]
SWING = 0.09 * BEAT                              # late off-beats = laid-back feel

music = np.zeros(N)
drums = np.zeros(N)
breaks = EV["break"]
stop_at = EV["gag"]                             # "masih tak bergerak": the band stops
n_beats = int(DUR / BEAT) + 1


def muted(t):
    # the band drops out for one beat right after each breakdown
    return any(b <= t < b + BEAT for b in breaks) or t >= stop_at


for bi in range(n_beats):
    tb = bi * BEAT
    bar, beat_in_bar = divmod(bi, 4)
    root, chord = CHORDS[bar % 4]
    intro = bar < 1
    if muted(tb):
        continue
    # chord: full strum on 1, a softer push on the "and" of 2
    if beat_in_bar == 0:
        for j, n in enumerate(chord):
            place(music, rhodes(note(n + 12), BEAT * 3.6), tb + j * 0.012, 0.12)
    if beat_in_bar == 1 and not muted(tb + BEAT / 2 + SWING):
        for j, n in enumerate(chord[1:]):
            place(music, rhodes(note(n + 12), BEAT * 1.8), tb + BEAT / 2 + SWING + j * 0.01, 0.06)
    # bass on 1 and 3
    if beat_in_bar in (0, 2):
        place(music, bass(note(root), BEAT * 1.7), tb, 0.42)
    # drums
    if beat_in_bar == 0 or (beat_in_bar == 2 and not intro):
        place(drums, kick(), tb, 0.6 if intro else 0.85)
    if beat_in_bar == 2 and not intro and not muted(tb + BEAT / 2 + SWING):
        place(drums, kick(), tb + BEAT / 2 + SWING, 0.4)
    if beat_in_bar in (1, 3) and not intro:
        place(drums, snap(), tb, 0.5)
    if not intro:
        place(drums, shaker(), tb, 0.12)
        if not muted(tb + BEAT / 2 + SWING):
            place(drums, shaker(), tb + BEAT / 2 + SWING, 0.2)

music = lowpass(music, 2600)                     # warm, dark top end

# reverse-cymbal swell into the big reveal
sw = 2 * BEAT
t_sw = t_axis(sw)
swell = highpass(rng.standard_normal(len(t_sw)), 3000) * (t_sw / sw) ** 2.5
place(drums, swell, EV["reveal"] - sw, 0.35)

# sad trombone after "masih tak bergerak"
def trombone(midi, sec, vib=False):
    t = t_axis(sec)
    f = note(midi) * (1 + (0.012 * np.sin(2 * np.pi * 6 * t) * np.minimum(1, t / 0.3) if vib else 0))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = sum((1 / h) * np.sin(ph * h) for h in range(1, 8))
    s = lowpass(s, 1400)
    return s * np.minimum(1, t / 0.04) * np.minimum(1, (sec - t) / 0.12)

tr = EV["facepalm"]
for i, (m, d) in enumerate([(62, 0.48), (61, 0.48), (60, 0.48), (59, 1.4)]):
    place(music, trombone(m, d, vib=(i == 3)), tr + i * 0.5, 0.22)

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
for i, (a, b) in enumerate(EV["loads"]):
    place(sfx, winch(b - a), a, 0.5)
    place(sfx, clank(), b, 0.45 + 0.05 * i)       # stack lands on the bed
for a, b, _ in EV["drive"]:
    place(sfx, engine(b - a + 0.3, 1.25), a, 0.5)
for i, bt in enumerate(breaks):
    place(sfx, bang(), bt, 0.7 + 0.06 * i)
    place(sfx, sputter(), bt + 0.05, 0.45)
    place(sfx, hiss(), bt + 0.1, 0.5)

# ---------------------------------------------------------------- voice + mix
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(ROOT, "build", "voice_edit.wav"),
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
