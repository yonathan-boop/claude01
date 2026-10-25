---
name: media-probe
description: "Ekstraksi metadata & keyframe visual postingan media/sosial media (Facebook Reels, YouTube, TikTok, X/Twitter, Instagram) tanpa login dan bebas blokir 403. Gunakan saat user membagikan link video/reels atau butuh inspeksi visual konten medsos."
---

# Media Probe (Inspeksi Media & Medsos Tanpa Login)

Perangkat inspeksi konten video dan media sosial untuk Node 01. Bekerja tanpa login, bebas blokir 403, dan menyelesaikan isu DNS Windows secara otomatis.

## Perintah CLI

```powershell
# Ekstraksi metadata postingan/video (judul, uploader, durasi, deskripsi, views, stream URL)
media-probe "<URL>"

# Ekstraksi metadata + ambil N keyframe gambar untuk inspeksi visual (misal 3 frame)
media-probe "<URL>" --frames 3

# Ekstraksi ke folder tujuan tertentu
media-probe "<URL>" --frames 3 --out-dir "C:\Users\yonat\AppData\Local\Temp\my_frames"

# Bersihkan frame otomatis setelah pemrosesan selesai
media-probe "<URL>" --frames 3 --clean
```

## Platform Didukung
- **Facebook**: Reels (`facebook.com/share/r/...`, `facebook.com/reel/...`), video postingan, feed publik.
- **YouTube**: Video reguler, YouTube Shorts (`youtube.com/shorts/...`).
- **TikTok & Instagram**: Video & Reels publik.
- **X / Twitter**: Video & postingan multimedia.

## Alur Kerja AI
1. Jalankan `media-probe "<URL>"` untuk membaca teks, konteks, dan metadata postingan.
2. Jika butuh melihat apa yang tertulis di layar video (kode program, repositori GitHub, diagram, tutorial), tambahkan `--frames 3` lalu buka path frame visual hasil ekstraksi menggunakan alat pembaca gambar/vision.
3. Berikan analisis langsung ke user (fakta konten + komentar kritis).
