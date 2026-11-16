#!/usr/bin/env python3
"""Make a phone voice-over sound like a high-end mic in a treated studio.

Chain:
  1. adeclip + -3 dB headroom (phone recordings often clip on plosives)
  2. DeepFilterNet 3 (deep-filter binary): removes background noise and room
     reverb; attenuation limited to 40 dB so the voice stays natural
  3. studio polish: 2x high-pass @70 Hz, +1.5 dB warmth @120 Hz, -3 dB boxiness @320 Hz,
     -1 dB @650 Hz, +2.5 dB presence @4.2 kHz, +3 dB air shelf @10 kHz, de-esser,
     two-stage compression (3:1 then 2:1), light harmonic exciter, limiter, -16 LUFS
  Output: 48 kHz / 24-bit WAV (final loudness is set again in the video mix).

Usage:
  python3 studio_voice.py INPUT.m4a OUTPUT.wav --deep-filter /path/to/deep-filter
  (binary: github.com/Rikorose/DeepFilterNet/releases, deep-filter-0.5.6-x86_64-unknown-linux-musl)
"""
import argparse
import os
import subprocess
import tempfile

STUDIO_CHAIN = ",".join([
    "highpass=f=70:poles=2", "highpass=f=70:poles=2",
    "equalizer=f=120:t=q:w=0.9:g=1.5",
    "equalizer=f=320:t=q:w=1.2:g=-3",
    "equalizer=f=650:t=q:w=1.4:g=-1",
    "equalizer=f=4200:t=q:w=1.0:g=2.5",
    "highshelf=f=10000:g=3",
    "deesser=i=0.4:m=0.5:f=0.5:s=o",
    "acompressor=threshold=-24dB:ratio=3:attack=6:release=90:knee=4:makeup=4dB",
    "acompressor=threshold=-14dB:ratio=2:attack=15:release=200:makeup=1dB",
    "aexciter=amount=1.2:drive=4:blend=0:freq=6000:ceil=16000",
    "alimiter=limit=0.89:level=false",
    "loudnorm=I=-16:TP=-1.5:LRA=7",
    "aresample=48000",
])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--deep-filter", required=True, help="path to the deep-filter binary")
    ap.add_argument("--atten", default="40", help="max noise attenuation in dB")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as td:
        pre = os.path.join(td, "pre.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.input, "-af",
                        "aresample=48000,adeclip,volume=-3dB", "-ac", "1", "-c:a", "pcm_f32le", pre],
                       check=True)
        outdir = os.path.join(td, "df")
        subprocess.run([a.deep_filter, "-D", "-a", a.atten, "-o", outdir, pre], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(outdir, "pre.wav"),
                        "-af", STUDIO_CHAIN, "-c:a", "pcm_s24le", a.output], check=True)
    print("studio voice ->", a.output)


if __name__ == "__main__":
    main()
