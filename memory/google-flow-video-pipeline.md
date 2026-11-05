---
name: google-flow-video-pipeline
description: "Alur produksi video otomatis via Google Flow & Ekstensi Tuyul Flow v2: Character Anchor, Storyboard, Dubbing Indo, Subtitle Kinetik, & Stitched Export"
metadata:
  node_type: memory
  type: reference
  originSessionId: 4a2c3316-acfb-447e-a15c-2c31024c4e76
  modified: 2026-10-26T23:35:33.585Z
---

# Alur Kerja Produksi Video Otomatis Google Flow & Tuyul Flow v2

## 1. Ekstensi Chrome "Tuyul Flow v2" (Telah Terpasang di Semua Profile)
- **Lokasi Folder**: `C:\Users\yonat\Desktop\VideoFactory\tuyul-flow-extension\`
- **Background Engine (PM2)**: `tuyul-bridge` berjalan 24/7 di port `8910`.
- **Shortcut & Registry**:
  - Registry: `HKCU:\Software\Google\Chrome\Extensions\aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` -> `path` = folder ekstensi.
  - Shortcut Chrome Desktop & Taskbar: ditambah `--load-extension="C:\Users\yonat\Desktop\VideoFactory\tuyul-flow-extension"`.
- **UI di Google Flow**:
  - Tombol melayang `👻` di pojok kanan bawah halaman `flow.google.com`.
  - Panel kontrol: Input topik, pilih 18 gaya visual (3D Pixar, Stickman, Doodle Purba, dll), format 20s/30s.
  - Tombol: `🚀 Lepas Tuyul (Kerjakan Otomatis)`.

## 2. Standar Format Video Shorts 20 Detik (2 Klip Mulus)
- **Bagian 1 (00:00 - 00:10)**: Hook & Pertanyaan Mengejutkan ("Tahukah kamu...").
- **Transisi**: Crossfade `xfade` 0.6 detik (menghubungkan adegan 1 ke adegan 2 dengan halus, anti-kaget).
- **Bagian 2 (00:10 - 00:20)**: Penjelasan Ilmiah / Fakta Inti.
- **Audio & Teks**: Voiceover Bahasa Indonesia (Edge-TTS Ardi/Gadis +10%) + Subtitle Kinetik gaya Vox/Mudeng (highlight kuning neon) + BGM lembut (volume 0.12).
- **Folder Hasil**: `C:\Users\yonat\Desktop\Hasil_Edit_Video\[Kategori] - [Topik] 20 Detik.mp4`.
