# Video-Claude — "Lori Towing"

A 41-second vertical (1080×1920) 3D animated short built entirely in code,
on top of a recorded Malay voiceover. Style is inspired by second-person
3D explainer shorts ("kalau kau…"): constant slow camera moves, ~2 s shots,
word-by-word captions, but with its own look — Malaysian highway world,
keyword pills (yellow = escalation, red = "rosak"), phone call cards and a
running tow-truck tally.

Every cut, hazard-light blink, reverse beeper and drum hit is locked to a
**110 BPM** grid (1 beat = 0.545 s, 1 bar = 2.18 s; the video is 19 bars).

## Pipeline

```
assets/voiceover.m4a ──transcribe.py──> video/transcript.json   (Whisper, word timestamps)
                                            │
                                   timeline.py  (fixes mishearings, caption styles,
                                            │    story events + shot cuts on the beat grid)
                                            ▼
                                   build/timeline.json
                         ┌──────────────────┴──────────────────┐
                    audio.py                              render.mjs
       (110 BPM music + SFX + voice mix)       (Three.js scene in headless Chromium,
                build/mix.wav                    frames → ffmpeg, muxed with mix.wav)
                                                             │
                                                   out/preview.mp4 / out/final.mp4
```

## Run

```bash
npm install                      # three.js
pip install faster-whisper numpy # only needed to re-transcribe

# put the voiceover at assets/voiceover.m4a (not committed)
python3 tools/transcribe.py small   # optional: transcript.json is committed
python3 tools/timeline.py
python3 tools/audio.py
node tools/render.mjs --preview     # 540x960 @15fps draft  -> out/preview.mp4
node tools/render.mjs               # 1080x1920 @30fps final -> out/final.mp4
node tools/render.mjs --stills 4.4,17.5,40.9   # PNG stills for checking shots
```

## Where things live

- `video/scene.js` — the whole 3D scene: world, car, five tow trucks (each bigger),
  the character, smoke, per-shot cameras (`SHOTS`), and the 2D overlay
  (captions, call card, tally).
- `tools/timeline.py` — caption corrections, story event times (`events`), shot
  list (`cuts` / `shots`). Change timing here, then re-run `audio.py` and render.
- `tools/audio.py` — music arrangement (chords, drums, breakdown drop-outs,
  sad trombone ending), sound effects and side-chain ducking under the voice.
