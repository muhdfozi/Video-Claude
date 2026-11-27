# Honda Prelude 2025: Editing Timeline (Preview v2)

- **Raw:** `IMG_1031.MOV`, satu take 2:21, 4K HDR (HLG) 60 fps, vertical
- **Hasil edit:** **96.8 s** (dipotong daripada 141.6 s), 9:16
- **Preview:** 720×1280 30 fps. Final nanti 1080×1920 60 fps daripada source 4K, selepas approve.
- **Skill:** `.claude/skills/tiktok-edit-style/SKILL.md` (PROVISIONAL, sebab tiada reference video)
- **Muzik:** tiada (ikut arahan). SFX semua di-synthesize sendiri (`make_sfx.py`).
- **Loudness:** ~-15 LUFS integrated (suara di-EQ, compress, normalize)

## Struktur

| Masa | Bahagian | Isi | Editing |
|---|---|---|---|
| 0:00–0:03 | **HOOK** | "First in Malaysia, Honda Prelude tahun 2025…" | Flash-forward: B-roll bonet belakang + cermin terangkat (dari 1:44 raw), text hook "FIRST IN MALAYSIA" + pop |
| 0:03–0:08 | Intro | dalaman hitam, salam, "Fauzi" | whoosh balik ke presenter, name tag FAUZI |
| 0:08–0:14 | Scarcity + harga | "sangat-sangat jarang", "RM250,000 sahaja" | punch-in pada "sangat-sangat", **price card** + SFX cash |
| 0:14–0:21 | Spec ringkas | 2 pintu, coupe, mileage rendah, model baru, recon imported | jump cut + zoom selang-seli |
| 0:21–0:31 | Hybrid & kuasa | enjin hidup/mati, motor 181 PS, enjin 141 PS | spec card "2.0 HYBRID", "MOTOR 181 PS", "ENJIN 141 PS" |
| 0:31–0:41 | **EKSTERIOR** | rim, caliper biru bertulis Prelude, gloss black, 19-20 inci | chip section + whoosh, crop detail 4K ke caliper/rim, spec card RIM |
| 0:41–0:46 | Pintu | door handle "ala-ala kereta mewah" | zoom ke door handle, balik wide bila pintu dibuka |
| 0:46–1:00 | **INTERIOR** | 4 tempat duduk (2 depan selesa), gearbox S+, paddle shifter, meter digital | jump cut terus duduk dalam kereta, zoom ke stereng/meter |
| 1:00–1:04 | Kekurangan | tiada frameless | dikekalkan sebab kejujuran bina trust |
| 1:04–1:14 | **PAYOFF** | "paling seksi bahagian belakang": bonet + cermin terangkat | riser + chip, shot dibiar berterusan (tiada cut) supaya angkatan bonet nampak penuh, whoosh ikut gerak bonet |
| 1:14–1:22 | Fakta + ruang | platform Civic FL5, ruang but, kerusi boleh dilipat | crop ke ruang but |
| 1:22–1:25 | **Blooper** | "Honda Civic… sorry" | punch-in muka + "EH? CIVIC??" + SFX scratch |
| 1:25–1:33 | CTA | "Honda Prelude 2025… RM250,000 sahaja, belum lagi on the road" | price card kedua + cash |
| 1:33–1:37 | Ending | taillight bercantum, "cantik gila" | crop taillight, punch ke muka, CTA "DM UNTUK INFO LANJUT". Ending kereta dari belakang boleh loop ke hook |

## Apa yang dibuang (dan kenapa)
- "Hari ni kita ada sebuah unit Honda Prelude 2025 2.0 Hybrid": ulang hook. Maklumat "2.0 Hybrid" dipindah ke spec card.
- "kalau korang boleh dengar sedikit": bunyi enjin tak jelas dalam rakaman.
- **"kalau ditambahkan dah 200 lebih, 300 lebih juga kan":** kuasa motor dan enjin hybrid tak dicampur macam tu, jadi claim "300 lebih" boleh mengelirukan pembeli. *Kalau kau nak kekalkan, beritahu aku.*
- "design preload", "full,", "meter meter", "ok", ulangan "kereta 2 pintu", 4 s panjat masuk kereta, "kalau kita nak" (jalan ke bonet), penjelasan berulang "sebab Civic FL5 bonet pun terangkat", semua jeda > 0.28 s.

## Pembetulan subtitle (Whisper vs sebenar)
preload → **Prelude**, S-Plus → **S+**, pedal → **paddle**, "dalam mana" → **dalamannya**, "anda kata" → **andai kata**, "Honda Road" → **on the road** (disahkan dengan transcribe kedua), bagian → bahagian.

## Perlu kau sahkan
1. CTA "DM UNTUK INFO LANJUT": nak tukar ke nombor telefon, nama showroom, atau "komen NAK"?
2. Fakta yang presenter sendiri tak pasti ("kalau tak silap saya"): 181/141 PS, rim 19-20 inci, platform Civic FL5. Aku kekalkan ayat ragu-ragu tu dalam subtitle, tapi spec card tunjuk nombor tu.
3. Blooper "Honda Civic… sorry": nak kekal (comedic) atau buang?
