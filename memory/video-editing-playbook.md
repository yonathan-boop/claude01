---
name: video-editing-playbook
description: "Playbook alur produksi video otomatis gratis (3D Pixar, 2D Stick Animation, & CapCut draft_content.json automation)"
metadata:
  node_type: memory
  type: reference
  originSessionId: 87648f51-d0cb-4adc-9bc5-94474a7c5fe9
  modified: 2026-10-25T03:50:11.007Z
---

# Playbook Pembuatan & Editing Video Otomatis (100% Free / Local Stack)

## 🎯 TUJUAN UTAMA KONTEN KREATOR (THE NORTH STAR)
> **"Lihat konten viral dari luar negeri (US/global), buat versi bahasa Indonesia, edit sedikit (lokalisasi, dubbing/VO, re-cut), lalu langsung upload."**
> 
> - **Formula Eksekusi**: Ambil topik/hook yang sudah terbukti meledak di luar -> adaptasi naskah ke Bahasa Indonesia -> rakit visual serupa tapi baru (anti-rip) -> upload konsisten.
> - **Benchmarking**: Model Loopra (`https://www.facebook.com/share/v/19bUCm8F3d/`) — fokus kecepatan eksekusi dan volume harian, bukan meraba ide dari nol.

Panduan teknis dan referensi workflow untuk produksi video otomatis skala massal (misal batch 30 video).

## 1. CapCut Automated Editing via Claude / JSON Hack (Matt Loui Method)
Bisa edit video tanpa sentuh timeline CapCut secara manual:
- **Mekanisme**: CapCut Desktop menyimpan seluruh struktur timeline (track video, audio, teks, durasi, efek, transisi) dalam file JSON lokal:
  - Lokasi Windows: `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\<Project_Name>\draft_content.json`
- **Cara Kerja Claude**:
  1. Buat project kosong di CapCut Desktop, letakkan asset (VO, gambar/video klip, BGM, SFX) di folder draft.
  2. Claude membaca `draft_content.json`.
  3. Script/Claude menyinkronkan timestamp gambar ke voiceover (VO duration mapping).
  4. Script menambahkan track audio SFX pada momen penting (hit, whoosh) dan track teks otomatis.
  5. Simpan kembali `draft_content.json`.
  6. Buka/refresh CapCut -> timeline sudah selesai ter-edit otomatis 100%.

## 2. 2D Stick Figure Animation (OverSimplified / Sam O'Nella Style)
Format paling cepat, stabil, dan bebas halusinasi untuk serial cerita/fakta/sejarah:
- **Karakter Konsisten**:
  - Buat **Master Character Sheet** (16:9): Berisi Front View, Side View, Back View, 3/4 View, dan grid ekspresi (Neutral, Angry, Shouting, Teeth Clench).
  - Prompt acuan:
    `Cartoon stick figure [theme] character sheet featuring [character description], displayed in professional full-body turnaround and expression reference layout 16:9. Views: Front, Side, Back, 3/4. Expressions: Neutral, Angry, Shouting, Teeth Clench. Flat 2D animation style, thick black outlines, meme-face expressions, simple clean shapes.`
- **Eksekusi 30 Video**:
  - Gunakan 3-5 background flat 2D statis yang dipakai berulang.
  - Gambar karakter transparan / sprite kepala ditempel dan diganti sesuai emosi narasi.
  - Zero distortion: Tubuh garis tidak pernah rusak saat di-render.

## 3. 3D Pixar Animation Workflow (Consistent Character & Storyboard)
- **Bukan Text-to-Video (T2V) langsung**: T2V membuat karakter dan baju berubah tiap shot.
- **Urutan 4 Langkah**:
  1. *Character Design Sheet*: 1 gambar grid acuan karakter (turnaround + ekspresi).
  2. *Detailed Storyboard*: Bagi cerita menjadi 6-8 panel adegan (Action, Camera framing, Lighting, Sound).
  3. *Image-to-Video (I2V)*: Jadikan panel storyboard sebagai first frame -> gerakkan 3-5 detik via tool I2V (Kling / Luma / AnimateDiff).
  4. *Foley & SFX*: Masukkan mikro-suara (buka tutup, langkah, dengkuran, siapaan angin) agar 3D terasa berbobot.

