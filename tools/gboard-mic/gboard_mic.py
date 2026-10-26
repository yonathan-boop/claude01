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
Hotkey: Spasi 2x (Double-Tap Spasi) untuk mulai/selesai.
"""

import ctypes
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
        self.recognizer = sr.Recognizer()
        self.target_hwnd = None
        self.root_hwnd = None

        self._build_ui()
        self._setup_drag()
        self._init_audio()
        self._setup_hotkey()
        self._start_worker()

        self.root.after(100, self._capture_root_hwnd)
        self.root.after(200, self._poll_target_window)
        self.root.after(35, self._update_visualizer)

    def _build_ui(self):
        self.frame = tk.Frame(self.root, bg="#1e1e2e", highlightthickness=1, highlightbackground="#45475a", bd=0)
        self.frame.pack(fill="both", expand=True)

        self.btn_mic = tk.Button(
            self.frame,
            text="🎙️",
            font=("Segoe UI Emoji", 13),
            bg="#313244",
            fg="#cdd6f4",
            activebackground="#45475a",
            activeforeground="#ffffff",
            bd=0,
            padx=7,
            pady=2,
            command=self.toggle_recording,
            cursor="hand2",
        )
        self.btn_mic.pack(side="left", padx=(6, 2), pady=4)

        # Visualizer Canvas (Waveform Naik-Turun)
        self.canvas_wave = tk.Canvas(
            self.frame,
            width=38,
            height=22,
            bg="#1e1e2e",
            highlightthickness=0,
            bd=0,
        )
        self.canvas_wave.pack(side="left", padx=(2, 4), pady=4)
        self.wave_bars = []
        bar_xs = [4, 11, 18, 25, 32]
        for bx in bar_xs:
            bar_id = self.canvas_wave.create_line(bx, 10, bx, 12, fill="#45475a", width=3, capstyle="round")
            self.wave_bars.append((bar_id, bx))

        self.lbl_status = tk.Label(
            self.frame,
            text="Spasi 2x: Bicara",
            font=("Segoe UI", 9, "bold"),
            bg="#1e1e2e",
            fg="#a6adc8",
            padx=2,
        )
        self.lbl_status.pack(side="left", padx=(2, 4), pady=4)

        self.btn_close = tk.Button(
            self.frame,
            text="✕",
            font=("Segoe UI", 8),
            bg="#1e1e2e",
            fg="#6c7086",
            activebackground="#f38ba8",
            activeforeground="#11111b",
            bd=0,
            padx=6,
            pady=2,
            command=self.close_app,
            cursor="hand2",
        )
        self.btn_close.pack(side="right", padx=(2, 6), pady=4)

        # Posisi default: Pojok kanan bawah di atas taskbar
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        w, h = 240, 42
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

        self.frame.bind("<Button-1>", start_drag)
        self.frame.bind("<B1-Motion>", do_drag)
        self.lbl_status.bind("<Button-1>", start_drag)
        self.lbl_status.bind("<B1-Motion>", do_drag)
        self.canvas_wave.bind("<Button-1>", start_drag)
        self.canvas_wave.bind("<B1-Motion>", do_drag)

    def _capture_root_hwnd(self):
        self.root_hwnd = user32.GetForegroundWindow()

    def _poll_target_window(self):
        fg = user32.GetForegroundWindow()
        # Simpan window aktif pengguna selain window widget ini
        if fg and fg != self.root_hwnd and fg != self.root.winfo_id():
            self.target_hwnd = fg
        self.root.after(200, self._poll_target_window)

    def _update_visualizer(self):
        # Smoothing volume decay
        self.display_volume = self.display_volume * 0.60 + self.latest_volume * 0.40
        norm = min(1.0, max(0.0, self.display_volume / 2000.0))

        multipliers = [0.6, 1.1, 1.4, 0.9, 0.5]
        for i, (bar_id, bx) in enumerate(self.wave_bars):
            if not self.is_recording:
                # Diam: titik abu-abu
                self.canvas_wave.coords(bar_id, bx, 10, bx, 12)
                self.canvas_wave.itemconfig(bar_id, fill="#45475a")
            else:
                # Dinamis: gelombang bergerak sesuai desibel suara
                bar_h = max(2, int(norm * multipliers[i] * 18))
                y1 = max(1, 11 - bar_h // 2)
                y2 = min(21, 11 + bar_h // 2)
                if norm > 0.4:
                    color = "#f38ba8" if norm > 0.75 else "#89dceb"
                else:
                    color = "#a6e3a1"
                self.canvas_wave.coords(bar_id, bx, y1, bx, y2)
                self.canvas_wave.itemconfig(bar_id, fill=color)

        self.root.after(35, self._update_visualizer)

    def _find_best_input_device(self):
        # ponytail: prioritize USB mic, fallback to headset/internal, avoid virtual/audiorelay
        devices = sd.query_devices()
        input_devs = []
        for i, d in enumerate(devices):
            if d.get("max_input_channels", 0) > 0 and d.get("hostapi") == 0:
                input_devs.append((i, d["name"]))

        # 1. Prioritize USB Mic
        for idx, name in input_devs:
            if "usb" in name.lower():
                return idx, name, "USB"

        # 2. Prioritize external headset / bluetooth mic
        for idx, name in input_devs:
            nl = name.lower()
            if any(k in nl for k in ["headset", "baseus", "hands-free", "bluetooth", "external"]):
                if not any(bad in nl for bad in ["virtual", "audiorelay", "stereo mix"]):
                    return idx, name, "Headset"

        # 3. Built-in physical mic (Realtek / Microphone Array)
        for idx, name in input_devs:
            nl = name.lower()
            if any(k in nl for k in ["realtek", "array", "internal"]):
                return idx, name, "Internal"

        # 4. Fallback (skip Virtual Mic if possible)
        for idx, name in input_devs:
            if not any(bad in name.lower() for bad in ["virtual", "audiorelay", "stereo mix"]):
                return idx, name, "Mic"

        return sd.default.device[0], "Default", "Default"

    def _init_audio(self):
        self.device_idx, self.device_name, self.device_cat = self._find_best_input_device()
        self._start_stream()

    def _start_stream(self):
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

        def callback(indata, frames, time_info, status):
            peak = float(np.abs(indata).max())
            self.latest_volume = peak
            if not self.is_recording:
                return

            self.active_phrase_chunks.append(indata.copy())
            if peak > 120:  # Suara manusia terdeteksi
                self.has_spoken = True
                self.silence_count = 0
            else:
                if self.has_spoken:
                    self.silence_count += frames

            # Real-time VAD streaming:
            # Jika jeda hening > 0.42 detik (napas) atau frase sudah 4.2 detik, segera kirim & ketik
            phrase_frames = sum(len(c) for c in self.active_phrase_chunks)
            pause_limit = int(SAMPLE_RATE * 0.42)
            max_phrase = int(SAMPLE_RATE * 4.2)

            if self.has_spoken and (self.silence_count >= pause_limit or phrase_frames >= max_phrase):
                if phrase_frames >= int(SAMPLE_RATE * 0.4):
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

    def toggle_recording(self, from_hotkey=False):
        now = time.time()
        if now - self.last_toggle_time < 0.35:
            return
        self.last_toggle_time = now

        if from_hotkey:
            # Hapus 2 karakter spasi yang sempat terketik saat double-tap
            self._send_backspaces(2)

        if not self.is_recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        # Refresh device in case USB mic was plugged in or unplugged
        cur_idx, cur_name, cur_cat = self._find_best_input_device()
        if cur_idx != self.device_idx or self.stream is None:
            self.device_idx, self.device_name, self.device_cat = cur_idx, cur_name, cur_cat
            self._start_stream()

        self.active_phrase_chunks = []
        self.has_spoken = False
        self.silence_count = 0
        self.is_recording = True
        self.btn_mic.config(bg="#f38ba8", fg="#11111b")  # Merah (merekam)
        self.lbl_status.config(text=f"Mendengar ({self.device_cat})...", fg="#f38ba8")

    def _stop_recording(self):
        self.is_recording = False
        self.btn_mic.config(bg="#89b4fa", fg="#11111b")  # Biru (memproses sisa)
        self.lbl_status.config(text="Selesai", fg="#89b4fa")

        # Flush sisa audio terakhir jika ada
        if self.active_phrase_chunks:
            phrase_frames = sum(len(c) for c in self.active_phrase_chunks)
            if phrase_frames >= int(SAMPLE_RATE * 0.35):
                data = np.concatenate(self.active_phrase_chunks, axis=0)
                self.transcribe_queue.put(data)
            self.active_phrase_chunks = []

        self.root.after(800, lambda: self._reset_ui("Spasi 2x: Bicara"))

    def _paste_text(self, text: str):
        if not text:
            return
        # Tambahkan spasi di ujung agar kata tersambung alami
        pyperclip.copy(text.strip() + " ")

        if self.target_hwnd:
            user32.SetForegroundWindow(self.target_hwnd)
            time.sleep(0.06)

        # Kirim Ctrl + V
        VK_CONTROL = 0x11
        VK_V = 0x56
        KEYEVENTF_KEYUP = 0x0002
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        user32.keybd_event(VK_V, 0, 0, 0)
        time.sleep(0.03)
        user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
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
            self.stream.stop()
            self.stream.close()
        self.root.destroy()
        os._exit(0)


def run_self_check():
    """Self-check audio devices and API connectivity."""
    devices = sd.query_devices()
    assert len(devices) > 0, "No audio devices found"
    app_dummy = GboardMicApp.__new__(GboardMicApp)
    dev_idx, dev_name, dev_cat = GboardMicApp._find_best_input_device(app_dummy)
    assert dev_idx is not None, "Failed to resolve input device"
    print(f"Self-check selected: [{dev_idx}] {dev_name} ({dev_cat})")
    r = sr.Recognizer()
    dummy = sr.AudioData(np.zeros(16000, dtype=np.int16).tobytes(), 16000, 2)
    try:
        r.recognize_google(dummy, language="id-ID")
    except sr.UnknownValueError:
        pass
    print("ALL CHECKS PASSED: Audio input + Google id-ID API ready.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        run_self_check()
    else:
        root = tk.Tk()
        app = GboardMicApp(root)
        root.mainloop()
