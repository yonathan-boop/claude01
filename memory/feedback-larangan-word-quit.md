---
name: feedback-larangan-word-quit
description: Larangan mutlak mengeksekusi word.Quit() pada Word COM karena menutup jendela Word aktif yang sedang diedit user
metadata:
  node_type: memory
  type: feedback
  originSessionId: 46537ccd-f052-4d92-a2a1-c74c63e93d79
  modified: 2026-11-05T02:09:35.770Z
---

DILARANG KERAS mengeksekusi `word.Quit()` atau `$word.Quit()` dalam skrip apa pun (Python, PowerShell, VBScript).

**Why:**
Pengguna sering bekerja paralel di Microsoft Word desktop. Perintah `word.Quit()` akan mematikan seluruh instance Word dan menutup paksa semua dokumen yang sedang dibuka/diedit pengguna, menyebabkan gangguan alur kerja dan risiko kehilangan data yang belum tersimpan.

**How to apply:**
1. Jika menggunakan Word COM untuk inspeksi atau ekspor PDF:
   - Cukup tutup dokumen yang dibuka oleh skrip: `doc.Close(False)`.
   - **JANGAN PERNAH** memanggil `word.Quit()`. Biarkan instance Word tetap berjalan atau lepaskan referensi COM tanpa `Quit()`.
2. Prioritaskan audit & inspeksi non-COM (`python-docx`, `pypdfium2`, `audit_naskah.py`) yang berjalan murni di level file disk tanpa menyentuh proses aplikasi Office pengguna.
Link terkait: [[rule-enforcement-engine]], [[feedback-strict-surgical-edits]].
