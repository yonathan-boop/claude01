# Rencana Implementasi: Google Flow Pipeline, Frame Self-Evaluation, & Rotasi 50% Token 9Router

## Context
User meminta riset komprehensif mengenai cara generate video berkualitas di Google Flow (flow.google.com), lengkap dengan pengujian mandiri dan evaluasi frame visual oleh AI (bukan dinilai manual oleh user). Selain itu, user menginstruksikan pemanfaatan token 9Router dengan batas toleransi 50%: akun yang tersisa <= 50% harus diganti ke akun lain sebelum terkuras habis (mencegah lockout/0%).

---

## 1. 9Router Token Management & Rotasi 50% (Immediate Safeguard)

### A. Masalah & Arsitektur Saat Ini
- 9Router berjalan di `http://localhost:20128` (DB: `C:\Users\yonat\AppData\Roaming\9router\db\data.sqlite` & runtime portable).
- Saat ini akun prioritas teratas (`nggaktauzancuk@gmail.com` dan `ynserver@gmail.com`) sudah habis (0%) karena sistem default `fill-first` memompa akun sampai rate limit.
- Masih ada 7 akun segar lain (`achiang.kwee`, `hanabionly1100`, `lupanggakingataku`, `coretask.id`, `yonathan.kwee`, `nahtan.kwee`, `zeroname1100`) dengan sisa kuota ~96% - 100%.

### B. Solusi Rotator Otomatis (`rotate-antigravity.js`)
- File target: `C:\Users\yonat\AppData\Roaming\9router\rotate-antigravity.js`.
- Logika:
  1. Ambil CLI token dari `machine-id` + `cli-secret`.
  2. Query `GET /api/providers` dan `GET /api/usage/{id}?force=1`.
  3. Cek persentase sisa kuota (`remainingPercentage`).
  4. Jika akun primary aktif saat ini memiliki sisa kuota `<= 50%`:
     - Set prioritas akun tersebut ke 50 atau nonaktifkan (`isActive: false`).
     - Cari akun alternatif dengan sisa kuota `> 50%` (ambil yang tertinggi).
     - Promosikan akun baru menjadi `priority = 1` dan `isActive = true`.
  5. Kirim update ke API `PUT /api/providers/{id}`.
- Integrasi:
  - Dipanggil otomatis di loop background atau di baris akhir `C:\Users\yonat\AppData\Roaming\9router\watchdog.ps1` yang sudah berjalan tiap 1 menit.

---

## 2. Google Flow: Riset, Best Practices, & Pipeline Produksi

### A. Seleksi Model Berdasarkan Kebutuhan

| Model | Durasi | Kredit | Input Referensi | Kasus Penggunaan Optimal |
|---|---|---|---|---|
| `omni-flash` | 4, 6, 8, 10s | Paling murah | s/d 7 gambar | First + last frame, multi-ingredients, video-to-video. **Default utama.** |
| `veo-3.1-fast` / `lite` | 8s fixed | ~20 kredit | s/d 3 gambar | Motion kompleks, adegan aksi, mendukung `flow-extend-video`. |
| `veo-3.1-quality` | 8s fixed | ~100 kredit | 0 (tidak bisa) | Mahal (5x), tanpa referensi. Hindari untuk produksi rutin. |

### B. Konsistensi Karakter (Character Consistency)
1. **Window Requirement**: Jendela Flow wajib **MAXIMISED** saat membuat karakter agar UI field style voice tidak hilang.
2. **Flag `--prompt` dan `--body` Wajib Identik**:
   - `--prompt`: Deskripsi fisik lengkap (umur, ras, pakaian detail atas ke bawah, warna spesifik, pose netral latar putih).
   - `--body`: Teks yang persis sama ditambah instruksi *Character Turnaround Sheet* (front, 3/4, side, back view).
3. **Pemanggilan di Adegan**: Gunakan `--character "NAMA_KARAKTER"` atau `--asset "NAMA_KARAKTER"`. Jangan mendeskripsikan ulang fitur wajah dari nol agar seed karakter tetap stabil.

### C. Transisi Antar Adegan Tanpa Warping (Frame Locking)
- Ekstrak frame terakhir dari klip $N$:
  `ffmpeg -sseof -0.1 -i scene_01.mp4 -update 1 -q:v 2 scene_01_end.png`
