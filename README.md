# Video-Claude — "Lori Towing"

A 38-second vertical (1080×1920) 3D animated short built entirely in code,
on top of a recorded Malay voiceover. Visual language follows cinematic
explainer reels: dusk/night lighting with practical light glows, sentence
subtitles in a dark box with coloured keywords (blue = info, red = failure),
big punch titles ("ROSAK! ✗"), data numbers ("• TINGGI MENARA 13.9 m"),
leader-line callouts pinned to 3D objects, and a closing question.

Every cut, hazard-light blink, reverse beeper and drum hit is locked to a
**110 BPM** grid (1 beat = 0.545 s, 1 bar = 2.18 s). The voiceover is tightened
so every sentence also starts on a half-beat.

## Pipeline

```
assets/voiceover.m4a ──transcribe.py──> video/transcript.json  (Whisper, word timestamps)
        │
   vo_edit.py   cuts dead air, breaths, hesitations (41.4s -> 35.2s of speech);
        │       each sentence starts on the next half-beat
        ▼
   build/voice_edit.wav + build/vo_map.json
        │
   timeline.py  word times moved to the edited clock; shot cuts and story
        │       events derived from anchor words, snapped to the beat grid
        ▼
   build/timeline.json
        ├── audio.py    110 BPM music + SFX + voice mix      -> build/mix.wav
        └── render.mjs  Three.js scene in headless Chromium  -> out/preview.mp4 | out/final.mp4
```

## Run

```bash
npm install                        # three.js
pip install faster-whisper numpy   # whisper only needed to re-transcribe

# put the voiceover at assets/voiceover.m4a (not committed)
python3 tools/transcribe.py small  # optional: transcript.json is committed
python3 tools/vo_edit.py
python3 tools/timeline.py
python3 tools/audio.py
node tools/render.mjs --preview    # 540x960 @15fps draft  -> out/preview.mp4
node tools/render.mjs              # 1080x1920 @30fps final -> out/final.mp4
node tools/render.mjs --stills 4.4,17.5,36   # PNG stills for checking shots
```

## Where things live

- `video/scene.js` — the whole 3D scene: world, car, five tow trucks (each ~1.35x
  bigger so its bed can carry the previous one; they stack into a tower),
  the character, smoke, per-shot cameras (`SHOTS`), and the 2D overlay
  (subtitles, titles, data numbers, callouts — all listed in one block, timed
  from the timeline).
- `tools/vo_words.py` — Whisper mishearings fixed, word onsets corrected.
- `tools/vo_edit.py` — pause/breath detection and the tightened voice edit.
- `tools/timeline.py` — anchor phrases for each shot, story events, caption styles.
- `tools/audio.py` — music arrangement (chords, drums, breakdown drop-outs,
  sad trombone ending), sound effects and side-chain ducking under the voice.
