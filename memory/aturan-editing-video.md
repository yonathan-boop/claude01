---
name: aturan-editing-video
description: "Aturan penyimpanan video hasil edit: 1 folder tunggal dan wajib penamaan deskriptif tentang isi video"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 105c2321-8bc9-4434-a01e-cceb1a9866e9
  modified: 2026-10-25T03:50:26.877Z
---

# Aturan Baku Penyimpanan & Penamaan Video Hasil Edit

## 🎯 TUJUAN UTAMA KONTEN KREATOR (THE NORTH STAR)
> **"Lihat konten viral dari luar negeri (US/global), buat versi bahasa Indonesia, edit sedikit, lalu langsung upload."**
> 
> Tidak perlu mulai dari nol: ambil pola/konten luar yang sudah terbukti meledak, adaptasi ke bahasa Indonesia, edit ringkas, upload rutin.

Setiap video hasil render/editing otomatis maupun manual WAJIB mematuhi dua aturan mutlak ini:

## 1. Lokasi Folder Tunggal (Single Folder)
- Seluruh video hasil akhir edit WAJIB dikumpulkan ke **1 folder saja**:
  - Folder Utama Lokal: `C:\Users\yonat\Desktop\Hasil_Edit_Video\` (atau shortcut langsung di Desktop).
  - Mirror Publik Server YN: `C:\Users\yonat\dashboard\public\shorts\` (otomatis terhubung ke web galeri `https://serveryn.my.id/gallery.html`).
- DILARANG menyebarkan file video di folder acak / subfolder tersembunyi (misal `temp_batch`, root project, atau folder unduhan).

## 2. Penamaan Wajib Deskriptif (Tentang Apa Video Tersebut)
- **Format Baku:**
  `[Kategori] - [Topik dan Inti Cerita].mp4`
  atau
  `[Nomor]_[Kategori] - [Judul Topik Deskriptif].mp4`
- **Contoh Benar:**
  - `Edukasi - Ben Franklin Effect Trik Bikin Orang Suka.mp4`
  - `Drama - Pewaris Konglomerat Menyamar Jadi OB Kantor.mp4`
  - `Misteri - Suara Bloop dan Misteri Palung Mariana.mp4`
  - `Sains - Hujan Berlian di Planet Neptunus 60fps.mp4`
- **DILARANG KERAS (Anti-Generic):**
  - `video_01.mp4`, `video_02.mp4`
  - `test.mp4`, `sample.mp4`, `output.mp4`
  - `final.mp4`, `edit_v2.mp4`
  Setiap file harus langsung terbaca tentang apa isi videonya tanpa perlu diputar terlebih dahulu.

## 3. Integrasi Otomatis Server YN
- Setiap ada video baru yang masuk ke folder tersebut, metadata dan link di `gallery.html` dan `catalog.json` Server YN wajib memuat judul deskriptif yang sama.
- Shortcut di Desktop (`Desktop\Buka Folder 30 Video.bat` / `Desktop\Hasil_Edit_Video`) dan Dashboard (`https://serveryn.my.id/gallery.html`) harus selalu mengarah ke folder tunggal ini.

## 4. Pasca-Upload: Hentikan Tab Video Browser (Anti-Looping)
- Facebook Reels / feed memutar video secara looping nonstop jika tab dibiarkan aktif.
- Begitu postingan terkonfirmasi berhasil diupload:
  - Tab upload WAJIB segera ditutup (`Ctrl+W`) atau dinavigasikan ke `about:blank`.
  - Jangan biarkan video Facebook berputar di background karena memboroskan RAM, CPU, dan mengganggu audio pengguna.

## 5. Standar Penilaian Kualitas Video (Scoring Rubric)
Setiap video yang diproduksi memiliki skor standar kelayakan tayang:
- **Skor < 5 (DITOLAK / TIDAK LAYAK TAYANG):**
  - Gambar statis tidak berubah atau tidak relevan dengan narasi.
  - Dubbing robotik lambat / tidak natural.
  - Penyebutan kata asing canggung/kaku.
  - Tanpa musik atau audio rusak.
- **Skor 6 (BARE MINIMUM / PAS-PASAN - Boleh Tayang):**
  - Foto berganti per adegan dengan zoom lambat (Ken Burns effect).
  - Dubbing cepat dan bahasa natural.
  - Subtitle per kalimat/frasa.
  - BGM latar dasar (contoh: video Sains Hujan Berlian).
