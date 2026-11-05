# Implementasi n8n Claude Code Agent di Server YN

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Membangun sistem chatbot AI otonom berbasis alur kerja n8n yang di-host di Server YN (`serveryn.my.id`), ditenagai oleh Claude via 9Router lokal (port 20128), dengan kapabilitas eksekusi perintah PowerShell, baca/tulis file lokal, dan inspeksi sistem 100% seperti Claude Code tanpa restriksi.

**Architecture:** n8n dijalankan sebagai background microservice mandiri di bawah PM2 Server YN (`services/n8n-service.js`) pada port 5678 dengan izin modul native (`NODE_FUNCTION_ALLOW_BUILTIN=*`). Traffic HTTP dan WebSocket di-reverse proxy secara mulus oleh `services/gateway.js` (port 8900) ke endpoint `/n8n/`, `/chat/`, dan `/webhook/`. Alur kerja AI Agent di n8n dikonfigurasi menggunakan OpenAI-compatible Chat Model terhubung ke 9Router lokal (`http://127.0.0.1:20128/v1`) dengan tools eksekusi PowerShell dan file system.

**Tech Stack:** n8n, Node.js (v24), PM2, 9Router (port 20128), PowerShell 5.1, SQLite, Cloudflare Tunnel (`serveryn.my.id`).

**Spec:** `C:\Users\yonat\Desktop\Claude\projects\n8n-claude-agent\docs\superpowers\specs\2026-11-04-n8n-claude-agent-design.md`

---

## Validasi Pemahaman Inti (Karpathy Threshold Rule)
1. **Chatbot Web:** Pengguna dapat berinteraksi langsung melalui antarmuka web (browser HP/PC) via `https://serveryn.my.id/chat` atau antarmuka n8n.
2. **Claude Engine via 9Router:** Menggunakan token 9Router (`sk-550b04f93399b7a7-cdmmjm-b8b1e5c3`) di port 20128 dengan model `campur` / `claude-3-7-sonnet-20250219`.
3. **100% Identik Claude Code:** Diberikan hak akses tanpa batas untuk menjalankan perintah PowerShell, membaca file, menulis file, dan memeriksa status sistem Node 01.
4. **Isolasi Node 01:** Hanya beroperasi di Node 01 (Laptop); sama sekali tidak mengganggu Node 02 (PC Kerja SD).
5. **Zero Downtime:** Tidak boleh me-restart `terminal-hub` (port 8901) atau memutus sesi ConPTY aktif.

---

## Global Constraints
- Windows 11 Home, PowerShell 5.1 native (dilarang sintaks Linux/bash).
- Ruang kerja project di `C:\Users\yonat\Desktop\Claude\projects\n8n-claude-agent`.
- Reverse proxy gateway Server YN di port 8900 (`C:\Users\yonat\dashboard\services\gateway.js`).
- PM2 configuration di `C:\Users\yonat\dashboard\ecosystem.config.js`.
- Endpoint 9Router di `http://127.0.0.1:20128/v1`.

---

## Review Focus
1. **WebSocket & SSE Push n8n:** Pastikan `gateway.js` mem-passthrough upgrade header dan tidak mem-buffer SSE agar status n8n tidak *offline* di balik Cloudflare.
2. **Izin Modul Native n8n:** Variabel lingkungan `NODE_FUNCTION_ALLOW_BUILTIN=*` wajib aktif agar Code Tool dapat memanggil `child_process.exec` (PowerShell).
3. **Cookie SameSite & Path Rewrite:** Pastikan redirect `/n8n` ke `/n8n/` terjaga agar asset JavaScript/CSS n8n termuat sempurna.
4. **Respon Webhook Chat:** Endpoint chat webhook wajib mengembalikan respons streaming atau teks utuh ke antarmuka web tanpa timeout 504.
5. **Ketersediaan 9Router Model:** Pastikan header otentikasi Bearer token 9router terinjeksi valid ke panggilan OpenAI Chat Model di n8n.

---

## Rencana Tugas Eksekusi (Implementation Tasks)

### Task 1: Verifikasi & Konfigurasi Runtime n8n di Node 01
**Tujuan:** Memastikan paket `n8n` dapat berjalan stabil di Node 01 dengan konfigurasi environment variabel yang mengizinkan eksekusi child_process.
- **Files:**
  - Create: `C:\Users\yonat\Desktop\Claude\projects\n8n-claude-agent\.env`
  - Create: `C:\Users\yonat\dashboard\services\n8n-service.js`
