---
name: gboard-mic-voice-typing
description: "Gboard Mic Windows voice typing widget dengan auto-prioritas USB mic, waveform live visualizer, dan real-time VAD streaming"
metadata:
  node_type: memory
  type: project
  originSessionId: 12b0c24a-39bb-4892-a452-475a8c20d8d9
  modified: 2026-10-29T11:04:07.145Z
---

# Gboard Mic for Windows (Voice Typing)

Widget mic melayang di Windows (`C:\Users\yonat\gboard_mic.py`) yang ditrigger via Spasi 2x (Double-Tap Spasi) untuk mendikte suara Bahasa Indonesia ke teks via Google Speech Recognition API.

**Arsitektur & Fitur Utama:**
1. **Auto-Prioritas & Pemilihan Manual USB Mic:**
   - Dropdown badge interaktif (`USB ▾`) pada widget: klik kiri / klik kanan di widget membuka popup menu daftar mic aktif.
   - Pilihan mic manual persisten disimpan ke `~/.gboard_mic_config.json`.
   - Dynamic PortAudio re-init (`sd._terminate(); sd._initialize()`): mendeteksi mic USB baru dicolok secara on-the-fly tanpa perlu me-restart aplikasi.
   - Rescan manual via menu "🔄 Pindai Ulang Mic".
2. **Sensitivitas Ekstra Tinggi (4x Digital Preamp Boost):**
   - Mengatasi mic USB/kondensor yang volume tangkapannya kecil atau user duduk jauh (1-2 meter).
   - Profil sensitivitas via menu: Paling Tinggi (Gain 4.0x, VAD 40 - Default), Tinggi (2.5x, 70), Normal (1.0x, 120).
   - Suara dikuatkan sebelum VAD & Google Speech API sehingga kata tertangkap jelas tanpa perlu mendekatkan mulut.
2. **Visualizer Waveform Naik-Turun (Live Equalizer):**
   - Canvas Tkinter 5 bar dinamis beranimasi 30 FPS (`_update_visualizer`).
   - Saat merekam, tinggi bar bergerak real-time mengikuti amplitudo/desibel input suara (hijau -> toska -> merah muda) sebagai bukti visual suara masuk.
   - Saat hening/diam, bar mengecil menjadi titik datar abu-abu.
3. **Streaming VAD Real-Time Transcription:**
   - Tidak menunggu user mematikan tombol mic untuk mulai mengetik.
   - Algoritma Voice Activity Detection (VAD) memantau jeda bicara: begitu user jeda bernapas (~0.42 detik) atau frase mencapai 4.2 detik, potongan suara langsung dikirim ke Google Speech API di worker thread terpisah (`_start_worker`).
   - Teks langsung terketik otomatis ke jendela/aplikasi aktif (Word/Browser/Notepad) via `pyperclip` + `Ctrl+V`.
4. **Shortcut & Launcher:**
   - Script launcher: `C:\Users\yonat\Desktop\AKTIFKAN_GOOGLE_VOICE.bat` & `Gboard_Mic.vbs`.
   - Shortcut desktop: `Google Voice (Spasi 2x).lnk`.
   - Menghapus 2 spasi otomatis saat trigger double-tap (`_send_backspaces(2)`).
5. **Window Focus & Anti-Poisoning (Fix 'Terketik Tapi Tidak Masuk'):**
   - **Root Cause:** Di Windows Tkinter, `root.winfo_id()` mengembalikan ID client area, bukan HWND top-level. Saat widget disentuh/diklik, target window ter-overwrite menjadi HWND widget itu sendiri, sehingga `Ctrl+V` dikirim ke widget kosong dan macet sampai aplikasi di-restart.
   - **Fix:** (1) Pasang `WS_EX_NOACTIVATE (0x08000000)` agar widget tidak mencuri fokus kursor; (2) Filter PID via `GetWindowThreadProcessId` (`wnd_pid.value != os.getpid()`); (3) Kunci HWND aktif langsung saat Spasi 2x ditekan; (4) Validasi `IsWindow` sebelum paste.

**Why:**
Laptop internal mic sering mati/rusak (peak 2), dan Windows sering mengarahkan default device ke AudioRelay virtual mic. Ditambah user membutuhkan kepastian visual bahwa mic menangkap suara serta ingin transkrip mengalir langsung (streaming) saat bicara tanpa harus menghentikan rekaman.

**How to apply:**
Jika mic USB dicabut atau berpindah port, `_find_best_input_device()` langsung mendeteksi ulang saat Spasi 2x. Jalankan via `AKTIFKAN_GOOGLE_VOICE.bat` jika proses tertutup.
