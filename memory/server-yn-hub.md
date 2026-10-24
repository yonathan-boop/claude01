---
name: server-yn-hub
description: "Arsitektur Server YN Dashboard, Persistent Multi-CMD Hub (/ssh), dan integrasi Cloudflare Tunnel"
metadata:
  node_type: memory
  type: project
  originSessionId: a6562376-15b8-410d-9b8f-e803f7a93d16
  modified: 2026-10-24T03:08:31.952Z
---

Server YN berjalan di port 8900 dan di-expose publik via Cloudflare Tunnel (`https://serveryn.my.id`).

## Komponen & Routing:
1. **Dashboard Utama** (`/`):
   - Lokasi: `C:\Users\yonat\dashboard`
   - File: `server.js`, `public/index.html`
   - Menampilkan status RAM, CPU, Uptime, serta gateway ke layanan aktif.
2. **Persistent Multi-CMD Terminal Hub** (`/ssh` -> `/ssh/`):
   - File: `public/ssh.html` + engine ConPTY di `server.js` (`@lydell/node-pty` + `ws`).
   - Fitur:
     - Bisa spawn banyak CMD/PowerShell (`/api/pty/spawn`).
     - Background persistence: sesi PTY tidak akan mati jika tab/browser ditutup atau koneksi putus; hanya mati jika di-kill manual (`/api/pty/kill`).
     - WebSocket `/api/pty/ws` dengan keepalive heartbeat 5s agar Cloudflare Tunnel tidak timeout.
     - Responsive 2-tier bar khusus mobile HP + auto-reconnect saat tab kembali aktif (`visibilitychange`).
     - Mobile HP Touch Scroll System:
       - Touch swipe 1 jari dengan akselerasi & momentum inersia untuk membaca riwayat/jawaban panjang ke atas.
       - Floating Nav Pad di kanan bawah: `⤒` (Top), `▲` (PgUp), `▼` (PgDn), `⤓` (Bottom).
       - Floating pill `↓ Terkini (Bottom)` otomatis muncul saat membaca riwayat lampau + indikator hijau `● Output Baru Masuk ↓` saat ada streaming respons masuk.
       - Draggable vertical touch scrubber di sisi kanan untuk scrubbing cepat ke ribuan baris lampau.
       - Buffer scrollback xterm ditingkatkan ke 10.000 baris.
     - Image paste/upload langsung dari clipboard HP/PC ke file path.
3. **Cloudflare Tunnel Auto-Supervisor**:
   - `server.js` otomatis menjalankan dan mengawasi proses `cloudflared.exe`. Jika tunnel drop atau dihentikan, auto-restart dalam 3 detik.
4. **Auto-Watchdog Tiap 5 Menit (Task Scheduler)**:
   - Task: `ServerYN-Watchdog` di Windows Task Scheduler.
   - Script: `C:\Users\yonat\dashboard\watchdog.ps1`.
   - Tiap 5 menit ping `http://127.0.0.1:8900/api/status`. Jika server/tunnel mati, watchdog otomatis memanggil `start.ps1` dan mencatat log ke `watchdog.log`.
   - Menjaga tunnel 9Router tetap online self-healing secara otomatis.
   - Startup login: sudah ada `server-yn.vbs` di folder Startup Windows.
5. **9Router AI Gateway Standalone (Port 20128 & Online Tunnel)**:
   - Akses Online Publik: `https://rcz2umy.abc-tunnel.us` (Direct fallback: `https://zoloft-beyond-dealt-rangers.trycloudflare.com`).
   - Halaman Gateway Hub: `public/9router.html` (`https://serveryn.my.id/9router.html`).
   - Kartu featured di Dashboard (`public/index.html`) dengan tautan instan ke dashboard 9router.
   - Arsitektur terpisah: berjalan di luar proses `server.js` sehingga pembaruan atau akses 9Router tidak pernah mengganggu/mematikan sesi SSH terminal aktif.
6. **3D AI Office** (`/3d`):
   - Proxy ke Cubefarm lokal di port 4317.
   - Fitur Chat CEO (Morgan): Tombol mic diganti tombol kamera (`📷`) untuk upload / attach gambar langsung (`PNG`, `JPG`, `WebP`, `GIF`, `SVG`) dan paste screenshot (`Ctrl+V`). File disimpan ke `~/.cubefarm/uploads/` via endpoint `POST /api/upload`.
   - Troubleshooting client: jika blank putih di PC luar saat pindah WiFi, issue ada pada cache browser (`Ctrl+F5`) atau filter DNS WiFi ISP (aktifkan DoH 1.1.1.1).
7. **Script Start/Stop (Proteksi Zero-Downtime Terminal)**:
   - `start.ps1`: dilengkapi pengecekan kesehatan port 8900. Jika server sudah hidup normal, proses restart otomatis dilewati agar sesi CMD/PowerShell aktif tidak mati.
   - `stop.ps1`: menghentikan node, cloudflared, dan membersihkan port 8900/4317.
8. **ConPTY Windows & Task Scheduler Working Directory**:
   - `node-pty` di Windows memanggil `conptyNative.startProcess(file, ...)` (`CreateProcess(lpApplicationName, ...)`). Jika `file` hanya `'cmd.exe'` dan CWD dari Task Scheduler adalah `C:\Windows\System32`, Windows melempar `Error: File not found:`.
   - Solusi: `server.js` selalu resolve executable path absolut via `resolveShellPath()` (`ComSpec` / full path powershell). `start.ps1`, `watchdog.ps1`, dan Action Task Scheduler selalu pakai `-WorkingDirectory C:\Users\yonat\dashboard`.

**Why:** Mencegah amnesia konteks pada sesi chat baru saat troubleshooting atau mengembangkan Server YN.
**How to apply:** Saat ada request terkait server YN, terminal, dashboard, atau Cloudflare tunnel, langsung rujuk direktori `C:\Users\yonat\dashboard`.
