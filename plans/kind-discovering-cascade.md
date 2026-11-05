# Rencana Pengujian: Penambahan Tombol 'Clear Screen' di Composer SSH

## Context
Pengguna meminta pengujian simulasi alur **Plan Mode** pada tugas nyata di Node 01.
Fitur yang akan diuji adalah penambahan tombol pintas **"Clear ⌫"** di toolbar Composer Terminal SSH (`public/ssh.html`), agar pengguna dapat membersihkan layar terminal yang penuh output dengan 1 klik tanpa harus mengetik `cls` secara manual.

## Rangkuman Pemahaman Kebutuhan
1. **Target:** File `C:\Users\yonat\dashboard\public\ssh.html`.
2. **Kebutuhan:**
   - Menambahkan tombol chip `Clear ⌫` di barisan chip composer toolbar (bersanding dengan Tab, Ctrl+C, Arrow, Enter).
   - Menambahkan fungsi handler `sendSpecialKey('clear')` yang memanggil `term.clear()` dan mengirimkan perintah `cls\r` ke PTY session.
   - Tetap mempertahankan persistensi draft dan arsitektur 0ms lag yang sudah ada.

## File yang Akan Diubah
- `C:\Users\yonat\dashboard\public\ssh.html`

## Langkah Kerja Konkret
1. **HTML Markup (`public/ssh.html` baris ~640):**
   - Tambahkan `<button type="button" class="chip-btn" onclick="sendSpecialKey('clear')" title="Bersihkan Layar (cls)">Clear ⌫</button>` ke dalam div `.composer-chips`.
2. **JavaScript Logic (`public/ssh.html` fungsi `sendSpecialKey`):**
   - Tambahkan percabangan:
     ```javascript
     else if (type === 'clear') {
       if (term) term.clear();
       dispatchTerminalInput('cls\r');
     }
     ```
3. **Verifikasi:**
   - Validasi sintaks inline JS dengan Node.js CLI.
   - Uji DOM visual menggunakan Playwright headless browser untuk memastikan tombol `Clear ⌫` muncul dan dapat diklik.
   - Pastikan status response HTTP 200 di port 8901 dan 8900.
