---
name: server-yn-hub
description: "Arsitektur Server YN Dashboard, Persistent Multi-CMD Hub (/ssh), dan integrasi Cloudflare Tunnel"
metadata:
  node_type: memory
  type: project
  originSessionId: a6562376-15b8-410d-9b8f-e803f7a93d16
  modified: 2026-10-26T01:03:22.890Z
---

Server YN berjalan dengan arsitektur **Local Microservices via PM2** dengan Reverse Proxy Gateway di port 8900 dan di-expose publik via Cloudflare Tunnel (`https://serveryn.my.id`).

## Arsitektur PM2 Microservices (`ecosystem.config.js`):
1. **Gateway "Batu Karang" (Port 8900)** (`services/gateway.js`):
   - Reverse proxy HTTP & WebSocket berkecepatan tinggi.
   - Dual routing: Subdomain (`ssh.*`, `m11.*`, `brain.*`, `voice.*`, `3d.*`) dan Path fallback (`/ssh/`, `/website/`, `/brain/`, `/voice/`, `/3d/`).
2. **Terminal Hub (Port 8901)** (`services/terminal-hub.js`):
   - Engine persistent ConPTY (`@lydell/node-pty` + `ws`).
   - Sesi CMD/PowerShell terisolasi penuh; restart web/dashboard tidak pernah memutus terminal.
3. **Methodist-11 Website (Port 8902)** (`services/m11-website.js`):
   - Melayani web sekolah dari `Desktop/Claude/projects/m11-website`.
4. **Second Brain (Port 8903)** (`services/second-brain.js`):
   - Melayani UI & API Obsidian markdown vault di `Documents/SecondBrain`.
5. **JARVIS 2.0 Tactical HUD (Port 3000)** (`C:\Users\yonat\jarvis-hud\server.js`):
   - Antarmuka Holographic Three.js, Voice Engine Edge-TTS (port 3002), Claude Fleet Manager, integrasi 9Router port 20128. Menggantikan Voice Agent lama port 8904. Rute reverse proxy gateway: `/jarvis/`, `/voice/`, `/voice.html` (redirect), dan subdomains `jarvis.*`, `voice.*`.
6. **Dashboard UI & Core APIs (Port 8905)** (`services/dashboard.js`):
   - Dashboard monitor RAM/CPU, `/api/status`, Universal Node Hub (RPC Node 01 <-> Node 02), upload gambar.
7. **Native SSH Server (Port 2222)** (`ssh-server.js`):
   - Akses langsung Termux / PC remote via SSH protocol (`ssh2`).
8. **Cloudflare Tunnel Supervisor** (`services/tunnel.js`):
   - Mengawasi proses `cloudflared.exe` agar tunnel `serveryn.my.id` selalu aktif.

## Manajemen Proses & Self-Healing:
- `pm2 restart <nama-service>` untuk restart service spesifik (contoh: `pm2 restart m11-website`).
- `start.ps1`: cek port 8900; jika down jalankan `pm2 start ecosystem.config.js`.
- `stop.ps1`: `pm2 stop all`, `pm2 delete all`, dan kill port lingering.
- `watchdog.ps1`: tiap 5 menit ping `/api/status`; jika down otomatis panggil `start.ps1`. Startup via `server-yn.vbs` di folder Startup Windows.
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
   - Status: **Dimatikan (Disabled)** atas permintaan user. File dan paket instalasi tetap utuh (`cubefarmEnabled = false` di `server.js`).
   - Fitur Chat CEO (Morgan): Tombol mic diganti tombol kamera (`📷`) untuk upload / attach gambar langsung (`PNG`, `JPG`, `WebP`, `GIF`, `SVG`) dan paste screenshot (`Ctrl+V`). File disimpan ke `~/.cubefarm/uploads/` via endpoint `POST /api/upload`.
   - Troubleshooting client: jika blank putih di PC luar saat pindah WiFi, issue ada pada cache browser (`Ctrl+F5`) atau filter DNS WiFi ISP (aktifkan DoH 1.1.1.1).
