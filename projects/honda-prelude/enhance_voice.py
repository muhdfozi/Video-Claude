"""Studio-voice step 1: AI noise removal with DeepFilterNet3 (48 kHz, mono).

usage: PYTHONPATH=/home/user/pystub python3 enhance_voice.py in48k.wav out48k.wav [model_dir] [atten_lim_db]

- DeepFilterNet's model zip is fetched once via a sparse git clone of github.com/Rikorose/DeepFilterNet
  (the direct raw download is blocked by the proxy); torchaudio is not available for this torch build, so a
  tiny stub package (/home/user/pystub/torchaudio) satisfies its imports — we pass tensors directly.
- atten_lim_db caps how much noise is removed (default 32 dB): full removal can sound gated/"underwater";
  a cap keeps a natural, quiet room tone like a treated studio.
"""
import sys, wave
import numpy as np
import torch
from df.enhance import enhance, init_df

src, dst = sys.argv[1], sys.argv[2]
model_dir = sys.argv[3] if len(sys.argv) > 3 else "/home/user/dfmodel/DF3/DeepFilterNet3"
lim = float(sys.argv[4]) if len(sys.argv) > 4 else 32.0

model, st, _ = init_df(model_base_dir=model_dir)
assert st.sr() == 48000
w = wave.open(src)
assert w.getframerate() == 48000
x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, w.getnchannels()).mean(1).astype(np.float32) / 32768
y = enhance(model, st, torch.from_numpy(x)[None], atten_lim_db=lim).squeeze().numpy()
o = wave.open(dst, "wb"); o.setnchannels(1); o.setsampwidth(2); o.setframerate(48000)
o.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()); o.close()
print("enhanced", dst, f"{len(y) / 48000:.2f}s", f"atten_lim {lim} dB")
