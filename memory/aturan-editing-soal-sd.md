---
name: aturan-editing-soal-sd
description: "Standar layout, kop surat, dan sistem self-review untuk editing naskah soal ujian SD"
metadata:
  node_type: memory
  type: project
  originSessionId: 45dd8b74-3eb6-4e92-b7eb-3cf817f031c5
  modified: 2026-10-23T13:10:21.712Z
---

# Aturan Baku Editing Naskah Soal Ujian SD (Methodist-11)

## 1. Spesifikasi Dokumen
- **Ukuran Kertas**: Folio / F4 (`21.59 cm x 33.02 cm` / `8.5 x 13.0 inci`).
- **Margin Halaman**: Atas/Bawah `0.5 cm`, Kiri/Kanan `1.0 cm` di seluruh sections.
- **Penamaan File**:
  - File draft/kerja: Tetap nama asal (misal `Agama 1 Rio OK.docx`).
  - Setelah fix dan di-ACC user: Tambahkan kata `edit` (misal `Agama 1 Rio OK edit.docx`).
- **Backup Internal**: Wajib di-backup ke internal storage Claude (`memory/backups/`) sebelum diedit. Folder kerja user harus tetap bersih.

## 2. Struktur Section & Kolom Baku
Sistem urutan kolom wajib:
1. **Kop Surat**: `1 kolom` (continuous break).
   - Gambar logo sekolah di kop surat wajib selalu ADA dan UTUH (`media/image1.png`, relasi `rId5`, dan `[Content_Types].xml` image/png).
2. **Pilihan Ganda**: `2 kolom` (continuous break).
   - Judul pertama (`Pilihan Ganda CP 1 (100%)`) wajib RAPAT dengan kop surat (space_before=0, tanpa enter).
   - Judul CP berikutnya (`CP 2`, `CP 3`): Wajib ada 1 enter kosong di atasnya.
   - Opsi jawaban dibersihkan dari trailing tabs (`\t`) dan trailing spaces.
3. **Transisi & Judul Isian**: `1 kolom` (ada enter 1 kali, judul `Isian CP ...` membentang 1 kolom utuh, continuous break).
4. **Soal Isian**: `2 kolom` (soal-soal isian mengalir dalam 2 kolom, continuous break).
5. **Esai**: `1 kolom` (ada enter 1 kali, judul `Esai` dan seluruh butir pertanyaan + garis jawaban `Jb: _____` mengalir dalam 1 kolom utuh sampai akhir dokumen).

**Aturan Keseragaman `sectPr` (Cegah Halaman Baru Paksa)**:
- Setiap section break wajib memiliki nilai `pgSz`, `pgMar` (top/bottom/left/right/header/footer), dan `docGrid` yang **100% IDENTIK**.
- Perbedaan sekecil apa pun pada header distance atau page code antar-section akan memaksa Word membuat halaman baru meskipun jenis section break sudah di-set `continuous`.

## 3. Standar Indentasi (Kelipatan 0.65 cm)
- **Judul Bagian**: `left = 0` (flush left ke margin).
- **Nomor Soal**: `left = 0.65 cm` (`369 dxa`), `hanging = 0.65 cm` (`369 dxa`). Posisi nomor di 0, teks nomor mulai di 0.65 cm.
- **Opsi Jawaban (a, b, c, d)**: `left = 1.30 cm` (`737 dxa`), `hanging = 0.65 cm` (`369 dxa`). Huruf opsi di 0.65 cm, teks opsi mulai di 1.30 cm.
- **Format Teks Opsi**: Jika tanpa penomoran otomatis, wajib berformat rapi: `a.\tisi soal`.

## 4. Sistem Self-Review (Kemandirian Kualitas)
- **Dilarang micromanage review satu per satu soal** ke user.
- Terapkan pipeline automated audit sebelum menyodorkan file:
  1. Validasi gambar logo kop surat tidak hilang.
  2. Validasi margins & ukuran F4.
  3. Validasi kontinuitas kop (kop tidak boleh terpisah ke halaman sendiri).
  4. Validasi kerapatan judul pertama dan enter pada judul berikutnya.
  5. Validasi urutan kolom: Kop(1) -> PG(2) -> Transisi(1) -> Isian(2) -> Esai(1).
  6. Validasi kelipatan indentasi 0.65 cm pada soal dan opsi.
  7. Perbaiki otomatis setiap anomali layout sebelum menyerahkan ke user.
