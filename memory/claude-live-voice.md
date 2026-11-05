---
name: claude-live-voice
description: "Arsitektur Claude Live di Server YN (Port 3000), sensor konteks real-time komputer, dan Edge-TTS"
metadata:
  node_type: memory
  type: project
  originSessionId: 2026-10-26-claude-live
  modified: 2026-10-26T13:13:18.031Z
---

Claude Live resmi menggantikan Jarvis 2.0 di PC Node 01 & Server YN:

1. **Lokasi & Komponen**:
   - Backend Service: `C:\Users\yonat\dashboard\services\claude-live.js` (Port 3000, PM2 `claude-live`).
   - TTS Microservice: `C:\Users\yonat\dashboard\services\tts_service.py` (Port 3002, Python Edge-TTS aiohttp `id-ID-ArdiNeural` / `en-GB-RyanNeural`).
   - Frontend UI: `C:\Users\yonat\dashboard\public\voice.html` (OLED Deep Dark, HTML5 canvas audio pulse visualizer, Web Speech API, auto-handsfree mode).
2. **Sensor Konteks Real-Time (Mata & Telinga Komputer)**:
   - **Active Windows**: Deteksi aplikasi GUI yang sedang terbuka di layar pengguna (`Get-Process | Where MainWindowTitle`).
   - **Clipboard**: Membaca otomatis teks/kode yang barusan di-copy pengguna (`Get-Clipboard -Raw`).
   - **Terminal ConPTY**: Membaca daftar sesi terminal Server YN aktif dan tail scrollback 1200 karakter (`/api/pty/tail`).
   - **Hardware Telemetry**: RAM kosong dan status baterai/daya.
3. **Otak & Model**:
   - 9Router `http://127.0.0.1:20128/v1/chat/completions` model `claude-3-7-sonnet-20250219`.
   - In-memory rolling history multi-turn sehingga paham kata rujukan "ini", "itu", "yang tadi".
   - Eksekusi aksi otomatis: format tag `[ACTION:terminal]` atau `[ACTION:powershell]` atau `[ACTION:spawn_claude]`.
4. **Akses & URL**:
   - Lokal: `http://127.0.0.1:3000/` atau via Gateway `http://127.0.0.1:8900/voice/`.
   - Publik Cloudflare Tunnel: `https://serveryn.my.id/voice/` (dan alias `/claude-live/`, `/jarvis/`).
