---
name: jarvis-2-hud
description: JARVIS 2.0 Holographic HUD dengan bola partikel 3D Three.js, Double-Tap 'Z' hotkey, Edge-TTS British voice, dan 9router
metadata:
  node_type: memory
  type: project
  originSessionId: 2026-10-25-jarvis
  modified: 2026-10-26T10:03:24.697Z
---

JARVIS 2.0 Tactical Neural Interface di PC Node 01:

1. **Path Folder**: `C:\Users\yonat\jarvis-hud\`
2. **Komponen**:
   - `server.js`: Node.js server port 3000 (bridge ke 9router port 20128, in-memory LRU TTS cache 150 entries, prewarming, dan SSE broadcast).
   - `tts_service.py`: Persistent Python aiohttp micro-service port 3002 (real-time edge-tts chunk streaming, no process spawn overhead).
   - `public/`: Three.js Holographic Particle Orb cyan, audio-reactive deformation, telemetri HUD sci-fi, dan subtitle ticker yang selaras dengan audio onplay (Zero-Desync).
   - `global_trigger.py`: Windows global double-tap `Z` / `C` detector via `ctypes.windll.user32.GetAsyncKeyState` (CPU < 0.05%).
   - `start-jarvis.bat`: Launcher 1-klik untuk server, hotkey listener, dan Chrome App mode borderless window.
   - Desktop Shortcut: `C:\Users\yonat\Desktop\JARVIS 2.0.lnk`.
3. **Voice Engine**:
   - TTS: Microsoft Edge TTS `en-GB-RyanNeural` (Jarvis British) & `id-ID-ArdiNeural` (Indonesian), persistent streaming di port 3002 via `tts_service.py` dengan `WordBoundary` alignment metadata, respons cached ~10ms, uncached ~1.4s (5x lebih cepat).
   - Subtitle Sync: Teks balasan muncul per-kata sinkron persis dengan timeline audio playback (`X-Word-Timings` header via Edge-TTS `WordBoundary`), menghilangkan lag dan premature render.
   - STT: Browser Web Speech API dengan timer jeda hening 1.2 detik (alami dan cepat).
   - LLM: 9router `http://127.0.0.1:20128` model `campur`.
4. **Transparansi Pekerjaan (Live Task Monitor)**:
   - Widget Tactical Task Monitor di kanan atas HUD menampilkan status aktivitas secara real-time (`IDLE`, `PROCESSING`, `EXECUTING PS`, `DELEGATED TO CLAUDE CODE`, `COMPLETED`).
   - Detail perintah dan rute delegasi selalu terpampang gamblang sehingga user tidak perlu menebak status pekerjaan.
5. **Multi-Terminal Claude Fleet Manager (Maksimal 3 Terminal)**:
   - Pembagian Tugas Tegas: JARVIS hanya eksekusi tugas ringan (buka notepad, youtube, cek ram). Semua tugas coding, ubah kode, periksa file, dan riset teknis WAJIB membuka jendela terminal Claude Code interaktif nyata di depan layar.
   - Kapasitas Fleet: Maksimal 3 slot terminal aktif (#01, #02, #03).
   - Jendela Nyata & Interaktif: Setiap terminal memunculkan window CMD terpisah berjudul `[CLAUDE WORKER #N] - <tugas>` via `terminal-worker.js` dengan opsi interaktif `--name "JARVIS Worker #N"`.
   - Dedicated Agent & Profile: Agent Claude `~/.claude/agents/jarvis.md` dan Profile Windows Terminal `JARVIS Worker` (OLED Deep Dark) terpasang.
   - Smart Routing: Router menangkap frasa `panggil claude`, `buka claude`, `suruh claude`, `terminal claude`, serta safety guard di `runPowerShell` mencegah eksekusi headless.
   - Notifikasi Selesai Otomatis: Saat perintah Claude selesai, skrip otomatis melapor ke `/api/terminal/complete`, slot kembali IDLE, dan jendela tetap terbuka (CMD standby) untuk dilihat pengguna.
6. **Staging Environment Terisolasi Port 3001 (`C:\Users\yonat\jarvis-staging\`)**:
   - Port 3000 (Produksi PM2) aktif dan sinkron.
   - Staging di port 3001 siap untuk eksperimen sebelum dilempar ke produksi.
7. **Titik Poin / Checkpoint Tag (Aman dari Kerusakan)**:
   - Git Tag Stabil: `checkpoint-stable-v2` di `jarvis-hud` (commit `764a6fe`) dan `jarvis-staging` (commit `acc6d78`).
   - Perintah Pemulihan Instan jika terjadi kerusakan di masa depan:
     `git -C C:\Users\yonat\jarvis-hud reset --hard checkpoint-stable-v2; pm2 restart jarvis`
