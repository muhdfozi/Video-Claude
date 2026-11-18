# Video-Claude: siri **Sebab Apa?**

Video explainer pendek (9:16, ~55 s) dalam Bahasa Melayu. Animasinya bergaya potongan kertas, dengan muzik dan SFX asli. Semuanya dijana dengan kod dan dikunci pada tempo **110 BPM**.

- `STYLE-GUIDE.md`: analisis gaya rujukan dan formula versi sendiri
- `projects/<topik>/`: satu folder untuk satu video
  - `timeline.json`: **sumber tunggal**. Mengandungi BPM, ayat VO (`*kata kunci*`, `|` untuk pecahan kapsyen) dan masa SFX dalam beat
  - `skrip-vo.md`: skrip untuk rakaman suara (dijana)
  - `scene.html` + `scene.js`: animasi (canvas, dilukis ikut beat)
  - `captions.json` / `captions.srt`: kapsyen (dijana)
- `tools/`
  - `build_script.py`: timeline → skrip VO + kapsyen
  - `music.py`: sintesis muzik + SFX asli (numpy)
  - `render.js`: Chromium (Playwright) → frame → ffmpeg
  - `finalize.py`: mix video + muzik + SFX (+ VO dengan sync per ayat & ducking)
  - `lib/paper.js`: perpustakaan gaya kertas (kamera, kapsyen, watak cicak, orang)
- `output/`: MP4 siap

## Bina semula

```bash
P=projects/durian
python3 tools/build_script.py $P          # skrip + kapsyen
python3 tools/music.py $P                 # muzik + sfx
node tools/render.js $P video             # video (tanpa audio)
python3 tools/finalize.py $P preview      # output/durian_preview.mp4
python3 tools/finalize.py $P final $P/vo/rakaman.m4a   # selepas VO dirakam
```

Keperluan: Python 3 (numpy, scipy, faster-whisper untuk sync VO), Node + Playwright (Chromium), ffmpeg.