- **Steps:**
  - [ ] Siapkan file konfigurasi environment `.env` untuk n8n (`N8N_PORT=5678`, `N8N_HOST=127.0.0.1`, `NODE_FUNCTION_ALLOW_BUILTIN=*`, `WEBHOOK_URL=https://serveryn.my.id/`, `N8N_EDITOR_BASE_URL=https://serveryn.my.id/n8n/`).
  - [ ] Buat supervisor script `services/n8n-service.js` di direktori dashboard Server YN untuk mengontrol proses lifecycle n8n secara otomatis dan bersih.
  - [ ] Daftarkan service `n8n` ke dalam `C:\Users\yonat\dashboard\ecosystem.config.js`.

### Task 2: Integrasi Reverse Proxy & WebSocket di Gateway Server YN
**Tujuan:** Membuka akses publik ke n8n dan Web Chat melalui `https://serveryn.my.id/n8n/`, `/chat/`, dan `/webhook/`.
- **Files:**
  - Modify: `C:\Users\yonat\dashboard\services\gateway.js`
- **Steps:**
  - [ ] Tambahkan `PORTS.N8N = 5678` ke dalam mapping port di `gateway.js`.
  - [ ] Tambahkan routing subdomain `n8n.*` dan path `/n8n`, `/n8n/`, `/chat`, `/chat/`, `/webhook/`, `/webhook-test/` ke `PORTS.N8N`.
  - [ ] Tambahkan penanganan WebSocket upgrade untuk n8n di event `server.on('upgrade')`.
  - [ ] Reload gateway PM2 secara aman tanpa menyentuh service terminal (`pm2 reload gateway`).

### Task 3: Pembuatan Template Workflow AI Agent Claude Code di n8n
**Tujuan:** Membuat workflow otomatis yang berisi Chat Trigger, Tools Agent (Claude Engine), dan Custom Code Tools (PowerShell, File IO).
- **Files:**
  - Create: `C:\Users\yonat\Desktop\Claude\projects\n8n-claude-agent\workflows\claude_code_agent_workflow.json`
  - Create: `C:\Users\yonat\Desktop\Claude\projects\n8n-claude-agent\scripts\deploy_workflow.js`
- **Steps:**
  - [ ] Rancang node **Chat Trigger** (`@n8n/n8n-nodes-langchain.chatTrigger`).
  - [ ] Rancang node **OpenAI Chat Model** terhubung ke `http://127.0.0.1:20128/v1` dengan model `campur` / `claude-3-7-sonnet-20250219`.
  - [ ] Rancang node **AI Agent** dengan system prompt Claude Code (Bahasa Indonesia komunikatif, otonom, instruktif).
  - [ ] Rancang **Custom Tool: PowerShell Executor** (`child_process.execSync('powershell.exe -Command ...')`).
  - [ ] Rancang **Custom Tool: File Reader & Writer** (`fs.readFileSync`, `fs.writeFileSync`).
  - [ ] Buat skrip deployment otomatis (`deploy_workflow.js`) untuk memasukkan workflow ke database SQLite n8n atau mengaktifkannya via REST API n8n.

### Task 4: Antarmuka Web Chat Client & Validasi End-to-End
**Tujuan:** Menyediakan halaman web chat yang bersih, responsif, berlatar gelap (OLED dark mode) di `https://serveryn.my.id/chat` serta menguji interaksi Claude Agent.
- **Files:**
  - Create: `C:\Users\yonat\dashboard\public\chat.html`
  - Create: `C:\Users\yonat\Desktop\Claude\projects\n8n-claude-agent\tests\verify_agent.js`
- **Steps:**
  - [ ] Buat halaman antarmuka chat OLED dark mode di `public/chat.html` yang terhubung ke webhook n8n chat trigger.
  - [ ] Jalankan verifikasi end-to-end:
    1. Cek kesehatan port 5678 (`http://127.0.0.1:5678/healthz`).
    2. Tes kirim pesan chat: "Siapa kamu dan jalankan hostname di powershell".
    3. Verifikasi agen memanggil tool PowerShell dan mengembalikan nama host sistem secara akurat.
  - [ ] Simpan dokumentasi status dan URL akses ke `memory/` dan panduan singkat untuk pengguna.
