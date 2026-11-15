---
name: style-kira-detail
description: Preset editing "style kira detail" — gaya GLASS (kaca kabur minimalis, nombor berguling, kad putih) yang user approve pada video GR86 "gaji layak". Guna TERUS bila user sebut "style kira detail" (atau "kira detail"), tanpa tanya gaya lain. Sesuai untuk video kira-kira/breakdown nombor (harga, OTR, loan, gaji, spec, perbandingan) dan case study.
---

# Style Kira Detail

Bila user sebut **"style kira detail"**: edit video dengan resipi di bawah dan **terus render final**
(user tak perlu preview). Rujukan yang user approve: `exports/GR86-Gaji-Layak-GLASS-FINAL.mp4`,
EDL `projects/gr86-glass/edl.py`. Skill penuh (teknik, pipeline): `.claude/skills/tiktok-edit-style/SKILL.md` §13.

## Peraturan tetap (dari user)
- **Tiada subtitle.** Teks hanya keypoint/nombor.
- **Warna asal**: footage HDR iPhone kekal HLG BT.2020 10-bit (`--hdr`); SDR kekal SDR. Jangan grade.
- Frame rate ikut source.
- Muzik: fail dalam folder Drive `Music` (bed −28 LUFS, ducking −8 dB bawah suara). Kalau tiada, tanya.
- Hantar melalui GitHub (`exports/`, < 100 MB) + link "Download raw file". App Claude tak boleh download file card.

## Resipi
1. **Ambil bahan** dari folder Drive user (`Raw Video`, `Music`). Transcribe Whisper large-v3 (`language="ms"`,
   word timestamps, tanpa initial_prompt). Sahkan frasa yang meragukan dengan transcribe klip pendek.
2. **Potong**: buang intro salam/"hari ni saya nak share", ayat berulang, restart ayat, filler, jeda > 0.28 s.
   Hook = soalan utama video (contoh "Gaji berapa layak pakai Toyota GR86?"). Jangan ubah nombor/maksud
   presenter; kalau kira-kira dia tak konsisten, kekalkan dan beritahu user.
3. **Struktur visual** (`THEME = "glass"`, `ACCENT` = satu warna aksen, contoh merah GR `C8102E`):
   - **Hook (presenter penuh skrin)**: `counter_pill` — nombor paling besar/penting berguling naik atas pill
     gelap di dada, label kecil huruf besar di atas, soalan hook di bawah. Lepas itu `title` chip (nama subjek + soalan aksen).
   - **Bab data = panel kaca** (`GLASS` windows): presenter diblur + diputihkan; di atasnya:
     `label` (huruf kecil jarang + garis), `timeline` (pilihan/varian/langkah), `card` (baris label–nilai muncul tepat
     bila disebut; baris `"total"` berguling, warna aksen), `counter` (jumlah besar di tengah), `cards`
     (3 poin bernombor, lama jadi pudar).
   - **Antara bab = presenter penuh skrin** dengan `pill` keypoint (kata kunci warna aksen) atau `counter_pill`.
   - **Payoff/jawapan**: panel kaca terakhir dengan `counter` besar warna aksen sampai hujung video.
   - Kaca ≤ ~60% durasi; selang-seli dengan presenter. Satu elemen baru setiap 1–3 s.
4. **Zoom**: presenter 1.05–1.25×, punch 1.3× pada nombor penting (pusat muka).
5. **SFX**: klik halus untuk baris/kad, cash untuk jumlah, whoosh lembut masuk kaca. Tiada SFX lain.
6. **Render**: `python3 projects/honda-prelude/build.py final --hdr --keypoints --edl projects/<projek>/edl.py
   --src <raw> --audio <audio48k.wav> --words <transcript.json> --sfx <sfxdir> --out <out.mp4>`.
   Semak frame (kad tak tutup muka, nombor betul), loudness ~−15 LUFS, saiz < 100 MB, kemudian push.

## Sumber dengan header tertanam (dari app lain)
Kalau fail dalam `Raw Video` dah ada header/teks tetap (contoh "TOYOTA ALPHARD Z 2023 RM245,000"):
`NO_ZOOM = True`, `GLASS_TOP = 780` (kaca hanya bawah header, header kekal tajam), semua elemen kaca y ≥ ~880,
warna ikut fail (biasanya SDR → tanpa `--hdr`), audio dari raw jika lag 0. Contoh: `projects/alphard-z/edl.py`.
Video walkaround: susun semula → hook soalan → kereta + harga → features (pill laju) → kira-kira → jawapan + CTA.

## Templat EDL ringkas
```python
THEME = "glass"; ACCENT = "C8102E"; FACE = (0.47, 0.40)
SEGMENTS = [dict(id="hook", a=(t0, t1), keys=[(t0, 1.25, *FACE)], why="..."), ...]
GLASS = [
    dict(win=(a, b), items=[dict(kind="label", text="Kos on the road"),
                            dict(kind="card", title=None, rows=[(at, "Harga", "RM140,000"), (at2, "Jumlah", 145880, "total")])]),
    dict(win=(a, 999), items=[dict(kind="label", text="Jawapan"),
                              dict(kind="counter", at=at, to=4000, lab="Gaji layak", sub="...", accent=True, y=920)]),
]
OVERLAYS = [dict(kind="counter_pill", at=hook_at, dur=4.6, to=145880, lab="...", sub="Soalan hook?"),
            dict(kind="title", at=..., dur=2.0, chip="NAMA SUBJEK", accent="Soalan?"),
            dict(kind="pill", at=..., dur=2.6, text="Minimum *20%* down payment")]
MUSIC = dict(file=".../Music/<fail>", start=<awal frasa>, lufs=-28, duck_db=8, fade_out=1.8)
```
