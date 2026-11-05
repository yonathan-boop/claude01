# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "sounddevice",
#     "numpy",
#     "SpeechRecognition",
#     "pyperclip",
#     "keyboard",
# ]
# ///
"""
Gboard Mic for Windows (Bahasa Indonesia)
Tombol mic melayang + Waveform Real-time + Streaming Voice Typing via Google Speech API.
Fitur: Pemilihan Mic Manual via Menu Klik, Auto-Prioritas USB, Rescan Otomatis, Sensitivitas Ekstra Tinggi (4x Boost).
Hotkey: Spasi 2x (Double-Tap Spasi) untuk mulai/selesai.
"""

import ctypes
import json
import os
import queue
import sys
import threading
import time
import tkinter as tk
import numpy as np
import pyperclip
import sounddevice as sd
import speech_recognition as sr

user32 = ctypes.windll.user32
SAMPLE_RATE = 16000
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".gboard_mic_config.json")

SENSITIVITY_PROFILES = {
    "max": {"gain": 4.0, "vad_threshold": 40, "label": "Paling Tinggi (4x Boost - Jarak Jauh)"},
    "high": {"gain": 2.5, "vad_threshold": 70, "label": "Tinggi (2.5x Boost)"},
    "normal": {"gain": 1.0, "vad_threshold": 120, "label": "Normal (1x)"},
}


class GboardMicApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Gboard Mic")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.94)

        # ponytail: live waveform + real-time VAD streaming, upgrade to whisper/edge-tts if offline requested
        self.is_recording = False
        self.last_toggle_time = 0
        self.last_space_up_time = 0
        self.latest_volume = 0.0
        self.display_volume = 0.0
        self.active_phrase_chunks = []
        self.has_spoken = False
        self.silence_count = 0
        self.transcribe_queue = queue.Queue()
        self.stream = None
        self.device_idx = None
        self.device_name = ""
        self.device_cat = "Default"
        self.short_name = "Mic"
        self.recognizer = sr.Recognizer()
        self.my_pid = os.getpid()
        self.target_hwnd = user32.GetForegroundWindow()
        self.root_hwnd = None

        # Load config & sensitivity
        self.config = self._load_config()
        self.device_pref = self.config.get("device_pref", "auto")
        self.sens_level = self.config.get("sensitivity", "max")
        self._apply_sensitivity()

        self._build_ui()
        self._setup_drag()
        self._init_audio()
        self._setup_hotkey()
        self._start_worker()

        self.root.after(80, self._capture_root_hwnd)
        self.root.after(150, self._poll_target_window)
        self.root.after(35, self._update_visualizer)

    def _load_config(self) -> dict:
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"device_pref": "auto", "sensitivity": "max"}

    def _save_config(self):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass

    def _apply_sensitivity(self):
        profile = SENSITIVITY_PROFILES.get(self.sens_level, SENSITIVITY_PROFILES["max"])
        self.gain = profile["gain"]
        self.vad_threshold = profile["vad_threshold"]

    def _build_ui(self):
        self.frame = tk.Frame(self.root, bg="#1e1e2e", highlightthickness=1, highlightbackground="#45475a", bd=0)
        self.frame.pack(fill="both", expand=True)

        # Tombol Mic (Klik kiri: Rekam, Klik kanan: Menu Pilihan Mic)
        self.btn_mic = tk.Button(
            self.frame,
            text="🎙️",
            font=("Segoe UI Emoji", 11),
            bg="#313244",
            fg="#cdd6f4",
            activebackground="#45475a",
            activeforeground="#ffffff",
            bd=0,
            padx=5,
            pady=2,
            command=self.toggle_recording,
            cursor="hand2",
        )
        self.btn_mic.pack(side="left", padx=(5, 2), pady=4)

        # Visualizer Canvas (Waveform Naik-Turun)
        self.canvas_wave = tk.Canvas(
            self.frame,
            width=32,
            height=20,
            bg="#1e1e2e",
            highlightthickness=0,
            bd=0,
        )
        self.canvas_wave.pack(side="left", padx=(1, 3), pady=4)
        self.wave_bars = []
        bar_xs = [3, 9, 15, 21, 27]
        for bx in bar_xs:
            bar_id = self.canvas_wave.create_line(bx, 9, bx, 11, fill="#45475a", width=3, capstyle="round")
            self.wave_bars.append((bar_id, bx))

        # Badge Pemilih Mic Interaktif (Klik kiri: Buka Daftar Mic)
        self.btn_device = tk.Button(
            self.frame,
            text="Mic ▾",
            font=("Segoe UI", 8, "bold"),
            bg="#313244",
            fg="#89dceb",
            activebackground="#45475a",
            activeforeground="#ffffff",
            bd=0,
            padx=4,
            pady=2,
            command=self._show_mic_menu,
            cursor="hand2",
        )
        self.btn_device.pack(side="left", padx=(1, 2), pady=4)

        # Status Teks
        self.lbl_status = tk.Label(
            self.frame,
            text="Spasi 2x: Bicara",
            font=("Segoe UI", 8, "bold"),
            bg="#1e1e2e",
            fg="#a6adc8",
            padx=2,
        )
        self.lbl_status.pack(side="left", padx=(1, 2), pady=4)

        # Tombol Tutup
        self.btn_close = tk.Button(
            self.frame,
            text="✕",
            font=("Segoe UI", 8),
            bg="#1e1e2e",
            fg="#6c7086",
            activebackground="#f38ba8",
            activeforeground="#11111b",
            bd=0,
            padx=5,
            pady=2,
            command=self.close_app,
            cursor="hand2",
        )
        self.btn_close.pack(side="right", padx=(1, 5), pady=4)

        # Posisi default: Pojok kanan bawah di atas taskbar
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        w, h = 265, 42
        x = screen_w - w - 24
        y = screen_h - h - 60
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _setup_drag(self):
        def start_drag(e):
            self._drag_x = e.x
            self._drag_y = e.y

        def do_drag(e):
            x = self.root.winfo_x() + (e.x - self._drag_x)
            y = self.root.winfo_y() + (e.y - self._drag_y)
            self.root.geometry(f"+{x}+{y}")

        for w in (self.frame, self.lbl_status, self.canvas_wave):
            w.bind("<Button-1>", start_drag)
            w.bind("<B1-Motion>", do_drag)
            w.bind("<Button-3>", lambda e: self._show_mic_menu(e))

        self.btn_mic.bind("<Button-3>", lambda e: self._show_mic_menu(e))

    # -------------------------------------------------------------------------
    # FUNGSI ANTI-CURI FOKUS JENDELA WINDOWS
    # Alur: Mengambil handle jendela (HWND) Tkinter dan menempelkan flag Windows WS_EX_NOACTIVATE.
    # Tujuan: Supaya saat tombol mic diklik atau digeser mouse, kursor ketik di aplikasi
    #         lain (Word, Chrome, Notepad) TIDAK LEPAS atau pindah ke widget mic ini.
    # -------------------------------------------------------------------------
    def _capture_root_hwnd(self):
        hwnd = user32.GetParent(self.root.winfo_id())
        self.root_hwnd = hwnd if hwnd else self.root.winfo_id()
        GWL_EXSTYLE = -20
        WS_EX_NOACTIVATE = 0x08000000  # Flag Windows: Jendela bisa diklik tanpa merebut fokus aktif
        try:
            ex_style = user32.GetWindowLongW(self.root_hwnd, GWL_EXSTYLE)
            user32.SetWindowLongW(self.root_hwnd, GWL_EXSTYLE, ex_style | WS_EX_NOACTIVATE)
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # FUNGSI DETEKSI TARGET APLIKASI KETIK
    # Alur: Setiap 150ms mengecek jendela mana yang sedang dipegang pengguna.
    # Tujuan: Menyimpan ID jendela aktif (misal Word) agar hasil suara bisa dikirim
    #         tepat sasaran, sekaligus mencegah mic mem-paste teks ke dirinya sendiri.
    # -------------------------------------------------------------------------
    def _poll_target_window(self):
        fg = user32.GetForegroundWindow()
        if fg and fg != self.root_hwnd:
            wnd_pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(fg, ctypes.byref(wnd_pid))
            if wnd_pid.value != self.my_pid:  # Hindari mencatat proses widget sendiri
                self.target_hwnd = fg
        self.root.after(150, self._poll_target_window)

    # -------------------------------------------------------------------------
    # FUNGSI EQUALIZER LIVE VISUALIZER
    # Alur: Menghitung volume rata-rata (smoothing) dan mengubah tinggi 5 bar warna di layar.
    # Tujuan: Memberi feedback visual instan ke pengguna bahwa suaranya benar-benar
    #         terdengar oleh sistem (hijau = normal, toska = sedang, merah muda = keras).
    # -------------------------------------------------------------------------
    def _update_visualizer(self):
        self.display_volume = self.display_volume * 0.60 + self.latest_volume * 0.40
        norm = min(1.0, max(0.0, self.display_volume / 2000.0))

        multipliers = [0.6, 1.1, 1.4, 0.9, 0.5]
        for i, (bar_id, bx) in enumerate(self.wave_bars):
            if not self.is_recording:
                self.canvas_wave.coords(bar_id, bx, 9, bx, 11)
                self.canvas_wave.itemconfig(bar_id, fill="#45475a")
            else:
                bar_h = max(2, int(norm * multipliers[i] * 18))
                y1 = max(1, 10 - bar_h // 2)
                y2 = min(19, 10 + bar_h // 2)
                if norm > 0.4:
                    color = "#f38ba8" if norm > 0.75 else "#89dceb"
                else:
                    color = "#a6e3a1"
                self.canvas_wave.coords(bar_id, bx, y1, bx, y2)
                self.canvas_wave.itemconfig(bar_id, fill=color)

        self.root.after(35, self._update_visualizer)

    def _get_input_devices(self, rescan=False):
        """Pindai daftar perangkat input suara dengan PortAudio re-init dinamis."""
        if rescan:
            try:
                sd._terminate()
                sd._initialize()
            except Exception:
                pass

        devices = sd.query_devices()
        input_devs = []
        seen = set()
        for idx, d in enumerate(devices):
            if d.get("max_input_channels", 0) > 0 and d.get("hostapi") == 0:
                name = d["name"]
                if name.lower().startswith("microsoft sound mapper"):
                    continue
                if name not in seen:
                    seen.add(name)
                    input_devs.append((idx, name))
        return input_devs

    def _categorize_device(self, name: str) -> str:
        nl = name.lower()
        if "usb" in nl:
            return "USB"
        if any(k in nl for k in ["headset", "baseus", "hands-free", "bluetooth"]):
            return "Headset"
        if any(k in nl for k in ["realtek", "array", "internal"]):
            return "Realtek"
        if any(k in nl for k in ["virtual", "audiorelay"]):
            return "Virtual"
        return "Mic"

    def _make_short_name(self, name: str) -> str:
        cat = self._categorize_device(name)
        if cat in ("USB", "Realtek", "Headset", "Virtual"):
            return cat
        clean = name.split("(")[0].strip()
        return clean[:7]

    def _resolve_device(self, rescan=False):
        devices = self._get_input_devices(rescan=rescan)

        # 1. Jika user memilih mic tertentu secara manual
        if self.device_pref != "auto":
            for idx, name in devices:
                if self.device_pref.lower() in name.lower() or name.lower() in self.device_pref.lower():
                    self.device_idx = idx
                    self.device_name = name
                    self.device_cat = self._categorize_device(name)
                    self.short_name = self._make_short_name(name)
                    return

        # 2. Mode Auto: Prioritaskan USB Mic
        for idx, name in devices:
            if "usb" in name.lower():
                self.device_idx = idx
                self.device_name = name
                self.device_cat = "USB"
                self.short_name = "USB"
                return

        # 3. Headset fisik / Bluetooth
        for idx, name in devices:
            nl = name.lower()
            if any(k in nl for k in ["headset", "baseus", "hands-free", "bluetooth", "external"]):
                if not any(bad in nl for bad in ["virtual", "audiorelay", "stereo mix"]):
                    self.device_idx = idx
                    self.device_name = name
                    self.device_cat = "Headset"
                    self.short_name = "Headset"
                    return

        # 4. Mic Internal laptop (Realtek / Microphone Array)
        for idx, name in devices:
            nl = name.lower()
            if any(k in nl for k in ["realtek", "array", "internal"]):
                self.device_idx = idx
                self.device_name = name
                self.device_cat = "Internal"
                self.short_name = "Realtek"
                return

        # 5. Fallback non-virtual
        for idx, name in devices:
            if not any(bad in name.lower() for bad in ["virtual", "audiorelay", "stereo mix"]):
                self.device_idx = idx
                self.device_name = name
                self.device_cat = "Mic"
                self.short_name = "Mic"
                return

        # 6. Fallback akhir ke default Windows
        try:
            def_idx = sd.default.device[0]
            self.device_idx = def_idx
            self.device_name = sd.query_devices(def_idx)["name"]
        except Exception:
            self.device_idx = None
            self.device_name = "Default"
        self.device_cat = "Default"
        self.short_name = "Default"

    def _init_audio(self):
        self._resolve_device(rescan=True)
        self._update_device_badge()
        self._start_stream()

    def _update_device_badge(self):
        self.btn_device.config(text=f"{self.short_name} ▾")

    def _show_mic_menu(self, event=None):
        """Tampilkan popup menu pilihan mikrofon & pengaturan sensitivitas."""
        # Stop stream sementara untuk scan ulang perangkat USB terbaru
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

        devices = self._get_input_devices(rescan=True)
        self._resolve_device(rescan=False)
        self._start_stream()

        menu = tk.Menu(
            self.root,
            tearoff=0,
            bg="#1e1e2e",
            fg="#cdd6f4",
            activebackground="#45475a",
            activeforeground="#ffffff",
            font=("Segoe UI", 9),
            bd=1,
        )

        menu.add_command(label="--- 🎙️ PILIH MIKROFON ---", state="disabled")

        # Auto Option
        auto_mark = "✓ " if self.device_pref == "auto" else "   "
        menu.add_command(
            label=f"{auto_mark}⭐ Auto (Prioritas USB Mic)",
            command=lambda: self._select_device("auto"),
        )
        menu.add_separator()

        # Daftar perangkat fisik
        for idx, name in devices:
            is_active = (self.device_pref == name) or (self.device_pref == "auto" and idx == self.device_idx)
            mark = "✓ " if is_active else "   "
            menu.add_command(
                label=f"{mark}{name}",
                command=lambda n=name: self._select_device(n),
            )

        menu.add_separator()
        menu.add_command(label="--- 🎚️ SENSITIVITAS SUARA ---", state="disabled")

        for key, p in SENSITIVITY_PROFILES.items():
            mark = "✓ " if self.sens_level == key else "   "
            menu.add_command(
                label=f"{mark}{p['label']}",
                command=lambda k=key: self._set_sensitivity(k),
            )

        menu.add_separator()
        menu.add_command(label="🔄 Pindai Ulang Mic (Rescan USB)", command=self._manual_rescan)
        menu.add_command(
            label="⚙️ Buka Pengaturan Suara Windows",
            command=lambda: os.system("start mmsys.cpl"),
        )

        if event:
            x, y = event.x_root, event.y_root
        else:
            x = self.btn_device.winfo_rootx()
            y = self.btn_device.winfo_rooty() + self.btn_device.winfo_height() + 2
        menu.post(x, y)

    def _select_device(self, name: str):
        self.device_pref = name
        self.config["device_pref"] = name
        self._save_config()
        self._resolve_device(rescan=False)
        self._start_stream()
        self._update_device_badge()
        self._show_temp_status(f"Mic: {self.short_name}")

    def _set_sensitivity(self, level: str):
        self.sens_level = level
        self.config["sensitivity"] = level
        self._save_config()
        self._apply_sensitivity()
        self._show_temp_status(f"Sensitif: {level.upper()}")

    def _manual_rescan(self):
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None
        self._resolve_device(rescan=True)
        self._start_stream()
        self._update_device_badge()
        self._show_temp_status(f"Terhubung: {self.short_name}")

    def _show_temp_status(self, msg: str, duration_ms: int = 1500):
        self.lbl_status.config(text=msg, fg="#89dceb")
        self.root.after(duration_ms, lambda: self.lbl_status.config(text="Spasi 2x: Bicara", fg="#a6adc8"))

    # -------------------------------------------------------------------------
    # FUNGSI STREAMING AUDIO & VAD (VOICE ACTIVITY DETECTION)
    # Alur: Menerima gelombang suara dari mikrofon, mendeteksi apakah pengguna sedang berbicara,
    #       dan otomatis memotong audio setiap kali ada jeda napas/bicara selama 0.42 detik.
    # Tujuan: Mengirim audio ke Google Speech API secara streaming per frasa kalimat
    #         tanpa menunggu tombol mic dimatikan secara manual.
    # -------------------------------------------------------------------------
    def _start_stream(self):
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

        def callback(indata, frames, time_info, status):
            # Penguatan digital (Gain Preamp) agar suara terdengar jelas dari jarak jauh
            if self.gain != 1.0:
                boosted = np.clip(indata.astype(np.float32) * self.gain, -32768, 32767).astype(np.int16)
            else:
                boosted = indata

            peak = float(np.abs(boosted).max())
            self.latest_volume = peak
            if not self.is_recording:
                return

            self.active_phrase_chunks.append(boosted.copy())
            if peak > self.vad_threshold:  # Deteksi suara manusia sensitif
                self.has_spoken = True
                self.silence_count = 0
            else:
                if self.has_spoken:
                    self.silence_count += frames

            # Streaming VAD:
            phrase_frames = sum(len(c) for c in self.active_phrase_chunks)
            pause_limit = int(SAMPLE_RATE * 0.42)
            max_phrase = int(SAMPLE_RATE * 4.2)

            if self.has_spoken and (self.silence_count >= pause_limit or phrase_frames >= max_phrase):
                if phrase_frames >= int(SAMPLE_RATE * 0.35):
                    data = np.concatenate(self.active_phrase_chunks, axis=0)
                    self.transcribe_queue.put(data)
                self.active_phrase_chunks = []
                self.has_spoken = False
                self.silence_count = 0

        try:
            self.stream = sd.InputStream(
                device=self.device_idx,
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="int16",
                callback=callback,
            )
            self.stream.start()
        except Exception:
            self.stream = None

    # -------------------------------------------------------------------------
    # WORKER THREAD PENGUBAH SUARA KE TEKS (SPEECH-TO-TEXT)
    # Alur: Mengambil potongan audio dari antrian (queue), mengirim ke Google Speech Recognition,
    #       lalu jika berhasil langsung memanggil fungsi paste ke aplikasi target.
    # Tujuan: Menghindari GUI Tkinter macet/freeze saat menunggu respon jaringan internet.
    # -------------------------------------------------------------------------
    def _start_worker(self):
        def worker():
            while True:
                chunk = self.transcribe_queue.get()
                if chunk is None:
                    break
                try:
                    audio_data = sr.AudioData(chunk.tobytes(), SAMPLE_RATE, 2)
                    text = self.recognizer.recognize_google(audio_data, language="id-ID")
                    if text:
                        self._paste_text(text)
                        self.root.after(0, lambda: self.lbl_status.config(text="Terketik...", fg="#a6e3a1"))
                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    self.root.after(0, lambda: self.lbl_status.config(text="Koneksi lambat", fg="#fab387"))
                except Exception:
                    pass
                finally:
                    self.transcribe_queue.task_done()

        threading.Thread(target=worker, daemon=True).start()

    # -------------------------------------------------------------------------
    # FUNGSI DETEKSI DOUBLE-TAP SPASI (HOTKEY GLOBAL)
    # Alur: Mencegat tombol spasi; bila dilepas 2x berturut-turut dalam rentang 0.05-0.38 detik,
    #       sistem langsung mengaktifkan perekam suara dan menghapus 2 karakter spasi tadi.
    # Tujuan: Kemudahan aktivasi tercepat tanpa perlu angkat tangan ke mouse atau tombol rumit.
    # -------------------------------------------------------------------------
    def _setup_hotkey(self):
        import keyboard

        def on_key_event(event):
            if event.name == "space" and event.event_type == "up":
                now = time.time()
                diff = now - self.last_space_up_time
                if 0.05 < diff < 0.38:
                    # Double-tap Spasi terdeteksi!
                    self.last_space_up_time = 0
                    self.root.after(0, lambda: self.toggle_recording(from_hotkey=True))
                else:
                    self.last_space_up_time = now

        keyboard.hook(on_key_event)

    def _send_backspaces(self, count=2):
        VK_BACK = 0x08
        KEYEVENTF_KEYUP = 0x0002
        for _ in range(count):
            user32.keybd_event(VK_BACK, 0, 0, 0)
            time.sleep(0.01)
            user32.keybd_event(VK_BACK, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.01)

    # -------------------------------------------------------------------------
    # FUNGSI TOGGLE MULAI / BERHENTI BICARA
    # Alur: Menyimpan HWND aplikasi sebelum merekam, menghapus 2 spasi dari layar,
    #       lalu mengubah state dan visual tombol mic (merah merekam / biru selesai).
    # -------------------------------------------------------------------------
    def toggle_recording(self, from_hotkey=False):
        now = time.time()
        if now - self.last_toggle_time < 0.35:
            return
        self.last_toggle_time = now

        if from_hotkey:
            cur_fg = user32.GetForegroundWindow()
            if cur_fg and cur_fg != self.root_hwnd:
                wnd_pid = ctypes.c_ulong()
                user32.GetWindowThreadProcessId(cur_fg, ctypes.byref(wnd_pid))
                if wnd_pid.value != self.my_pid:
                    self.target_hwnd = cur_fg
            self._send_backspaces(2)

        if not self.is_recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        # Auto-rescan jika saat ini bukan USB tapi user menyetel auto (mungkin baru dicolok)
        if self.device_pref == "auto" and self.device_cat != "USB":
            old_idx = self.device_idx
            self._resolve_device(rescan=True)
            if self.device_idx != old_idx or self.stream is None:
                self._update_device_badge()
                self._start_stream()

        self.active_phrase_chunks = []
        self.has_spoken = False
        self.silence_count = 0
        self.is_recording = True
        self.btn_mic.config(bg="#f38ba8", fg="#11111b")  # Merah (merekam)
        self.lbl_status.config(text=f"Mendengar ({self.short_name})...", fg="#f38ba8")

    def _stop_recording(self):
        self.is_recording = False
        self.btn_mic.config(bg="#89b4fa", fg="#11111b")  # Biru (memproses sisa)
        self.lbl_status.config(text="Selesai", fg="#89b4fa")

        if self.active_phrase_chunks:
            phrase_frames = sum(len(c) for c in self.active_phrase_chunks)
            if phrase_frames >= int(SAMPLE_RATE * 0.35):
                data = np.concatenate(self.active_phrase_chunks, axis=0)
                self.transcribe_queue.put(data)
            self.active_phrase_chunks = []

        self.root.after(800, lambda: self._reset_ui("Spasi 2x: Bicara"))

    # -------------------------------------------------------------------------
    # FUNGSI PENGETIKAN OTOMATIS KE APLIKASI AKTIF (SIMULASI KEYBOARD CTRL+V)
    # Alur: Menyalin teks hasil dikte ke clipboard Windows, mengembalikan fokus jendela
    #       ke aplikasi pengguna (Word/Browser), lalu mengirim kombinasi tombol fisik Ctrl+V.
    # Tujuan: Mengetik instan berkecepatan 0 milidetik tanpa typo karakter per karakter.
    # -------------------------------------------------------------------------
    def _paste_text(self, text: str):
        if not text:
            return
        payload = text.strip() + " "

        for _ in range(3):
            try:
                pyperclip.copy(payload)
                break
            except Exception:
                time.sleep(0.02)

        if self.target_hwnd and user32.IsWindow(self.target_hwnd):
            cur_fg = user32.GetForegroundWindow()
            if cur_fg != self.target_hwnd:
                user32.SetForegroundWindow(self.target_hwnd)
                time.sleep(0.04)

        VK_CONTROL = 0x11
        VK_V = 0x56
        KEYEVENTF_KEYUP = 0x0002
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        time.sleep(0.02)
        user32.keybd_event(VK_V, 0, 0, 0)
        time.sleep(0.04)
        user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

    def _reset_ui(self, msg: str = "Spasi 2x: Bicara"):
        def update():
            self.btn_mic.config(bg="#313244", fg="#cdd6f4")
            self.lbl_status.config(text=msg, fg="#a6adc8")
            if msg != "Spasi 2x: Bicara":
                self.root.after(1500, lambda: self.lbl_status.config(text="Spasi 2x: Bicara", fg="#a6adc8"))
        self.root.after(0, update)

    def close_app(self):
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
        self.root.destroy()
        os._exit(0)


def run_self_check():
    """Self-check audio devices, dynamic scan, and API connectivity."""
    devices = sd.query_devices()
    assert len(devices) > 0, "No audio devices found"
    app_dummy = GboardMicApp.__new__(GboardMicApp)
    app_dummy.config = {"device_pref": "auto", "sensitivity": "max"}
    app_dummy.device_pref = "auto"
    app_dummy.sens_level = "max"
    app_dummy._apply_sensitivity()
    GboardMicApp._resolve_device(app_dummy, rescan=True)
    assert app_dummy.device_idx is not None, "Failed to resolve input device"
    print(f"Self-check selected: [{app_dummy.device_idx}] {app_dummy.device_name} ({app_dummy.short_name})")
    print(f"Sensitivity: Gain={app_dummy.gain}x, VAD Threshold={app_dummy.vad_threshold}")

    r = sr.Recognizer()
    dummy = sr.AudioData(np.zeros(16000, dtype=np.int16).tobytes(), 16000, 2)
    try:
        r.recognize_google(dummy, language="id-ID")
    except sr.UnknownValueError:
        pass
    print("ALL CHECKS PASSED: Audio input + Dynamic Rescan + Google id-ID API ready.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        run_self_check()
    else:
        root = tk.Tk()
        app = GboardMicApp(root)
        root.mainloop()
