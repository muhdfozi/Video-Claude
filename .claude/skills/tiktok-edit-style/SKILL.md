---
name: tiktok-edit-style
description: TikTok Edit Style — gaya editing video TikTok/Reels 9:16 user ini untuk content talking-head (jualan kereta / produk / tutorial) dalam Bahasa Melayu. Guna bila user minta edit raw footage jadi video TikTok, buat hook, keypoint text, jump cut, motion graphics, SFX, atau minta "edit macam style aku". Mengandungi bila, kenapa dan bagaimana setiap teknik digunakan, serta pipeline ffmpeg/ASS yang boleh diulang.
---

# TikTok Edit Style (v1.0)

Sumber gaya:
1. **Reference video user** (`References Video/v1c044g50000dbenm3fog65ur7ujrt4g.mp4`, 88 s, talking-head
   tutorial). Dikaji: contact sheet 1 fps, scene detection, transcript + kadar cakap, spektrum audio.
2. **Feedback user pada projek pertama (Honda Prelude):**
   - "Keypoint saja highlight. Subtitles tak perlu."
   - "Warna video yang asal": jangan tukar atau grade warna footage.
   - "Yang lain dah cantik": hook flash-forward, jump cut + zoom, kad harga/spec, label section,
     SFX dan CTA diterima.

Peraturan bertanda **[USER]** datang terus daripada feedback user. Jangan langgar tanpa tanya.

## 0. Prinsip (kenapa)

Setiap elemen mesti menambah satu daripada **retention**, **clarity** atau **entertainment**.
Reference sangat bersih: satu idea di skrin pada satu masa, banyak ruang kosong, tiada efek berlonggok.
Kalau ragu, buang. Video mesti nampak macam editor manusia yang yakin, bukan template AI.

## 1. Apa yang reference buat (pemerhatian)

| Aspek | Reference |
|---|---|
| Pacing cakap | ~204 perkataan/minit, hampir tiada jeda > 0.3 s (semua jeda dibuang) |
| Shot | Satu framing talking-head, jump cut berterusan; sesekali punch-in kecil |
| Hook | 0–4 s: tajuk besar ("✳ Claude") + kata-kata kecil muncul satu-satu di atas; ayat terus ke masalah penonton ("tapi kau masih *lost*") |
| Teks | **Bukan subtitle penuh.** Hanya keyphrase terpilih, *sentence case* (bukan ALL CAPS), 1 kata kunci berwarna **biru**, kadang-kadang kata aksen dalam *serif italic biru* ("Claude *Pro*", "*lawa-lawa*", "pandai *edit*") |
| Kinetic word | Satu perkataan besar (contoh "install", "wajib") untuk momen paling penting, hitam atas latar cerah atau biru |
| Sticker | Label putih bucu bulat, teks gelap tebal, senget ±2–3°, bayang lembut ("Siap dalam 20–30 minit", "Weekly habis hari ke-6") |
| UI card | Kad gelap gaya macOS (bucu bulat, header 3 titik) yang beranimasi (taip prompt, baris muncul, highlight biru bergerak, progress bar terisi) di 1/3 bawah |
| Progress | Label kecil kiri atas "step 1 / 5" / "bonus" + garis progres biru nipis merentas atas |
| Emphasis | Bracket sudut "viewfinder" berkelip pada momen penting |
| Warna | Natural, hangat, tiada grading berat |
| Audio | Muzik latar berterusan perlahan di bawah suara; suara padat dan jelas |
| Ending | Kad CTA ("Share link, biar aku tengok" + butang pill merah "Share hasil kau"), kemudian end card |

## 2. Flow & storytelling

| Bahagian | Masa | Tujuan |
|---|---|---|
| HOOK | 0–3 s | Visual paling kuat + claim paling kuat + text hook |
| CONTEXT | 3–10 s | Apa ni, kenapa peduli, harga/outcome awal |
| BODY | bahagian demi bahagian | Setiap point ≤ 6 s, label section/progress bila tukar bahagian |
| PAYOFF | akhir | Benda paling "wow" disimpan (open loop dari hook) |
| CTA | 3–5 s terakhir | Satu arahan jelas |