7. **Script Start/Stop (Proteksi Zero-Downtime Terminal)**:
   - `start.ps1`: dilengkapi pengecekan kesehatan port 8900. Jika server sudah hidup normal, proses restart otomatis dilewati agar sesi CMD/PowerShell aktif tidak mati.
   - `stop.ps1`: menghentikan node, cloudflared, dan membersihkan port 8900/4317/2222.
8. **Native Direct SSH Server (Port 2222 untuk Termux & Remote PC)**:
   - File: `C:\Users\yonat\dashboard\ssh-server.js` (`ssh2` + `@lydell/node-pty`).
   - Akses langsung tanpa browser / tanpa Cloudflare WebSocket:
     - ZeroTier (Remote HP/PC Luar): `ssh node01@192.168.195.80 -p 2222` (atau alias `ssh node01`)
     - LAN WiFi Rumah/Sekolah: `ssh node01@192.168.2.101 -p 2222`
     - Autentikasi: Passwordless (tanpa password langsung masuk).
     - Identitas Visual: Banner `[NODE 01] LAPTOP SERVER YN` + prompt hijau `[01-SERVER-YN] C:\Users\yonat>` agar tidak tertukar dengan PC kerja 02.
   - Diawasi otomatis oleh `watchdog.ps1` dan `start.ps1`.
9. **Proteksi Sleep & WiFi Windows**:
   - Power policy AC: Standby 0 (Never), Display 0 (Never), Lid Close 0 (Do Nothing) agar tunnel & WiFi tidak sleep saat ditinggal lama.
10. **File Installer & Launcher Otomatis 2-Arah (Node 01 <-> Node 02 / Advan)**:
   - Disediakan langsung di `dashboard/public/` dan halaman `https://serveryn.my.id/`:
     - `setup.ps1`: One-liner PowerShell (`irm https://serveryn.my.id/setup.ps1 | iex`). Otomatis minta hak Administrator, pasang OpenSSH Server di Node 02 (port 22), set authorized_keys kunci ed25519 Node 01, buka firewall, dan **LANGSUNG MASUK** ke SSH remote Node 01 (`ssh node01`) dalam 1 proses tanpa file terpisah.
     - `SETUP_AKSES_2_ARAH_ADVAN.bat`: Launcher batch 1-klik untuk Windows Explorer, memanggil `setup.ps1` dengan elevasi UAC otomatis.
     - Kunci Publik Node 01: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIBqpwGqx4oyx+H0DKSQpkl74rvMJ/J/+5a+jY917D0T yonat@SERVER-YN`.
     - Akses Balik Node 01 -> Node 02: Node 01 bisa remote & edit file di laptop Advan via `ssh -i ~/.ssh/id_ed25519 advan@192.168.2.105` (atau alias `node02`). Teruji membaca dan mengeksekusi perintah di `C:\Users\advan\Desktop\New folder`.
11. **ConPTY Windows & Task Scheduler Working Directory**:
   - `node-pty` di Windows memanggil `conptyNative.startProcess(file, ...)` (`CreateProcess(lpApplicationName, ...)`). Jika `file` hanya `'cmd.exe'` dan CWD dari Task Scheduler adalah `C:\Windows\System32`, Windows melempar `Error: File not found:`.
   - Solusi: `server.js` selalu resolve executable path absolut via `resolveShellPath()` (`ComSpec` / full path powershell). `start.ps1`, `watchdog.ps1`, dan Action Task Scheduler selalu pakai `-WorkingDirectory C:\Users\yonat\dashboard`.

**Why:** Mencegah amnesia konteks pada sesi chat baru saat troubleshooting atau mengembangkan Server YN.
**How to apply:** Saat ada request terkait server YN, terminal, dashboard, atau Cloudflare tunnel, langsung rujuk direktori `C:\Users\yonat\dashboard`.
