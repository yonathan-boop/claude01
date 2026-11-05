---
name: claude-video-watch-gemini
description: Skill watch (claude-video) & integrasi Gemini API key untuk inspeksi video YouTube dan file lokal
metadata:
  node_type: memory
  type: project
  originSessionId: 1b2ec116-08f3-449e-8d4a-d887c0c6ae8b
  modified: 2026-10-26T13:08:51.126Z
---

Skill `/watch` terpasang di Node 01 (`~/.claude/skills/watch/`) dari repo `bradautomates/claude-video`.

**Konfigurasi & Backend:**
1. **Gemini API Key:** Disimpan di `GEMINI_API_KEY` (User Environment Variable), `~/.config/watch/.env`, dan `~/.claude-mem/settings.json`.
2. **Engine:** `WATCH_ENGINE=gemini` (Google Agentic Video Model: `gemini-3.7-flash` / `gemini-2.5-flash`).
3. **Dependensi Lokal:** Python 3.12, ffmpeg 9.0.1, yt-dlp 2026.08.19 (sudah lolos `setup.py --json`).
4. **Fungsi:** Claude Code bisa menonton video YouTube atau file video lokal langsung via `/watch <url>` dan menghasilkan transkrip, deteksi visual, frame bertimestamp, atau ekstraksi panduan langkah demi langkah.
