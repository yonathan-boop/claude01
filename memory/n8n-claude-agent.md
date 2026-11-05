---
name: n8n-claude-agent
description: "Arsitektur Native Claude Code Engine di balik n8n Webhook Server YN (/chat), Attach Gambar & Suara"
metadata:
  node_type: memory
  type: project
  originSessionId: f1715dca-1f48-4e5d-94c7-f83a5d0b4df1
  modified: 2026-11-04T15:23:04.876Z
---

Sistem chatbot AI otonom berbasis n8n Webhook di Server YN Node 01 yang ditenagai **100% oleh Claude Code CLI native** (`C:\Users\yonat\.local\bin\claude.exe`) dengan model `campur` via 9Router port 20128.

## Arsitektur Teknis
1. **Layanan n8n Background (Port 5678):**
   - Berjalan sebagai PM2 service `n8n` via `C:\Users\yonat\dashboard\services\n8n-service.js`.
   - Menghubungkan webhook endpoint `POST /webhook/claude-chat` ke Node.js Code node yang memanggil Claude Code CLI secara terisolasi tanpa shell wrapper.
   - Mengelola sesi multi-turn secara otomatis via `--session-id <uuid>` (sesi baru) dan `--resume <uuid>` (melanjutkan sesi aktif) melalui file tracking `C:\Users\yonat\.n8n\claude_cli_sessions.json`.
   - Diawasi oleh watchdog otomatis Server YN (`C:\Users\yonat\dashboard\watchdog.ps1`).

2. **Dukungan Tools Penuh (100% Claude Code Asli):**
   - Bukan sekadar tool tiruan: di balik n8n adalah Claude Code itu sendiri dengan akses ke seluruh tools:
     - `PowerShell` / `Bash` terminal execution.
     - `Read`, `Edit`, `Write` file surgical manipulation.
     - `Grep` & `Glob` search patterns.
     - Sistem memori permanen (`memory/`), `CLAUDE.md`, Karpathy Guidelines, dan Superpowers skills.

3. **Fitur Antarmuka Web Chat (`https://serveryn.my.id/chat`):**
   - **📎 Attach Gambar:** Tombol lampirkan gambar + drag & drop + paste clipboard (`Ctrl+V`). Otomatis diunggah ke `~/uploads/` dan dianalisis langsung oleh Claude via tool Read image.
   - **🎤 Ketik Suara (Voice Typing):** Tombol mikrofon Web Speech API (`id-ID`) untuk dikte suara langsung ke input teks tanpa lag.
   - **☰ Riwayat Sesi (History Drawer):** Laci riwayat percakapan dengan auto-title, tombol ganti sesi, dan tombol hapus 🗑️.
   - **+ Baru:** Tombol membuat sesi baru yang bersih dengan UUID unik.
   - **Anti-Zoom Mobile:** Font input 16px dan safe-area insets untuk kenyamanan di HP.

**Why:** Memberikan akses penuh ke kemampuan eksekusi nyata Claude Code CLI lewat antarmuka web yang fleksibel di HP dan desktop.
**How to apply:** Buka `https://serveryn.my.id/chat` atau periksa service `n8n` di PM2 Server YN.
