---
name: gboard-mic-voice-typing
description: "Gboard Mic Windows voice typing widget dengan auto-prioritas USB mic, waveform live visualizer, dan real-time VAD streaming"
metadata:
  node_type: memory
  type: project
  originSessionId: 12b0c24a-39bb-4892-a452-475a8c20d8d9
  modified: 2026-10-26T10:13:38.687Z
---

# Gboard Mic for Windows (Voice Typing)

Widget mic melayang di Windows (`C:\Users\yonat\gboard_mic.py`) yang ditrigger via Spasi 2x (Double-Tap Spasi) untuk mendikte suara Bahasa Indonesia ke teks via Google Speech Recognition API.

**Arsitektur & Fitur Utama:**
1. **Auto-Prioritas USB Mic:**
   - Secara otomatis mendeteksi perangkat audio dengan nama `USB` (misal `Microphone (USB2.0 Device)`).
   - Fallback otomatis ke Headset fisik/Bluetooth (misal `Baseus Bowie MC1`).
   - Memblokir `Virtual Mic for AudioRelay` yang menghasilkan desibel 0/peak 1 (hening).
   - Re-scan dinamis saat tombol rekam ditekan tanpa perlu me-restart aplikasi jika mic USB dicabut-colok.
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

**Why:**
Laptop internal mic sering mati/rusak (peak 2), dan Windows sering mengarahkan default device ke AudioRelay virtual mic. Ditambah user membutuhkan kepastian visual bahwa mic menangkap suara serta ingin transkrip mengalir langsung (streaming) saat bicara tanpa harus menghentikan rekaman.

**How to apply:**
Jika mic USB dicabut atau berpindah port, `_find_best_input_device()` langsung mendeteksi ulang saat Spasi 2x. Jalankan via `AKTIFKAN_GOOGLE_VOICE.bat` jika proses tertutup.
