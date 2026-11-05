---
name: editor-soal-claude01
description: Spesifikasi resmi engine editor naskah soal ujian Word milik Claude 01 versi 00.1
metadata:
  node_type: memory
  type: project
  originSessionId: 46537ccd-f052-4d92-a2a1-c74c63e93d79
  modified: 2026-11-05T02:48:13.097Z
---

# Engine Editor Soal Ujian Claude 01 (Versi 00.1)

Engine resmi penyunting naskah soal ujian Word jenjang SD Methodist-11 milik sistem **Claude 01 (Node 01)**.

- **Berkas Eksekusi Utama:** `C:\Users\yonat\Desktop\CLAUDE\tools\editor_soal_claude01.py`
- **Cadangan Preservasi:** `C:\Users\yonat\.claude\projects\C--Users-yonat\memory\editor_soal_claude01.py`
- **Versi Rilis:** `00.1`

### Fitur Baku Versi 00.1:
1. **Aturan Penamaan Anti-Label OK Liar:**
   - Unit editing **hanya berhak** menambahkan kata `edit` (`[Nama Asli] edit.docx`).
   - Dilarang keras menyisipkan `OK` jika berkas awal tidak memiliki `OK`.
2. **Layout Opsi Menyamping 2x2 Presisi:**
   - Opsi `a` dan `b`: `a.\tText` dan `b.\tText` (hanging indent 1.30 cm).
   - Lompat kolom: Tepat 1 elemen `<w:tab>` (posisi 5.00 cm / 2835 twips).
   - Opsi `c` dan `d`: **`c. Text` dan `d. Text`** (wajib spasi tunggal setelah titik, tanpa tab).
3. **Format Judul Romawi:**
   - Nomor romawi `I.\t`, `II.\t`, `III.\t` cetak tebal non-underline.
   - Teks judul cetak tebal bergaris bawah (*underline*).
   - Indentasi: Left 0.65 cm, Hanging 0.65 cm.
4. **Pagar Proteksi Office:**
   - Dilarang mengeksekusi `word.Quit()` agar tidak menutup jendela Word aktif pengguna.

Link terkait: [[aturan-editing-soal-sd]], [[aturan-penamaan-file-edit-vs-ok]], [[aturan-opsi-menyamping-cd-spasi]], [[feedback-larangan-word-quit]].
