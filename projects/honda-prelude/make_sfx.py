"""Synthesize simple SFX (no external libraries/assets). Output 48 kHz stereo WAV."""
import numpy as np, wave, sys, os
SR = 48000
out = sys.argv[1] if len(sys.argv) > 1 else "sfx"
os.makedirs(out, exist_ok=True)
rng = np.random.default_rng(7)

def save(name, x):
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.9
    st = np.stack([x, x], 1)
    with wave.open(f"{out}/{name}.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())

def t(d): return np.arange(int(SR * d)) / SR

def onepole_lp(x, fc):
    # time-varying one-pole low-pass, fc array (Hz)
    y = np.zeros_like(x); a = np.exp(-2 * np.pi * np.asarray(fc) / SR) * np.ones_like(x); s = 0.0
    for i in range(len(x)):
        s = (1 - a[i]) * x[i] + a[i] * s; y[i] = s
    return y

# whoosh: band-ish noise, filter sweep up then down, bell envelope
d = 0.45; tt = t(d); n = rng.standard_normal(len(tt))
fc = 300 + 5000 * np.sin(np.pi * tt / d) ** 2
w = onepole_lp(n, fc) - onepole_lp(n, fc * 0.15)
env = np.sin(np.pi * tt / d) ** 1.5
save("whoosh", w * env)

# pop: short sine with fast pitch drop
d = 0.09; tt = t(d); f = 900 * np.exp(-tt * 30) + 250
ph = 2 * np.pi * np.cumsum(f) / SR
save("pop", np.sin(ph) * np.exp(-tt * 45) * (1 - np.exp(-tt * 2000)))

# ding: bell partials
d = 1.2; tt = t(d)
x = sum(a * np.sin(2 * np.pi * f * tt) * np.exp(-tt * k) for f, a, k in
        [(1568, 1, 3.5), (3136, .45, 5), (4704, .2, 7), (2093, .3, 4.5)])
save("ding", x * (1 - np.exp(-tt * 3000)))

# cash: two quick high dings + short noise "shk"
d = 0.9; tt = t(d)
b = lambda f0, t0: np.where(tt >= t0, np.sin(2*np.pi*f0*(tt-t0)) * np.exp(-(tt-t0)*6), 0)
shk = rng.standard_normal(len(tt)) * np.exp(-tt * 40) * 0.25
save("cash", b(2637, 0) + .8 * b(3520, 0.07) + .3 * b(5274, 0.07) + shk)

# riser: noise + rising tone, crescendo
d = 1.0; tt = t(d); n = rng.standard_normal(len(tt))
r = onepole_lp(n, 200 + 6000 * (tt / d) ** 2) * 0.6
ph = 2 * np.pi * np.cumsum(220 * 2 ** (2 * tt / d)) / SR
save("riser", (r + 0.25 * np.sin(ph)) * (tt / d) ** 2)

# record scratch-ish (comedic "eh?"): fast down-up pitch wobble on noise+saw
d = 0.35; tt = t(d)
f = 600 + 500 * np.sin(2 * np.pi * 6 * tt)
ph = 2 * np.pi * np.cumsum(f) / SR
saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
save("scratch", (saw * 0.5 + rng.standard_normal(len(tt)) * 0.3) * np.exp(-tt * 6))

# soft click for subtitle-free emphasis
d = 0.03; tt = t(d)
save("click", rng.standard_normal(len(tt)) * np.exp(-tt * 300))
print("ok")
