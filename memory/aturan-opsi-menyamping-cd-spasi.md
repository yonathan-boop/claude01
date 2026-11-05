---
name: aturan-opsi-menyamping-cd-spasi
description: "Aturan baku format opsi pilihan ganda menyamping 2x2 (a, b pakai tab hanging; c, d wajib spasi tanpa tab)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 46537ccd-f052-4d92-a2a1-c74c63e93d79
  modified: 2026-11-05T02:35:02.842Z
---

Aturan baku layout opsi pilihan ganda menyamping 2x2 (`a-c` dan `b-d`):

1. **Opsi Kiri (`a` dan `b`):**
   - Menggunakan format: `a.\tText` dan `b.\tText`.
   - Mengikuti *hanging indent* Word pada grid `1.30 cm` (`737 twips`) dengan *first line* `-0.65 cm` (`-369 twips`).
2. **Pemisah Kolom:**
   - Menggunakan tepat 1 karakter tab `\t` setelah teks opsi `a` / `b` untuk melompat ke posisi kolom kedua (tab stop `2835 twips` / `5.00 cm`).
3. **Opsi Kanan (`c` dan `d`):**
   - **WAJIB MENGGUNAKAN SPASI TUNGGAL SETELAH TITIK**: `c. Text` dan `d. Text`.
   - **DILARANG KERAS MENGGUNAKAN TAB** setelah huruf `c.` atau `d.` (BUKAN `c.\tText`).
   - Alasan: Penggunaan tab setelah `c.` membuat teks melompat terlalu jauh ke kanan sehingga jarak antara huruf `c.` dengan isi kalimat opsi menjadi renggang/berantakan seperti pada bukti visual naskah.

**Skrip Acuan Baku:**
Tersimpan di Claude 01: `C:\Users\yonat\Desktop\CLAUDE\tools\editor_soal_claude01.py`.
Link terkait: [[aturan-editing-soal-sd]], [[feedback-strict-surgical-edits]], [[aturan-penamaan-file-edit-vs-ok]].
