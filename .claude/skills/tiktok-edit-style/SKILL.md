---
name: tiktok-edit-style
description: TikTok Edit Style — gaya editing video TikTok/Reels 9:16 untuk content talking-head jualan (car dealer / product walkaround) dalam Bahasa Melayu. Guna bila user minta edit raw footage jadi video TikTok, buat hook, subtitles, jump cut, motion graphics, SFX, atau minta "edit macam style aku". Mengandungi bila, kenapa dan bagaimana setiap teknik digunakan, serta pipeline ffmpeg/ASS yang boleh diulang.
---

# TikTok Edit Style

> **STATUS: PROVISIONAL (v0.1).** Skill ini ditulis TANPA reference video. Folder
> `References Video` kosong semasa skill ini dibina, jadi peraturan di bawah datang
> daripada amalan biasa editor TikTok car-dealer/talking-head Malaysia, BUKAN analisis
> editor user. Bila reference video tersedia: study dulu, kemudian kemas kini setiap
> bahagian yang bertanda `[VERIFY]` dengan nilai sebenar (font, warna, posisi subtitle,
> kadar cut, jenis SFX, gaya meme) dan buang label provisional.

## 0. Prinsip utama (kenapa)

Setiap keputusan editing mesti jawab salah satu soalan ini. Kalau tak jawab satu pun, buang.

1. **Retention:** adakah ia menghalang penonton swipe dalam 1–2 saat akan datang?
2. **Clarity:** adakah ia buat maklumat (harga, spec, feature) lebih cepat difahami?
3. **Entertainment:** adakah ia tambah personaliti atau humor yang ASLI daripada footage?

Kurang lebih baik daripada serabut. Video mesti nampak macam editor manusia yang yakin,
bukan template AI. Rule of thumb: **maksimum 1 elemen "baru" (zoom/graphic/SFX) setiap ~1.5 s**,
dan beri ruang "bernafas" (2–3 s tanpa graphic) selepas setiap momen besar.

## 1. Flow & storytelling

Struktur untuk video jualan/walkaround (60–90 s ideal untuk TikTok):

| Bahagian | Masa | Tujuan | Isi |
|---|---|---|---|
| HOOK | 0–3 s | Hentikan scroll | Visual paling "wow" + claim paling kuat (harga / "first in Malaysia" / rare) |
| CONTEXT | 3–10 s | Beritahu apa ni & kenapa peduli | Nama produk, harga, 1 selling point |
| PROOF / TOUR | 10–60 s | Bina keinginan | Feature ikut susunan fizikal (luar → dalam → belakang), setiap feature ≤ 6 s |
| PAYOFF | akhir | Momen "seksi" disimpan | Feature paling unik (open loop yang dijanji di awal) |
| CTA | 3–5 s terakhir | Convert | Ulang harga + arahan jelas (DM / komen / link) |

