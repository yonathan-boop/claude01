# Rencana Peningkatan Server YN Web Terminal (Multi-CMD & SSH Hub)

## Context
Server YN menyediakan Web Terminal Hub (`/ssh/` atau `https://ssh.serveryn.my.id`) berbasis persistent ConPTY (`@lydell/node-pty` + `ws` di port 8901) dan antarmuka xterm.js 5.5.0. 
Keluhan utama user saat ini: **scrolling di terminal masih terasa macet, berat, dan tersendat (khususnya di layar sentuh HP)**.
Selain itu, user meminta terminal dipercantik dan ditambahkan fitur-fitur produktivitas mandiri yang relevan untuk operasional harian (remote coding, eksekusi Claude Code, manajemen server via HP/desktop).

---

## 1. Diagnosis Akar Masalah Scrolling Macet

1. **`touch-action: none;` pada Container Utama**:
   - Di `dashboard/public/ssh.html`, `#terminal-container` diberi style `touch-action: none;`. Ini mematikan total hardware acceleration dan gesture panning bawaan browser pada elemen `.xterm-viewport`.
2. **Kalkulasi Stepped Delta Manual yang Patah-patah**:
   - Kode lama menangkap event sentuhan secara manual (`accumulatedDelta += dy * 1.35; lines = Math.trunc(accumulatedDelta / 16);`). Outputnya hanya bergerak per 16 pixel (stepped/choppy) bukannya mulus per pixel (smooth kinetic scrolling).
3. **Jebakan Alternate Screen Buffer pada Claude Code / TUI (`baseY === 0`)**:
   - Saat menjalankan Claude Code, vim, atau nano, xterm berpindah ke alternate buffer di mana `term.buffer.active.baseY === 0`.
   - Kode lama mencoba menyuntikkan `new WheelEvent('wheel', ...)` buatan lewat JavaScript. Di browser mobile (Chrome/Safari), event sintesis tidak tepercaya (untrusted) ini sering kali diabaikan/di-drop oleh browser engine, membuat tampilan terminal tampak macet total saat disentuh.

---

## 2. Strategi Perbaikan & Solusi Arsitektur

### A. Mesin Scrolling 60 FPS Mulus (Smooth Dual-Mode Scroll)
1. **Normal Buffer Mode (CMD / PowerShell / Output Panjang)**:
   - Hapus `touch-action: none` yang memblokir scrolling. Aktifkan `touch-action: pan-y; -webkit-overflow-scrolling: touch;` langsung pada container dan `.xterm-viewport`.
   - Manfaatkan scrolling bawaan viewport xterm yang terintegrasi dengan hardware thread browser, ditambah momentum inertia yang presisi.
2. **Alternate Buffer Mode (Claude Code / Interactive CLI)**:
   - Deteksi otomatis apakah terminal sedang berada di alternate buffer (`term.buffer.active.baseY === 0`).
   - Jika di alternate buffer: Terjemahkan gesture geser vertikal menjadi escape sequence arah terminal asli (`\x1b[A` / `\x1b[B` atau PageUp `\x1b[5~` / PageDown `\x1b[6~`), sehingga history chat Claude Code dapat di-scroll naik-turun tanpa macet!
3. **Penyempurnaan Navigasi Cepat (Quick Scroll & Scrubber)**:
   - Tombol cepat floating (`⤒ Top`, `▲ PgUp`, `▼ PgDn`, `⤓ Bottom`) dibuat cerdas: di normal buffer memanggil `term.scrollPages()`, di alternate buffer mengirim sequence PgUp/PgDn langsung ke PTY WebSocket.
   - Tombol floating "↓ Terkini (Bottom)" dilengkapi indikator unread badge dan auto-hide saat posisi sudah di dasar.
   - Track scrubber vertikal di tepi kanan dioptimalkan agar tidak menghalangi sentuhan normal.

### B. Fitur-Fitur Produktivitas Baru (Mobile & Desktop)
1. **Toolbar Makro Cepat (Quick Chips)**:
   - Tombol kontrol vital: `Esc`, `Tab`, `Ctrl+C`, `Ctrl+D`, `↑`, `↓`, `↵ Enter`.
   - Makro aksi: `Clear` (`cls`), `Git Status`, `PM2`, `/compact`, `/clear`.
   - Fitur simpan chip kustom: Pengguna bisa menambah perintah favorit sendiri via tombol `+` (tersimpan di `localStorage`).
