# Rencana Perbaikan: Tampilan Terminal SSH Server YN di HP (Mobile Layout & PTY Sync)

## Validasi Pemahaman Inti (Karpathy Rule)
Pengguna melaporkan dan melampirkan screenshot (`img_1793833811471.jpg`) bahwa tampilan terminal web SSH (`https://serveryn.my.id/ssh`) di HP (smartphone portrait) berantakan:
1. Teks terpotong di tengah kata (`TASK OBSERVE` terpotong ke baris baru `R AKTdan`, `konte` terpotong ke `ks sesi.`).
2. Garis divider TUI dan status bar saling menimpa/tumpang tindih (`__________ash`, `[ry "refactor <filepath>"`).
3. Tombol scroll melayang di sebelah kanan menutupi teks terminal.
4. Ukuran font di HP terlalu besar (13px) dan kontrol pengatur ukuran font hilang di tampilan HP.

---

## Analisis Akar Masalah (Root Cause Analysis)

Setelah pelacakan sistematis pada `dashboard/services/terminal-hub.js` dan `dashboard/public/ssh.html`:

1. **Akar Masalah Utama: PTY Columns Dipaksa 100 Cols di Backend**
   - Di `dashboard/services/terminal-hub.js` baris 117–120:
     ```javascript
     clampCols(cols) {
       const val = parseInt(cols, 10);
       if (isNaN(val) || val < 80) return 100;
       return Math.min(val, 300);
     }
     ```
   - Di layar HP portrait (lebar ~390–412px), xterm.js mengukur lebar kontainer dan menghasilkan ~42–46 kolom.
   - Karena `val < 80`, backend **memaksa ukuran PTY menjadi 100 kolom**.
   - Akibat fatal: Proses CLI (Claude Code, cmd.exe, PowerShell) me-render baris sepanjang 100 karakter. Ketika string 100 karakter dikirim ke xterm HP (yang lebarnya hanya 44 kolom), xterm memecah 1 baris menjadi 2-3 baris fisik.
   - Saat Claude Code mengirim kode ANSI cursor-up (`\x1b[1A`) untuk memperbarui status/prompt, kursor hanya naik 1 baris fisik (bukan 1 baris logis), sehingga mendarat di tengah teks sebelumnya dan menimpa karakter (`__________ash`).

2. **Frontend `ssh.html` Memblokir Resize jika Kolom < 60**
   - Di `ssh.html` baris 1213:
     ```javascript
     if (ws && ws.readyState === WebSocket.OPEN && term && term.cols >= 60 && term.rows >= 10)
     ```
   - Karena di HP `term.cols` bernilai ~44 (kurang dari 60), frontend menolak mengirim event `resize` ke server.

3. **Kontrol Font Hilang di HP & Ukuran Font Terlalu Besar**
   - Di `ssh.html` CSS `@media (max-width: 600px)`:
     ```css
     .font-stepper { display: none !important; }
     ```
   - Default font `13px` di layar HP hanya memuat ~44 karakter.
   - Pengguna HP tidak memiliki cara untuk mengecilkan font (misalnya 10px–11px yang bisa memuat 65–75 kolom) agar terminal lebih lega dan nyaman dibaca.

4. **Tombol Navigasi Scroll Melayang (`.mobile-scroll-nav`) Menutupi Teks**
   - Posisi `.mobile-scroll-nav` berada di `position: absolute; right: 16px; bottom: 20px;` tanpa ada padding gutter di sisi kanan terminal.
   - 4 tombol scroll (`[⤒] [▲] [▼] [⤓]`) selebar 36px menutupi 5–7 karakter di ujung kanan setiap baris.

5. **Gesture Swipe Touch Mengirim Tombol Panah (Arrow Keys) Liar**
   - Di `ssh.html` baris 1780–1794, saat buffer dianggap alternate/baseY=0, usapan layar diubah menjadi `\x1b[A` (Up) dan `\x1b[B` (Down), yang memicu history navigasi prompt Claude Code secara tidak sengaja saat pengguna hanya ingin membaca teks.