- **Open loop:** dalam 10 s pertama, janji sesuatu yang datang kemudian ("tunggu sampai
  tengok bahagian belakang dia"). Ia beri sebab untuk tonton sampai habis.
- **Susun semula footage** kalau feature terbaik ada di hujung raw: ambil 1–2 s visual
  feature itu untuk HOOK (flash-forward), kemudian main penuh di PAYOFF.
- **Jangan ubah maksud asal.** Susun semula hanya ayat yang berdiri sendiri; jangan
  sambung separuh ayat daripada tempat berlainan sampai jadi claim baru.
- Kalau presenter ragu-ragu tentang fakta ("kalau tak silap saya"), kekalkan keraguan itu
  dalam subtitle (atau buang ayat). Jangan tukar jadi fakta pasti.

## 2. Hook (0–3 s)

Tiga lapis serentak:

- **Visual hook:** shot paling dinamik/unik (contoh: but belakang terangkat bersama cermin),
  punch-in zoom 110–120% dengan sedikit gerak (slow push) supaya frame pertama dah "hidup".
- **Verbal hook:** ayat terkuat presenter, potong terus ke isi (buang "Assalamualaikum"
  ke bawah atau buang terus; salam boleh kekal sebagai 0.5–1 s selepas hook kalau sopan diperlukan).
- **Text hook:** 2–5 perkataan besar di tengah-atas frame (safe zone), contoh
  "FIRST IN MALAYSIA 🇲🇾" atau "RM250K JE?!". Masuk dengan pop/scale-overshoot pada frame 0,
  keluar selepas 2–3 s.

Kenapa: TikTok tentukan nasib video dalam ~1.5 s pertama. Frame pertama mesti dah ada
gerak + text + suara; tiada fade-in, tiada logo intro.

## 3. Pacing & jump cuts

- **Buang semua jeda > ~0.25 s**, nafas panjang, "emm", "so", "macam tu", ayat berulang,
  salah sebut + pembetulan (contoh "Honda Civic.. sorry" → simpan versi betul sahaja).
- **Purata shot length 1.5–3 s** `[VERIFY]`. Kalau satu take panjang tanpa potong, pecahkan
  dengan punch-in zoom pada setiap jump cut.
- **Zoom-on-cut (jump cut punch-in):** selang-seli skala 100% ↔ 112–125% pada setiap cut
  dalam take yang sama. Ia sembunyikan jump cut (mata baca sebagai "angle baru") dan
  beri tenaga. Jangan zoom pada SETIAP cut: corak 1-1-0 atau 1-0-1 lebih natural.
- **Emphasis punch:** zoom snap ke 130–140% di muka/objek pada perkataan kunci (harga,
  "cantik gila"), tahan 0.5–1 s, kembali.
- **Detail cutaway (B-roll dari footage 4K):** bila presenter sebut detail (rim, caliper,
  door handle, lampu), crop masuk ke detail itu daripada source 4K (crop 2× tanpa hilang
  kualiti pada output 1080p). Ini "B-roll percuma" yang paling sesuai bila tiada B-roll lain.
- Audio: crossfade 10–20 ms di setiap cut untuk elak "klik"; jangan pernah potong
  di tengah perkataan.

## 4. Subtitles

- **Gaya:** 1–4 perkataan setiap paparan, bold sans-serif tebal (Montserrat ExtraBold /
  Inter Black / Poppins Bold) `[VERIFY font]`, HURUF BESAR, putih dengan outline hitam 6–8 px
  + drop shadow lembut.
- **Highlight keyword:** perkataan kunci (harga, nombor, nama model, kata sifat kuat)
  warna kuning/brand `[VERIFY warna]`, sedikit lebih besar. Hanya 1 keyword setiap paparan.
- **Animasi:** setiap chunk masuk dengan pop kecil (scale 85%→105%→100% dalam ~120 ms).
  Tiada typewriter, tiada bounce berlebihan.
- **Posisi:** tengah horizontal, ~62–70% dari atas (atas caption TikTok, bawah muka).
  Elak 15% bawah dan 10% kanan (UI TikTok).
- **Ketepatan:** semak setiap perkataan. Betulkan istilah teknikal (Prelude, e:HEV,
  paddle shifter, PS, RM). Bahasa campur Melayu–Inggeris dikekalkan seperti dituturkan.
  Nombor ditulis sebagai angka (RM250,000; 19 inci).

## 5. Motion design

Guna hanya bila ia menambah clarity:

- **Spec card / callout:** maklumat bernombor (kuasa, harga, saiz rim) → kad kecil
  dengan latar gelap separa lutsinar, masuk slide+pop, kekal semasa ayat itu, keluar fade cepat.
- **Price reveal:** harga = momen terbesar. Text besar tengah, warna highlight,
  pop + shake kecil, SFX "ka-ching"/ding.
- **Arrow / circle highlight:** tunjuk feature kecil yang mudah terlepas pandang (door handle,
  tulisan pada caliper). Jarang (≤ 2 kali setiap video).
- **Section label:** label kecil di atas ("EXTERIOR", "INTERIOR", "BELAKANG") bila lokasi
  berubah, bantu penonton tahu progres tour.
- **Tracking/masking:** hanya bila text perlu "melekat" pada objek bergerak. Kalau tiada
  tracker, letak text di kawasan statik frame dan jangan pura-pura track.
- Easing: ease-out untuk masuk, ease-in untuk keluar. Durasi animasi 100–250 ms.

## 6. Sound design

- **Suara presenter = keutamaan.** Normalize ke ~-14 LUFS (TikTok), high-pass 80 Hz,
  compressor ringan, de-ess kalau perlu. Ruang gudang yang bergema: kurangkan dengan EQ,
  jangan sampai suara jadi nipis.
- **Muzik latar** (kalau ada): -20 hingga -24 dB di bawah suara, duck lagi semasa ayat penting,
  naik sedikit di jeda/transisi. Kalau user tak mahu muzik, jangan tambah. Mereka akan guna
  trending sound dalam app.
- **SFX: setiap satu terikat pada event visual:**
  - whoosh → zoom besar / tukar bahagian (section change)
  - pop → spec card / text hook masuk
  - ding / ka-ching → harga
  - riser pendek → sebelum payoff
  - record-scratch / "bruh" → blooper atau salah sebut (comedic)
  Level SFX -12 hingga -18 dB relatif suara; jangan tindih perkataan kunci.
- Maksimum ~1 SFX setiap 3–4 s secara purata. SFX berterusan = rasa murahan.

## 7. Entertainment (memes, troll, reaction)

- Humor mesti datang daripada **momen sebenar** dalam footage:
  - salah sebut ("Honda Civic.. sorry") → boleh dikekalkan sebagai blooper ringkas dengan
    freeze-frame/zoom muka + text "eh salah 😅" + SFX, KALAU ia tak mengganggu flow.
    Kalau video dah panjang, buang terus.
  - reaksi spontan ("cantik gila") → punch-in muka + highlight text.
- Meme clip luar hanya bila user sediakan aset; jangan masukkan meme generik secara rawak.
- Satu momen komedi setiap ~20–30 s sudah cukup untuk video jualan; jangan ganggu kredibiliti
  penjual.

## 8. CTA & ending

- Ulang harga + 1 arahan (DM / komen "NAK" / klik profile).
- Akhiri pada frame yang boleh loop ke hook (contoh: shot kereta), bukan pada skrin hitam.
- Tiada end-card panjang; 2–3 s maksimum.

## 9. Technical spec

- Output 1080×1920 (9:16) minimum, MP4 H.264 High, CRF 16–18 / ~16–20 Mbps,
  AAC 320 kbps 48 kHz, frame rate ikut source (contoh 60 fps).
- iPhone HDR (HLG/Dolby Vision, BT.2020): tukar ke SDR BT.709. Uji: `scale` dengan
  `in_color_matrix=bt2020:out_color_matrix=bt709` beri hasil paling natural untuk
  footage iPhone HLG; tonemap hable/mobius cenderung pudar/oren. Sentiasa banding frame.
- Source 4K → gunakan resolusi lebih untuk punch-in/detail crop tanpa hilang kualiti.
- Preview: 720×1280 cukup untuk review; final render dari source asal.

## 10. Workflow (bagaimana)

1. **Study reference** (bila ada): contact sheet frame (`fps=1/2,tile`), ukur shot length
   (`select='gt(scene,0.3)'`), kaji subtitle (font, warna, posisi), senarai SFX + bila ia
   berbunyi, dan update `[VERIFY]` dalam skill ini.
2. **Ingest raw:** semak orientation (displaymatrix), HDR, fps. Buat mezzanine SDR 1080×1920.
3. **Transcribe:** Whisper (`large-v3`, `language="ms"`, `word_timestamps=True`,
   `condition_on_previous_text=False`, JANGAN beri `initial_prompt` sebab ia boleh
   menyebabkan halusinasi berulang). Betulkan transcript secara manual.
4. **Paper edit:** senarai ayat yang disimpan (dengan timestamp perkataan), susunan baru,
   hook, open loop. Tandakan setiap zoom/graphic/SFX bersama SEBABnya.
5. **Build:** EDL → potong & zoom (ffmpeg crop/scale per segment dari source 4K),
   ASS subtitles + motion graphics, SFX track, mix audio, render preview.
6. **Review:** semak preview frame-by-frame di cut, semak subtitle vs audio, semak
   tiada glitch. Tunjuk kepada user. **Jangan render final sebelum user approve.**
7. **Final:** render dari source 4K pada spec di §9. Semak durasi, sync, loudness.

Pipeline rujukan untuk projek pertama: `projects/<nama>/edit.py` dalam repo ini.
