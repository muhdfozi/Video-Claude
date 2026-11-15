---
name: style-rentak
description: Preset editing "style rentak" — gaya SENDIRI user (inspirasi dari 4 reference TikTok, bukan tiru): speed rule 110 BPM (setiap elemen jatuh tepat atas beat), palet arang + krim + aksen oren, font Anton / Instrument Serif Italic / JetBrains Mono, HUD REC + progress bab, word slam, ledger mono, counter berguling, bracket viewfinder. Guna TERUS bila user sebut "style rentak" (atau "rentak").
---

# Style Rentak

Gaya milik user. Diinspirasi (tidak ditiru) daripada 4 reference TikTok yang dikaji frame demi frame
(@akidahmad GrabMaps & "Claude Video for Dummies", @abdmateenhashim pakar.io, @tenfoldmarc 17 video effects).
Demo approved/rujukan: `exports/GR86-Gaji-Layak-RENTAK.mp4`, EDL `projects/gr86-rentak/edl.py`,
grafik `projects/honda-prelude/rentak_gfx.py`. Peraturan umum (export TikTok, tiada subtitle, warna asal,
jumlah kira sebenar, hantar GitHub) ikut `.claude/skills/tiktok-edit-style/SKILL.md` + `style-kira-detail`.

## Apa yang dipelajari dari reference (ringkas)
| Ref | Ambil prinsip | Tidak diambil |
|---|---|---|
| GrabMaps | latar gelap, satu aksen, kaunter + progress bar, bracket pada muka, teks bina perkataan demi perkataan | hijau Grab, grid peta |
| Claude for Dummies | campur sans tebal + serif italic untuk satu kata emosi, kad UI berisi | hijau/krim editorial, serif Didot |
| pakar.io | **speed rule 110 BPM** (beat = 0.545 s), word slam penuh skrin, HUD mono, stat besar | lime, maskot, voxel |
| 17 video effects | penomboran "01/17", ritma senarai, kontras tajuk tebal | kuning, grade gelap |
Kadar cakap reference 165–208 wpm, jeda > 0.3 s hampir tiada → potong semua jeda.

## Identiti Rentak
- **Speed rule:** grid **110 BPM**. Muzik di-time-stretch ke 110 BPM (librosa kesan tempo asal → `atempo`),
  fasa grid dipilih supaya paling banyak cut jatuh atas beat, permulaan muzik dianjak supaya beat muzik = beat grid.
  Setiap elemen grafik di-*snap* ke beat terdekat (±0.22 s). Word slam: **satu perkataan setiap beat**.
  Tiada > 4 beat (~2.2 s) tanpa perubahan visual.
- **Palet:** arang `#111113`, krim `#F3EFE6`, aksen oren `#FF5A1F` (boleh tukar `ACCENT`), kelabu `#9A968E`, merah REC.
- **Font:** Anton (kata kinetik, huruf besar) · Instrument Serif Italic (SATU kata aksen, oren) ·
  JetBrains Mono ExtraBold (HUD, ledger, nombor) · Inter Display SemiBold (ayat tag).
- **Elemen** (`RENTAK = dict(bpm=110, chapters=[...], items=[...])`):
  - `chapters`: HUD kiri atas `● REC  02/07 · KOS OTR` + bar progress bersegmen (setiap segmen terisi ikut bab).
  - `slam`: panel arang miring masuk dari kanan (130 ms), perkataan Anton muncul satu per beat (scale 130→100),
    kata aksen serif italic oren; `alpha="50"` untuk hook (muka masih nampak), `"18"` untuk tajuk bab.
  - `ledger`: kad arang, tajuk Anton + petak oren, baris mono "taip masuk" (clip sweep 220 ms) bila disebut;
    baris `"total"` oren + garis.
  - `counter`: kad arang, label mono, nombor mono berguling + bar oren tumbuh; `accent=True` → oren + cash + `flash`.
  - `tag`: pill arang dengan tepi oren, indeks mono (contoh "SZ", "20%"), ayat Inter, kata kunci oren.
  - `brackets`: penjuru viewfinder oren snap masuk pada muka + label mono ("HARGA").
  - `flash`: kilat krim 2 frame atas beat untuk momen besar.
- **SFX (atas beat):** klik setiap perkataan/baris/tag, whoosh lembut masuk panel, cash pada jumlah.
- **Framing talking head:** crop centre di BAWAH muka (`FACE=(0.47,0.60)`, zoom 1.18–1.38) supaya muka di separuh
  atas dan kad (y ≥ 1060) tak tutup mulut/dagu. POV/walkaround: zoom biasa, kad tetap di bawah.

## Resipi
1. Ambil bahan Drive (`Raw Video`, `Music`), transcribe large-v3, potong jeda/ulangan (sasar ~200 wpm rasa).
2. Hook = soalan utama → `slam` (alpha 50) perkataan demi perkataan, kata terakhir aksen.
3. Bab → `chapters` HUD; tajuk bab besar → `slam` ringkas (1–3 perkataan).
4. Senarai/kos → `ledger`; jumlah → `counter accent flash` (jumlah sebenar + formula kecil); fakta pendek → `tag`;
   nombor penting atas muka → `brackets` + `counter`.
5. Jawapan/payoff → `slam` "JAWAPAN" → `counter` aksen sampai hujung.
6. Render: `python3 projects/honda-prelude/build.py final --keypoints --edl projects/<projek>/edl.py ...`
   (export TikTok standard automatik). Terus render, hantar link GitHub.