2. **Alat Pencarian Teks Buffer (Buffer Search / Find `Ctrl+F`)**:
   - Floating search bar minimalis dengan input pencarian, tombol Next/Prev, dan hit counter.
   - Menggunakan inspeksi teks `term.buffer.active` bawaan xterm secara native tanpa library eksternal, langsung lompat dan highlight baris yang cocok.
3. **Pengatur Ukuran Font Dinamis (`A-` / `A+`)**:
   - Tombol zoom font terminal (10px hingga 18px).
   - Otomatis trigger `fitAddon.fit()` dan menyimpan preferensi ukuran font di `localStorage`.
4. **Penyalin Teks Cepat (Copy Output Helper)**:
   - Tombol 1-klik untuk menyalin seluruh teks yang terlihat atau output perintah terakhir ke clipboard HP/PC tanpa perlu seleksi sentuh yang rumit.
5. **Mode Layar Penuh (Fullscreen Toggle)**:
   - Tombol masuk mode fullscreen (`requestFullscreen`) untuk menyembunyikan address bar browser saat digunakan di HP.
6. **Rename Sesi Tab**:
   - User bisa mengubah nama tab terminal (misal: "Claude Code", "Build M11", "Worker") agar rapi dan mudah dikenali.

### C. Pembenahan Backend Terminal Hub (`services/terminal-hub.js`)
1. **Endpoint `POST /api/pty/rename`**:
   - Menyimpan nama sesi baru ke memori ConPTY session manager dan membroadcast perubahan ke semua client aktif.
2. **Dukungan Endpoint `POST /api/upload-image` pada Port 8901**:
   - Mengatasi bug di mana upload gambar 📷 gagal saat terminal diakses via subdomain `https://ssh.serveryn.my.id` (yang langsung mengarah ke port 8901 tanpa lewat port 8905).

### D. Percantik Tampilan (Aesthetic & Visual Polish)
1. Desain Glassmorphism gelap premium ala Cyberpunk / Obsidian dengan border halus, efek neon cyan/emerald pada elemen aktif, dan kontras teks tinggi.
2. Status badge interaktif (indikator PID sesi, indikator koneksi WebSocket real-time).
3. Haptic feedback ringan (`navigator.vibrate`) pada penekanan tombol makro di HP.

---

## 3. File yang Akan Dimodifikasi

1. **`C:\Users\yonat\dashboard\public\ssh.html`**:
   - Merombak arsitektur touch & scroll handling.
   - Menambahkan komponen UI: Search bar, macro chips bar yang dapat dikustomisasi, font scaler, fullscreen toggle, copy helper, dan modal rename tab.
   - Memperbarui styling CSS glassmorphism & responsive layout.
2. **`C:\Users\yonat\dashboard\services\terminal-hub.js`**:
   - Menambahkan route `POST /api/pty/rename`.
   - Menambahkan route `POST /api/upload-image` untuk direct subdomain upload.
   - Menambahkan event broadcast rename pada WebSocket handler.

---

## 4. Verification & Testing Plan

1. **Uji Scrolling HP & Desktop**:
   - Buka sesi CMD standar: jalankan output panjang (`dir /s C:\Windows` atau `npm list`), uji kelancaran scrolling naik-turun menggunakan touch gesture, mouse wheel, tombol PgUp/PgDn, dan track scrubber.
   - Buka sesi Claude Code / interactive TUI: verifikasi scrolling gesture dapat menggeser tampilan obrolan tanpa macet.
2. **Uji Fitur Baru**:
   - Pengatur font: klik `A+` dan `A-`, verifikasi terminal resize otomatis dan layout tetap rapi.
   - Pencarian: buka search bar (`Ctrl+F` atau tombol cari), cari kata tertentu, verifikasi teks ter-highlight dan layar melompat ke baris tersebut.
   - Makro chip: klik `Tab`, `Ctrl+C`, `Esc`, dan jalankan chip custom.
   - Rename tab: ubah nama tab, pastikan nama berubah seketika dan tersinkronisasi.
3. **Uji Upload Gambar Subdomain**:
   - Tes endpoint `/api/upload-image` di port 8901 untuk memastikan upload gambar via `ssh.serveryn.my.id` berjalan normal.
4. **Uji PM2 & Zero-Downtime**:
   - Reload service `pm2 restart terminal-hub`, pastikan sesi terminal tetap hidup dan otomatis tersambung kembali (reconnected) tanpa kehilangan sesi.