- **Skor 8 - 9+ (TARGET UTAMA / KONTEN PREMIUM):**
  - **Visual Dinamis**: Klip video B-roll nyata yang bergerak (bukan hanya foto diam di-zoom).
  - **Multi-Layer SFX**: Efek suara hit pembuka (hook), whoosh saat pergantian adegan, dan suara kontekstual (foley/gemerincing).
  - **Subtitle Kinetik Kata-per-Kata**: Efek pop-up atau highlight melompat tiap kata (karaoke style) sinkron ketukan vokal.
  - **Pacing Cepat**: Durasi 15-25 detik, padat informasi, zero jeda kosong.

## 6. Privasi Upload Medsos (Default Akun Sudah Publik)
- User sudah mengatur setelan akun Facebook secara global ke **Publik**.
- Semua postingan & Reel otomatis berstatus Publik tanpa perlu pengubahan manual.
- Tetap pastikan tidak ada perubahan setelan akun yang tidak disengaja.

## 7. Sinkronisasi Mutlak Visual & Plot Narasi (Anti-Desync Timeskip)
- **Larangan Desync Alur**: DILARANG membiarkan footage video satu adegan terus berputar saat narasi cerita sudah berpindah babak/waktu (misal: narasi cerita sudah timeskip '17 tahun kemudian / mobil mewah tiba / sukses besar', tapi video di layar masih adegan masa lalu makan mie/hujan).
- **Aturan Multi-Klip Per Babak Cerita**:
  - Cerita recap drama dengan alur multi-fase WAJIB memotong footage menjadi per adegan spesifik:
    1. *Fase 1 (Masa Lalu / Pemicu)*: Footage orang miskin / hujan / makan mie.
    2. *Fase 2 (Transisi / Timeskip)*: Footage waktu berlalu / kalender / suasana kota modern.
    3. *Fase 3 (Klimaks / Masa Depan)*: Footage mobil mewah / kantor CEO / jas rapi / sukses.
  - Jika footage asli hanya meliput 1 adegan, jangan buat naskah timeskip panjang yang visualnya tidak ada. Buat cerita padat yang 100% selaras dengan adegan visual yang dimiliki.

## 8. Aturan Baku Desain Audio (Anti-Whoosh & Anti-Kaget)
- **Larangan Keras Sound Effect Mengejutkan**:
  - DILARANG menggunakan efek suara Whoosh, Boom, Impact keras, atau sound effect transisi yang tiba-tiba berbunyi keras di tengah narasi.
  - Teguran User: *"efek suara whoosh itu mengganggu sekali... ibaratnya sama seperti orang lagi ngomong pelan terus tiba-tiba teriak"*.
- **Formula Mix Audio Bersih & Nyaman (Clean Editorial Mix)**:
  1. *Voiceover Utama*: Jernih, vokal bulat, treble pas (Volume: 1.25 - 1.35).
  2. *Background Music (BGM)*: Musik latar konstan, lembut, tidak menenggelamkan vokal (Volume: 0.12 - 0.15) dengan fade out halus di detik terakhir.
  3. *Sound Effects*: ZERO efek transisi kencang. Hindari penumpukan audio yang merusak kejelasan kata.

## 9. Larangan Mencomot Aset Milik Orang Lain (Anti-Ripping & Serupa Tapi Tak Sama)
- **DILARANG Comot Frame Langsung**: Jangan pernah mengambil screenshot / memotong frame langsung dari postingan/video referensi orang lain untuk dimasukkan ke video kita.
- **Prinsip "Serupa Tapi Tak Sama"**:
  - Ambil *konsep, struktur, dan gayanya*, lalu buat **aset visual 100% baru**:
    1. Karakter 2D/3D: Generate via Prompt AI baru (Pollinations / Flux / SDXL) atau gambar mandiri via SVG/Canvas.
    2. Infografis: Render sendiri menggunakan filter FFmpeg / HTML canvas / drawing pad.
    3. Foto/Video: Gunakan database open-source domain publik murni (NASA, Unsplash, Pexels, Wikimedia Commons bebas atribusi).

## 10. Kalibrasi Timing Sinkronisasi: Visual Harus Masuk Duluan (Lead-in 1-2 Detik)
- **Penyebab Audio Terasa 1-2 Detik Lebih Cepat**:
  - Mata manusia butuh waktu 1 - 1.5 detik untuk memproses gambar baru di layar sebelum otak siap mencerna kata-kata dari narator.
  - Jika narator sudah berbicara tepat di detik 0.0 atau sebelum adegan berubah, penonton merasa audio "kecepatan 2 detik" dan gambar terlambat.
- **Standar Pacing Visual-First**:
  - Beri jeda *visual lead-in* 0.8 - 1.2 detik saat pergantian adegan atau potong transisi visual 1-2 detik lebih awal sebelum kata kunci tersebut diucapkan.
  - Ketika narator menyebut nama objek (misal "Jupiter" atau "Rolls Royce"), visual objek tersebut WAJIB sudah terpampang di layar 1 detik sebelumnya.