- **Open loop:** tunjuk payoff sekejap di hook (flash-forward), bayar balik di hujung.
- **Susun semula** hanya ayat yang berdiri sendiri. Jangan ubah maksud asal.
- Kekalkan keraguan presenter ("kalau tak silap saya"). Buang claim yang boleh mengelirukan
  (contoh jumlah kuasa hybrid yang dicampur salah) dan beritahu user.

## 3. Hook (0–3 s)

- **Visual:** shot paling dinamik, sudah bergerak pada frame pertama (slow push 1.3→1.45×).
- **Verbal:** ayat paling kuat, tanpa salam dahulu (salam boleh selepas hook, ≤ 2 s).
- **Text:** 2–4 perkataan besar di 1/3 atas; pop-in; keluar selepas 2–3 s.

## 4. Pacing & jump cuts

- Buang semua jeda > ~0.28 s, filler, ayat berulang, salah sebut + pembetulan
  (kecuali dijadikan momen lawak, lihat §8). Sasar rasa padat macam reference (~200 wpm).
- Setiap potongan yang tinggal ≥ 0.35 s (potongan lebih pendek nampak macam glitch).
- **Zoom-on-cut:** selang-seli 100% ↔ ~110% pada jump cut dalam take sama.
- **Emphasis punch:** 1.2–1.4× ke muka pada perkataan kunci.
- **Detail crop dari source 4K** sebagai B-roll (caliper, door handle, stereng, lampu).
- **Footage POV (tiada muka):** zoom sasar kereta/objek, bukan muka. Shot "tangan + kereta jauh"
  → crop 1.8–2.2× ke kereta dari source 4K. Hook guna B-roll sudut terbaik kereta.
- Audio fade 8 ms di setiap cut. Jangan potong tengah perkataan. Sahkan dengan
  transcribe semula audio hasil edit.

## 5. Teks atas skrin — KEYPOINT SAHAJA [USER]

- **Tiada subtitle berterusan.** Hanya keypoint: maklumat yang penonton patut ingat
  (harga, spec bernombor, feature unik, kelebihan/kekurangan, payoff).
- **Gaya sticker (reference):** label putih bucu bulat (radius ~22 px pada 1080 lebar), teks
  Inter Display Bold ~58 px *sentence case*, warna dakwat gelap `#15171A`, **satu** kata kunci biru
  `#4F6EF7`, senget selang-seli −2.5° / +2°, bayang lembut, pop-in (70%→108%→100% dalam 160 ms),
  fade-out 120 ms. Posisi tengah, ~66% tinggi frame (di atas UI caption TikTok).
- Kekerapan: ~1 keypoint setiap 4–6 s, durasi 1–3 s, tidak bertindih.
- Ayat keypoint ≤ 5 perkataan, guna bahasa presenter (jangan cipta claim baru).
- Elemen besar sedia ada yang user dah suka: text hook (Montserrat Black, putih + kuning),
  **kad harga** kuning senget + pill "SAHAJA"/"BELUM ON THE ROAD", **kad spec** gelap slide-in
  dari kanan (label putih + nilai kuning), **label section** pill gelap di atas, name tag kuning,
  CTA pill kuning berdenyut.
- Belum diguna tapi ada dalam reference (cuba pada projek akan datang, tanya user dulu):
  progress bar "step x / y", kinetic word besar, UI card gelap beranimasi, bracket viewfinder,
  aksen serif italic biru.

## 6. Warna — KEKALKAN ASAL [USER]

- **Jangan grade dan jangan tukar colour space.** Footage iPhone HDR (HLG, BT.2020, 10-bit)
  dikeluarkan semula sebagai HLG BT.2020 10-bit (HEVC Main10, `hvc1`, MP4). Pipeline: decode
  ke `rgb48le` (matrix bt2020), zoom/crop dalam 16-bit, overlay ASS terus atas `rgb48le`, encode
  balik dengan matrix bt2020 + tag `arib-std-b67`. Sahkan: purata beza piksel output vs source < 1/255.
