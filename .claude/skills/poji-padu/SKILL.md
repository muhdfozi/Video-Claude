---
name: poji-padu
description: Preset editing "poji padu" — gaya "showroom malam" yang user approve pada video Toyota Alphard Z 2025: kad data skrin penuh (latar hitam, lampu sorot atas, lantai berkilat + garis ufuk, aksen champagne), perkataan latar bergaris luar, tajuk Montserrat Black bercahaya, cincin loan / cincin 1/3 gaji / odometer / checklist, lower-third besar atas footage, dan HOOK dengan tajuk besar nama kereta (font Formula1 user) DI BELAKANG kereta / kepala presenter. Guna TERUS bila user sebut "poji padu".
---

# Poji Padu

Gaya milik user, diinspirasi (struktur sahaja, bukan tiru) daripada video TikTok contoh (explainer kereta
GLA35, @ecwmotorsportsrecond). Rujukan approved: `exports/Alphard-Z-2025-POJI-PADU-FINAL.mp4`,
EDL `projects/alphard-z-2025/edl_showroom.py`, grafik `projects/honda-prelude/showroom_gfx.py`
(`THEME = "showroom"`), tajuk-di-belakang-subjek dalam `build.py` (`BEHIND`).
Peraturan umum ikut `tiktok-edit-style` + `style-kira-detail`: **preview dulu, render hanya bila user approve**,
tiada subtitle, warna asal (SDR BT.709 export TikTok), **jumlah kira = nilai sebenar**, suara studio bila diminta,
susunan hook → kereta → kira-kira → jawapan → features → CTA, hantar via GitHub `exports/`.

## Identiti
- **Palet:** hitam showroom `#0B0B0E`, putih `#F5F3EE`, SATU aksen champagne `#E6C07B` (`ACCENT`). Tiada merah/grid neon.
- **Font:** Montserrat Black tegak (tajuk/nombor), Anton bergaris luar (perkataan latar), JetBrains Mono ExtraBold
  (kicker huruf jarang, label), Inter Display (label ledger). **Hook:** font user `Formula1-Bold.ttf`
  (Drive "Font Type"; muat turun ke `/home/user/fonts_dl/f1/`, JANGAN commit fail font).
- **Kad skrin penuh (~40% video, untuk bab nombor):** latar showroom malam (lampu sorot atas + lantai berkilat +
  garis ufuk champagne + grain), kicker taip (typewriter), tajuk bercahaya + garis bawah, perkataan latar gergasi
  bergaris luar yang bergerak perlahan, foto kereta berbingkai dengan corner tick + **kilauan cahaya melintas**.
  Masuk dengan kilat champagne + whoosh + thump.
- **Elemen kad:** `counter` (berguling, champagne + glow, formula mono di bawah), `tiles` (2×2 nilai),
  `ring` (segmen = tahun loan), `fraction` (cincin 1/3 gaji), `chip`, `checklist` (✓ ikut sebutan), `ledger`.
- **Atas footage:** `lowers` — scrim gelap bawah + kicker mono + kata besar (`*kata*` = champagne) + chip;
  `odometer` untuk mileage; kotak ledger (insurans, road tax, fee) di bawah presenter.
- **HOOK (user rule):** tajuk BESAR nama kereta di bahagian atas ("TOYOTA" kecil + "ALPHARD *Z*" hampir
  penuh lebar), diletak **di belakang kereta / kepala presenter**: mask setiap frame dengan BiRefNet
  (`rembg`, model `birefnet-general-lite`, cache `work/_masks/`), latar atas digelapkan sikit, subjek kekal terang.
  Letak per shot supaya hanya bahagian bawah huruf tersorok (shot depan kereta: `bottom≈625`; presenter
  berdiri depan kereta: `bottom≈975`). Kaunter OTR + soalan hook di bawah.

## Cara guna
1. Potong & susun macam `style-kira-detail` (EDL `SEGMENTS` boleh dikongsi: `from edl import ...`).
2. EDL baru: `THEME = "showroom"`, `ACCENT = "E6C07B"`, `SHOWROOM = dict(cards=[...], lowers=[...])`,
   `BEHIND = [dict(win=(a,b), font=F1, top="TOYOTA", main="ALPHARD *Z*", bottom=..., width=1050, top_scale=0.42, dim=0.38,
   enter="slam"|"settle", exit=False|True)]`. Masa semua dalam saat SOURCE.
3. Foto untuk kad: JPG dari Drive terus, atau still dari klip HLG (`colorspace=all=bt709:iall=bt2020:itrc=bt709`).
4. Preview: `build.py preview ...` (render pertama kira mask ~10 s/frame untuk hook sahaja; selepas itu cache).
   Semak frame: tajuk boleh dibaca (jangan tersorok > ~1/3), kad tak bertindih CTA, nombor betul.
5. Final hanya bila user approve: `build.py final ...` (standard export TikTok).
- `pip install "rembg[cpu]"` menaikkan numpy ke 2.x; cv2/whisper/librosa masih OK. DeepFilterNet mungkin perlu numpy 1.x.
