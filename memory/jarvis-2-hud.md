---
name: jarvis-2-hud
description: JARVIS 2.0 Holographic HUD dengan bola partikel 3D Three.js, Double-Tap 'Z' hotkey, Edge-TTS British voice, dan 9router
metadata:
  node_type: memory
  type: project
  originSessionId: 2026-10-25-jarvis
  modified: 2026-10-25T16:29:10.345Z
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
   - Pembagian Tugas Tegas: JARVIS hanya eksekusi tugas ringan (buka notepad, youtube, cek ram). Semua tugas coding, ubah kode, periksa file, dan riset teknis WAJIB membuka jendela terminal Claude Code nyata di depan layar.
   - Kapasitas Fleet: Maksimal 3 slot terminal aktif (#01, #02, #03).
   - Jendela Nyata & Visibel: Setiap terminal memunculkan window CMD terpisah berjudul `[CLAUDE WORKER #N] - <tugas>` dengan teks cyan, menjalankan `claude -p "<tugas>"`.
   - Smart Context Affinity: Tugas baru dialokasikan ke terminal IDLE yang topiknya seirama. Terminal BUSY tidak boleh diganggu. Jika ketiga slot BUSY, JARVIS menolak dan melaporkan terminal mana saja yang sedang bekerja.
   - Notifikasi Selesai Otomatis: Saat perintah Claude selesai, skrip `notify-terminal.js` melapor ke `/api/terminal/complete`, slot kembali IDLE, dan JARVIS mengabarkan lewat suara.
6. **Staging Environment Terisolasi Port 3001 (`C:\Users\yonat\jarvis-staging\`)**:
   - Port 3000 (Produksi) dikunci aman dan tetap aktif.
   - Semua pembaruan, perbaikan deteksi selesai terminal instan (via `terminal-worker.js` tanpa tekan Enter), dan pengujian mandiri dijalankan di port 3001.
   - Penggabungan ke port 3000 hanya dilakukan setelah verifikasi dan persetujuan pengguna.