- Grafik dalam HLG: putih grafik ~75–80% isyarat (BT.2408), bukan 100%, supaya teks tak menyilaukan
  di skrin HDR. Fungsi `C()` dalam `build.py` skala semua warna ASS.
- Footage SDR biasa: kekalkan BT.709 apa adanya.
- Jangan guna tonemap hable/mobius: hasilnya pudar/oren.

## 7. Sound design

- Suara keutamaan: highpass 90 Hz, denoise ringan, EQ (−2.5 dB @250 Hz, +2 dB @3.5 kHz),
  compressor 3:1, loudnorm ~-15 LUFS, limiter.
- **Muzik:** reference ada muzik latar berterusan perlahan. Untuk projek Honda Prelude user pilih
  **tiada muzik**. Bila user letak fail dalam folder Drive `Music`, guna fail itu.
  - Fail panjang/kompilasi: analisis tenaga + tempo setiap 30 s (librosa), cari sempadan
    movement (silencedetect −40 dB, ≥1 s), mula bahagian bertenaga **di permulaan frasa/movement**.
    Jangan mula tengah frasa.
  - Bed: loudnorm −27 LUFS, fade-in 0.25 s, fade-out 1.5–1.8 s di hujung video.
  - **Ducking** bawah suara: −7 dB bila presenter bercakap (attack cepat, release perlahan).
  - Set `MUSIC = dict(file=…, start=…, lufs=-27, duck_db=7)` dalam `edl.py`.
- **SFX** (synth: `make_sfx.py`), setiap satu terikat pada event visual:
  whoosh = tukar section / cut dari B-roll, pop = kad/text masuk, cash = harga,
  riser = sebelum payoff, scratch = blooper. Purata ≤ 1 SFX setiap 3–4 s. Sticker keypoint tiada SFX.

## 8. Entertainment

- Humor daripada momen sebenar sahaja: salah sebut ("Honda Civic… sorry") → punch-in muka +
  teks "EH? CIVIC??" senget bergoyang + scratch. Satu momen lawak setiap ~20–30 s sudah cukup.
- Meme luar hanya jika user beri aset.

## 9. CTA & ending

- Ulang harga/outcome + satu arahan (DM / komen / share). Akhiri pada frame yang boleh loop ke hook.

## 10. Technical spec

- 1080×1920 (9:16), fps ikut source (60), MP4.
- HDR source: HEVC Main10 HLG, CRF 18, VBV max 12 Mbps, AAC 320k.
  SDR source: H.264 High CRF 16, AAC 320k.
- Kalau user perlu download dari GitHub: fail mesti < 100 MB. App Claude tak boleh download
  file card; Google Drive tak boleh di-upload tanpa token user.

## 11. Workflow

1. Download bahan (Drive: `gdown` untuk senarai, `drive.usercontent.google.com/download?id=…&confirm=t` untuk fail besar).
2. Study reference: contact sheet, scene detect, transcript (wpm, jeda), spektrum audio. Kemas kini skill ini.
3. Ingest raw: semak rotation, HDR, fps. Buat mezzanine SDR 1080p untuk preview pantas.
4. Transcribe: Whisper `large-v3`, `language="ms"`, `word_timestamps=True`,
   `condition_on_previous_text=False`, **tanpa** `initial_prompt` (ia sebabkan halusinasi berulang).
5. Paper edit dalam `edl.py`: segmen (audio in/out, video override, zoom keys, `why`),
   GRAPHICS, KEYPOINTS. Semak dengan `build.py plan`.
6. Preview (`build.py preview`), semak frame + transcribe semula audio. Tunjuk user. Jangan render final sebelum approve.
7. Final: `build.py final --hdr --keypoints` (atau tanpa `--hdr` untuk SDR). Sahkan spec, warna, loudness.

Pipeline rujukan: `projects/honda-prelude/` (build.py, make_sfx.py, face_track.py). Setiap projek ada `edl.py` sendiri: `python3 projects/honda-prelude/build.py final --hdr --keypoints --edl projects/<projek>/edl.py ...`. Contoh: `projects/honda-prelude/edl.py` (presenter on-camera), `projects/honda-jade/edl.py` (POV + muzik).