---

## Rencana Perbaikan Bedah Kode (Surgical Implementation)

### 1. Perbaikan Backend PTY Hub (`dashboard/services/terminal-hub.js`)
- Ubah `clampCols` agar mendukung lebar layar mobile secara natural:
  ```javascript
  clampCols(cols) {
    const val = parseInt(cols, 10);
    if (isNaN(val) || val < 20) return 80; // Batas minimal realistis 20 kolom (HP portrait)
    return Math.min(val, 300);
  }

  clampRows(rows) {
    const val = parseInt(rows, 10);
    if (isNaN(val) || val < 5) return 24; // Batas minimal realistis 5 baris
    return Math.min(val, 120);
  }
  ```
- **Catatan Proteksi Zero-Downtime:** Perubahan file ini disimpan di disk dan akan aktif otomatis saat restart server berikutnya tanpa memutus sesi ConPTY aktif saat ini.

### 2. Perbaikan Frontend Web Terminal (`dashboard/public/ssh.html`)
- **A. Izinkan Resize Kolom Mobile:**
  - Hapus batasan artifisial `term.cols >= 60` pada `handleResize()`. Ganti dengan `term.cols >= 20 && term.rows >= 5`.
  - Pastikan event `resize` dan `attach` mengirimkan ukuran kolom xterm yang sesungguhnya ke server.

- **B. Tampilkan Kontrol Font Stepper di Header Mobile:**
  - Pindahkan atau aktifkan `.font-stepper` di header mobile agar pengguna HP bisa langsung menekan tombol `A-` dan `A+`.
  - Sesuaikan default font untuk layar mobile: jika lebar layar `<= 480px` dan belum ada preferensi tersimpan, set default font ke `11px` (nyaman dibaca di layar HP resolusi tinggi dan langsung memberikan 65–70 kolom).

- **C. Tata Letak Floating Scroll Navigasi & Right Gutter:**
  - Perkecil tombol `.mobile-scroll-nav` di HP menjadi lebih ramping (misalnya width 28px, height 28px) atau buat semi-transparan dengan opsi toggle sembunyikan/ciutkan.
  - Tambahkan padding kanan pada kontainer xterm (`padding-right: 38px` di HP) sehingga teks terminal **tidak pernah tertutup** oleh tombol floating panah.

- **D. Cegah Gesture Swipe Mengirim Karakter Panah Liar ke Terminal:**
  - Nonaktifkan pengiriman `\x1b[A` / `\x1b[B` otomatis pada touch drag biasa; biarkan touch drag murni melakukan scrolling viewport (`term.scrollLines`), sehingga tidak merusak teks/prompt yang sedang aktif.

- **E. Safe Area Inset untuk HP Modern:**
  - Tambahkan dukungan `padding-bottom: max(6px, env(safe-area-inset-bottom))` pada `.composer-container` agar tidak tertutup bar navigasi gestur Android/iOS.

---

## File yang Dimodifikasi
1. `C:\Users\yonat\dashboard\services\terminal-hub.js` (Perbaikan clamp PTY)
2. `C:\Users\yonat\dashboard\public\ssh.html` (Perbaikan layout mobile, resize guard, font stepper, right gutter, & touch handling)

---

## Verifikasi dan Pengujian
1. **Verifikasi Sintaks & Endpoint:**
   - Jalankan `node -c dashboard/services/terminal-hub.js` untuk memastikan tidak ada kesalahan sintaks.
   - Akses `http://127.0.0.1:8901/ssh/` secara lokal untuk memastikan file HTML ter-render tanpa error.
2. **Uji Responsive Mobile Viewport:**
   - Verifikasi melalui kalkulasi kolom xterm pada lebar 360px–420px.
   - Pastikan teks terminal tidak lagi terpotong mid-word dan kontrol font stepper dapat digunakan di HP.