- Jadikan start frame untuk klip $N+1$ menggunakan `flow-frame-to-video`:
  `flow-auto generate create flow-frame-to-video --prompt "..." --image scene_01_end.png --aspect-ratio 9:16 --model omni-flash --wait`

---

## 3. Sistem Automated Visual Frame Self-Evaluation (Penilaian Mandiri)

AI melakukan ekstraksi frame dan inspeksi visual mandiri tanpa membebani user untuk menilai.

### A. Ekstraksi Keyframe Otomatis
- Script helper mengekstrak 5 frame proporsional per video (di 10%, 30%, 50%, 70%, 90% durasi):
  `ffmpeg -ss <timestamp> -i clip.mp4 -vframes 1 -q:v 2 eval_frames/clip_01_f<idx>.jpg`

### B. Protokol Evaluasi Visual AI (Rubrik Skor 1–10)
Setiap klip dinilai berdasarkan 4 pilar:
1. **Identitas Karakter (Bobot 30%)**: Wajah, bentuk rambut, pakaian cocok dengan reference sheet tanpa mutasi aneh.
2. **Semantic Alignment (Bobot 30%)**: Aksi visual di frame selaras dengan narasi script audio pada detik tersebut.
3. **Bebas Artefak & Motion Distortion (Bobot 25%)**: Tidak ada anatomi cacat (jari ganjil, wajah meleleh, ghosting/blur berlebih, teks bocor).
4. **Komposisi 9:16 Portrait Safe Zone (Bobot 15%)**: Fokus utama di tengah frame, aman dari crop vertikal dan tidak tertutup area subtitle bawah (25% margin bawah).

$$\text{Total Score} = (K_1 \times 0.3) + (K_2 \times 0.3) + (K_3 \times 0.25) + (K_4 \times 0.15)$$

### C. Decision Rule
- **Score $\ge$ 7.0**: **PASS**. Klip dinyatakan valid, lanjut ke tahap subtitle kinetik dan stitching akhir.
- **Score $<$ 7.0**: **FAIL (Auto Re-roll)**.
  - Tentukan akar masalah: jika karakter drift -> perkuat prompt pakaian / reference; jika motion rusak -> ubah prompt aksi menjadi lebih stabil atau switch ke `veo-3.1-fast`.
  - Re-generate otomatis klip tersebut (maksimal 2x retry).

---

## 4. Subtitle Kinetik & Final Stitching Pipeline

### A. Subtitle Kinetik ASS (Safe Zone 9:16)
- Font: Arial / Montserrat ExtraBold, ukuran 52, outline tebal hitam, margin bawah 280px.
- Highlight kinetik per kata/frasa berdasarkan timestamp presisi VTT dari Edge-TTS.

### B. Final FFmpeg Stitching
- Resolusi seragam 1080x1920 (portrait).
- Transisi halus antar scene menggunakan filter `xfade=transition=fade:duration=0.6`.
- Audio mixing: Voiceover vokal utama + Background Music (BGM) ducking ke -14dB saat narasi berbicara.
- Burning subtitle otomatis via filter `ass`.

---

## 5. Rencana Langkah Eksekusi (Step-by-Step)

1. **Step 1: Pasang & Jalankan Rotator Akun 9Router 50%**:
   - Buat skrip `C:\Users\yonat\AppData\Roaming\9router\rotate-antigravity.js`.
   - Eksekusi langsung untuk memverifikasi kuota seluruh akun, menurunkan akun yang sudah habis/kritis (0%), dan mengarahkan prioritas 1 ke akun segar (>90%).
   - Tautkan ke `watchdog.ps1`.
2. **Step 2: Setup Workspace Pipeline Video & Evaluator**:
   - Buat folder kerja `C:\Users\yonat\Desktop\VideoFactory\flow_evaluation_lab\`.
   - Siapkan skrip helper ekstraksi frame dan generator subtitle ASS.
3. **Step 3: Uji Coba Pembuatan Video Google Flow & Self-Evaluation**:
   - Buat 1 sampel video uji (2 adegan portrait 9:16) via Flow Connector / `flow-auto`.
   - Ekstrak 5 frame dari klip hasil generate.
   - Lakukan inspeksi visual menggunakan tool image read.
   - Laporkan skor rubrik (Karakter, Semantic, Artefak, Komposisi).
4. **Step 4: Stitching Final & Verifikasi Output**:
   - Gabungkan video dengan Edge-TTS audio dan kinetic subtitle.
   - Periksa keutuhan file video akhir di `Desktop\Hasil_Edit_Video\`.