## 4. Stack Tool 100% Gratis (Headless CLI)
- **Naskah & Breakdown Prompt**: 9router (LLM lokal/proxy).
- **Voiceover (TTS)**: `edge-tts` (Microsoft Neural: `id-ID-GadisNeural` / `id-ID-ArdiNeural`), gratis tanpa kuota limit.
- **Generator Gambar**: REST API Pollinations.ai (Flux/SDXL, tanpa key) & Wikimedia Commons / Unsplash / NASA open media.
- **Video Assembly**: `ffmpeg` (zoompan Ken Burns effect, concatenation, subtitle overlay) ATAU injeksi `draft_content.json` CapCut.

## 5. Automasi Upload Medsos (YouTube Studio & Facebook Reels)
- Menggunakan PowerShell + `UIAutomationClient` langsung terhadap window Google Chrome aktif yang sudah login (Zero-auth, tanpa API key berbayar).
- **Alur Facebook Reels**:
  1. Navigasi address bar ke `https://www.facebook.com/reels/create`.
  2. Klik tombol `Tambahkan video atau seret dan letakkan` (membuka dialog Open Windows).
  3. Inject path file video ke edit box dialog Open via Win32 `SendMessage`.
  4. Klik tombol `Berikutnya` (2x sampai tab Pengaturan Reel).
  5. Isi teks pada `Deskripsikan reel Anda...` via `ValuePattern`.
  6. **Privasi**: Akun sudah disetel default **Publik** oleh pengguna (otomatis publik).
  7. Klik tombol `Posting` (selesai & otomatis dipublikasikan secara publik).
  8. Pasca-Upload: Segera tutup tab upload (`Ctrl+W`) atau arahkan ke `about:blank` agar video feed tidak looping nonstop dan memakan RAM/suara.

## 6. Standar Penyimpanan & Penamaan File (Single Folder & Deskriptif)
- **1 Folder Tunggal**: Semua hasil video edit diletakkan di `C:\Users\yonat\Desktop\Hasil_Edit_Video\` (mirror ke `dashboard\public\shorts\` di Server YN).
- **Wajib Nama Deskriptif**: Format `[Kategori] - [Topik dan Inti Cerita].mp4`.
- **Dilarang**: Nama generik seperti `video_01.mp4`, `sample.mp4`, `output.mp4`.
- **Rujukan**: `memory/aturan-editing-video.md`.

## 7. Format Editorial Explainer / Jurnalistik Sains (Mudeng.id / Vox Style)
Format video edukasi/sains paling berbobot, elegan, dan dipercaya audiens:
- **Arsitektur Layout Split 9:16 (Vertikal)**:
  1. *Header Bar*: Progress bar garis tipis oranye di paling atas + penanda chapter (contoh: `01 · MISTERI LAMA`, `04 · SOAL WARNA`) + Badge kotak `REKAMAN ASLI` / `FOTO ASLI`.
  2. *Headline Dual-Tone*: Teks bold besar 2 baris (Baris 1 Putih, Baris 2 Oranye Terang Emas) sebagai penegas inti bahasan per segmen.
  3. *Center Box (16:9 Frame)*: Jendela video/foto rekaman nyata dengan border garis tipis bersih. Tidak perlu ditarik distorsi (stretch).
  4. *Ambient Blurred Backdrop*: Area di belakang jendela video menggunakan versi blur dari footage itu sendiri (efek bokeh sinematik), bukan background hitam mati.
  5. *Lower Third*: Subtitle kinetik per kata/frasa berukuran besar dan terbaca jelas (`warna` putih, `gelapnya` oranye).
  6. *Footer Diagram*: Skema visual atau diagram interaktif (misal: skema kromosom X, timeline tahun, atau perbandingan persentase).
- **Audio & Pacing**:
  - Voiceover natural santai dan cerdas (kecepatan normal +10%).
  - Musik latar instrumen cerdas (pizzicato strings / cello / piano minimalis).
  - Sound effect halus (pop, slide, ticker) saat teks atau diagram bergerak.


