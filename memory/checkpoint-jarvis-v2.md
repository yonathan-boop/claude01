---
name: checkpoint-jarvis-v2
description: "Titik poin stabil JARVIS 2.0 HUD dan Multi-Terminal Claude Fleet (commit 764a6fe, tag checkpoint-stable-v2)"
metadata:
  node_type: memory
  type: project
  originSessionId: b6ff8e5a-1f27-4192-9dcf-02bcf0e1cea2
  modified: 2026-10-26T11:54:22.955Z
---

Titik poin (checkpoint) stabil sistem JARVIS 2.0 HUD:

- **Waktu Snapshot**: 2026-10-26
- **Git Tag**: `checkpoint-stable-v2`
- **Repo Produksi**: `C:\Users\yonat\jarvis-hud` (Commit `77ef010`)
- **Repo Staging**: `C:\Users\yonat\jarvis-staging` (Commit `d2beb01`)

**Komponen Stabil Terverifikasi:**
1. Large Holographic Background Terminal: Ditambahkan konsol terminal latar belakang berukuran besar (lebar 940px / 90vw, tinggi 180px–380px) tepat di latar HUD dengan teks monospace Cascadia Code jelas, live streaming command + output, live timer pengerjaan, tombol bersihkan, dan tombol perbesar/perkecil.
2. Pengumuman Suara Hasil Selesai (Anti-Hening): Setiap kali eksekusi perintah lokal / PowerShell selesai, JARVIS WAJIB menyambungkan hasil output nyata ke respons suara dan membacakannya (contoh: "... Eksekusi selesai. Hasilnya: [data]") sehingga pengguna tidak pernah lagi dibiarkan menunggu dalam keheningan tanpa kabar.
3. Sanitizer Command PowerShell: Menghapus flag `-NoExit` dan wrapper redundan secara otomatis agar eksekusi perintah komputasi/skrip tidak pernah timeout menggantung.
4. Formal JARVIS Delegation Header: Setiap kali tugas dikirim ke terminal Claude, JARVIS menyematkan header resmi:
   `[DELEGASI RESMI DARI J.A.R.V.I.S.]`
   `Permintaan Asli Pengguna: "..."`
   `Instruksi Teknis: ...`
   `Catatan Memori: Tugas didelegasikan oleh JARVIS ke Terminal #N.`
5. Explicit Voice Note Recording: Perintah suara seperti *"catat di memori jarvis..."* atau *"simpan di memori..."* langsung ditangkap dan disimpan deterministik ke `jarvis_memory.json` (bagian `notes`).
6. Intelligent Third-Party Reformulation: JARVIS bertindak sebagai eksekutif pihak ketiga. DILARANG menyalin mentah-mentah ucapan pengguna.
7. Tugas Ringan Tetap di JARVIS: Buka folder, berkas, atau aplikasi sepele dieksekusi langsung via `[EXEC] explorer` / `Start-Process`, tidak pernah lagi dilempar keliru ke terminal Claude.
8. Terminal Interaktif Penuh (Bisa Ikut Mengetik & Campur Tangan): Sesi di terminal adalah Claude Code interaktif normal (`claude`). Pengguna bisa melihat alur proses secara langsung, membaca diff, mengetik keyboard, mengonfirmasi aksi, atau ikut berdiskusi kapan saja.
9. Auto Turn-Completion via `Stop` Hook: Saat Claude selesai menjawab suatu tugas di terminal, hook resmi `Stop` di `settings.json` memanggil `notify-stop.js` ke port 3000 (`/api/terminal/turn-complete`), slot kembali `STANDBY`, dan JARVIS mengumumkan selesai secara alami.
10. Deterministic Auto-Learning Engine: Setiap kali pengguna memberi teguran, kata "ingat ya", "jangan pernah", "mulai sekarang", atau "kamu salah", sistem server secara deterministik mengekstrak inti pelajaran dan langsung menyimpannya ke `jarvis_memory.json`.
11. Win32 Foreground Enforcer (`focus-window.ps1` & `bringToFront()`): Setiap kali terminal dibuka atau tugas baru didelegasikan, jendela terminal langsung dipaksa muncul di PALING DEPAN layar (top-most / foreground) di atas browser Chrome atau aplikasi apa pun via Win32 `SetForegroundWindow` + `ShowWindowAsync(SW_RESTORE)` + `SwitchToThisWindow`.
12. Anti-Apology Sanitizer: JARVIS dilarang keras meminta maaf ("mohon maaf", "minta maaf" disapu bersih otomatis dari audio sebelum diucapkan). Nada suara diubah menjadi taktis, tenang, dan solutif.
13. Multi-terminal Claude Fleet 3 slot persisten (`terminal-loop.js` via HTTP long-poll dispatching).
14. Jeda Hening 2.0 Detik Murni (Anti-Potong): Web Speech API dikalibrasi ke jeda hening tepat 2.0 detik (2000ms). Jika pengguna berhenti sebentar untuk bernapas/berpikir, JARVIS TIDAK AKAN memotong ucapan.
15. Reset Fleksibel (Suara & Klik): Perintah suara *"terminal 1 selesai"* atau klik langsung pada kartu slot HUD menormalkan slot.
16. Explicit Slot Targeting: Mengenali target eksplisit (`buka satu`, `buka 1`, `terminal 1`, `terminal 2`, `terminal 3`, `di terminal 1...`).
17. PM2 proses `jarvis` port 3000 online & hotkey listener `global_trigger.py` aktif.

**Cara Rollback Instan (Jika rusak di kemudian hari):**
```powershell
git -C C:\Users\yonat\jarvis-hud reset --hard checkpoint-stable-v2
pm2 restart jarvis
```
