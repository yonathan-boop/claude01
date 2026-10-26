---
name: checkpoint-jarvis-v2
description: "Titik poin stabil JARVIS 2.0 HUD dan Multi-Terminal Claude Fleet (commit 764a6fe, tag checkpoint-stable-v2)"
metadata:
  node_type: memory
  type: project
  originSessionId: b6ff8e5a-1f27-4192-9dcf-02bcf0e1cea2
  modified: 2026-10-26T10:26:21.019Z
---

Titik poin (checkpoint) stabil sistem JARVIS 2.0 HUD:

- **Waktu Snapshot**: 2026-10-26
- **Git Tag**: `checkpoint-stable-v2`
- **Repo Produksi**: `C:\Users\yonat\jarvis-hud` (Commit `209b54c`)
- **Repo Staging**: `C:\Users\yonat\jarvis-staging` (Commit `68ac031`)

**Komponen Stabil Terverifikasi:**
1. Multi-terminal Claude Fleet 3 slot persisten (`terminal-loop.js` via HTTP long-poll dispatching).
2. Explicit Slot Targeting: Mengenali target eksplisit (`buka satu`, `buka 1`, `terminal 1`, `terminal 2`, `terminal 3`, `di terminal 1...`).
3. Anti-Cross-Spawning: Jika Anda minta Terminal #1, JARVIS TIDAK AKAN lancang membuka Terminal #2 di atasnya. Jika Terminal #1 masih sibuk, JARVIS memberi tahu bahwa Terminal #1 sedang sibuk, bukan membakar slot baru.
4. Anti-Window-Sprawl: Jika jendela Terminal #1, #2, atau #3 sudah terbuka di layar, tugas langsung dialirkan ke jendela yang ada TANPA membuka jendela baru lagi. Jendela baru HANYA dibuka jika slot belum aktif.
5. Router regex cepat tangkap `panggil claude`, `buka claude`, `suruh claude`, `terminal claude`, `profil jarvis`.
6. Interceptor anti-headless di `runPowerShell`.
7. Dedicated agent `~/.claude/agents/jarvis.md` dan profile Windows Terminal `JARVIS Worker`.
8. PM2 proses `jarvis` port 3000 online & hotkey listener `global_trigger.py` aktif.

**Cara Rollback Instan (Jika rusak di kemudian hari):**
```powershell
git -C C:\Users\yonat\jarvis-hud reset --hard checkpoint-stable-v2
pm2 restart jarvis
```
