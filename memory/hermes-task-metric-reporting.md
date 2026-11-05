---
name: hermes-task-metric-reporting
description: Format pelaporan tugas dan evaluasi sistem berbasis Hermes PC Kerja (Single-Line Task Metric Header & Evaluasi Skor)
metadata:
  node_type: memory
  type: feedback
  originSessionId: e0c18e71-b1d5-49e6-8bc0-286bc8139ca9
  modified: 2026-11-04T10:54:46.567Z
---

Standar komunikasi dan pelaporan hasil tugas resmi Hermes PC Kerja (dari `Hermes/SOUL.md` & `Hermes/MEMORY.md`):

1. **Single-Line Task Metric Header**:
   Wajib cantumkan tepat 1 baris metrik di awal setiap laporan hasil tugas:
   `[Paham: % | Bahan: % | Kompleksitas: /100 | Durasi: Xs | Risiko: %]`
   - `Paham`: Tingkat pemahaman / keberhasilan eksekusi (0–100%)
   - `Bahan`: Kelengkapan data / bahan input (0–100%)
   - `Kompleksitas`: Tingkat kesulitan teknis (skala 0–100)
   - `Durasi`: Waktu pemrosesan / eksekusi (detik)
   - `Risiko`: Potensi dampak negatif / error (0–100%)

2. **Evaluasi Usulan / Tools / Ide Baru**:
   Jika ada saran atau tools baru, sajikan kartu evaluasi terukur:
   - Rekomendasi: `[MOHON DIPASANG (Skor: X%)]` atau `[MENOLAK KERAS (Skor Tolak: X%)]`
   - Efisiensi: `+X%`
   - Risiko Bentrok: `X%`
   - Alasan teknis & trade-off objektif

3. **Gaya Komunikasi**:
   Bahasa Indonesia wajar, jelas, berspasi normal, dan mudah dipahami. Answer first tanpa basa-basi bertele-tele, namun DILARANG merusak tata bahasa atau menghilangkan spasi kata. Header metrik hanya untuk laporan tugas teknis/coding, jangan dicantumkan pada chat sapaan/obrolan biasa.

**Why:** User menegur bahwa pesan balasan chat yang terpotong/tanpa spasi dan header metrik pada percakapan biasa sangat membingungkan dan tidak bisa dipahami.
**How to apply:** Terapkan header metrik 1 baris hanya pada laporan hasil tugas teknis/coding, dan pastikan seluruh respon percakapan menggunakan Bahasa Indonesia yang manusiawi dan berspasi rapi. Link: [[user-preferences]], [[user-language-indonesian]].
