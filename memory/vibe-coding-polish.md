---
name: vibe-coding-polish
description: "Standar keterbacaan kode (variabel deskriptif, komentar why/intent, ringkasan fungsi manusiawi) pasca kode jalan"
metadata:
  node_type: memory
  type: feedback
  originSessionId: a284f2d5-5d3c-471b-a318-bdbad6dd724a
  modified: 2026-11-03T14:32:44.253Z
---

Kode jalan saja tidak cukup. AI wajib mencegah cognitive debt saat pemeliharaan kode di masa depan.

**Standar Wajib Pasca-Generasi:**
1. **Variabel Deskriptif**: Hindari nama generik (`data`, `temp`, `val`, `res`). Gunakan nama spesifik konteks (contoh: `daftarProdukAktif`).
2. **Komentar Why/Intent**: Komentar hanya untuk menjelaskan alasan arsitektural/tujuan (*why*), bukan menceritakan ulang sintaks kode.
3. **Ringkasan Fungsi Manusiawi**: Berikan 1 baris penjelasan alur fungsi dalam bahasa manusia di atas fungsi.
4. **Surgical Scope**: Penyesuaian nama dan dokumentasi dilarang merusak atau merombak struktur logika yang sudah stabil.

**Why:** Mencegah kode tidak terbaca saat dibuka kembali di masa depan.
**How to apply:** Terapkan otomatis pada setiap pembuatan fungsi atau refactor tanpa perlu diminta ulang.
