# Rencana Implementasi: Mode Chat Modern Berbasis ConPTY Terminal Hub (`ssh.html`)

> **Konteks & Validasi Kebutuhan:**
> User meminta: *"buat seperti sistem chattingan saja.. tapi di belakangnya terminal gitu"*
> Antarmuka terminal raw xterm saat ini rentan glitch wrapping teks, cursor jumping escape ANSI (`Polishing...`, `[?25h`), dan kurang nyaman dibaca di layar HP/browser.
> Solusi: Menghadirkan antarmuka percakapan (Chat View) yang bersih, estetik (bubble chat ChatGPT/WhatsApp style), responsif, dan mudah dibaca di mobile/desktop, dengan mesin terminal ConPTY tetap berjalan 100% stabil di belakang layar.

---

## 1. Arsitektur & Prinsip Desain

1. **Dual-View Switcher (Zero Risk & 100% Fleksibel)**:
   - Tambahkan toggle view di header: **`[💬 Mode Chat]`** dan **`[⌨️ Mode Terminal]`**.
   - User dapat berpindah mode seketika (toggle `display: flex/none`) tanpa reload dan tanpa kehilangan state.
   - Pilihan mode tersimpan di `localStorage.getItem('terminal_view_mode')` (default: `chat`).

2. **Sinkronisasi 2-Arah (Chat View <-> PTY Stream)**:
   - **Kirim Pesan (User -> PTY)**:
     - User mengetik di input bar bawah -> tekan Enter / tombol Kirim.
     - Bubble pesan user (kanan) langsung muncul dengan teks rapi.
     - Teks dikirim ke WebSocket PTY (`{ type: 'input', data: text + '\r' }`).
     - Bubble balasan baru (kiri) otomatis disiapkan untuk menampung output streaming.
   - **Terima Output (PTY -> Chat Bubble)**:
     - Data streaming ANSI dari ConPTY tetap diteruskan ke instance xterm di background (agar riwayat terminal utuh).
     - Parser ANSI regex membersihkan escape codes (`\x1b\[[0-9;]*[a-zA-Z]`, spinner artifacts `Polishing...`, `[?25h`) menjadi teks bersih.
     - Output ditambahkan secara real-time ke bubble balasan terminal/AI dengan auto-scroll ke bawah.
     - Blok kode Markdown (```...```) dan path file otomatis diformat dengan syntax highlight dan tombol salin 📋.

3. **Proteksi Sesi Aktif (Zero Downtime)**:
   - Perubahan hanya pada file client-side `C:\Users\yonat\dashboard\public\ssh.html`.
   - **DILARANG MERESTART `terminal-hub`**: Karena sesi Claude Code saat ini sedang berjalan di dalam ConPTY `terminal-hub`. Perubahan HTML langsung aktif pada refresh browser (`F5`).

---

## 2. Struktur Komponen UI Baru di `ssh.html`

### A. Header Navigation:
- Tombol Toggle:
  ```html
  <div class="view-mode-switch">
    <button id="btn-mode-chat" class="mode-btn active" title="Tampilan Chat">💬 Chat</button>
    <button id="btn-mode-term" class="mode-btn" title="Tampilan Raw Terminal">⌨️ Terminal</button>
  </div>
  ```

### B. Chat Container (`#chat-container`):
- Area pesan beralas pekat (`#08090C` OLED Dark) dengan scroll momentum mulus.
- **Bubble User (Kanan)**:
  - Background biru gelap aksen (`#1e3a8a` / `#1d4ed8`), border halus, border-radius 16px 16px 4px 16px.
  - Waktu kirim & tombol salin teks.
- **Bubble Terminal / AI (Kiri)**:
  - Background slate pekat (`#0f172a`), border `#1f293d`, border-radius 16px 16px 16px 4px.
  - Teks terbaca jelas (sans-serif / font Cascadia Code untuk blok perintah).
  - Tampilan collapsible jika output log > 25 baris (tombol *"Lihat N baris log lengkap"*).
  - Indikator status typing/berpikir saat terminal aktif memproses output.

### C. Input Bar & Toolbar Terpadu:
- Textarea fleksibel (auto-grow 1–5 baris).
- Tombol Kirim (`↵ Kirim`), Shortcut Cepat (`Esc`, `Ctrl+C`, `Clear`, `/compact`), dan Tombol Kamera 📷 untuk upload gambar.

---

## 3. Rincian Modifikasi File

### File: `C:\Users\yonat\dashboard\public\ssh.html`
1. **CSS Styling**:
   - Styling `#chat-container`, `.chat-stream`, `.chat-bubble-user`, `.chat-bubble-bot`, `.chat-timestamp`, `.code-block`, `.log-collapse`.
   - Responsive styling untuk mobile HP (<600px) dan desktop (>768px).
2. **HTML Layout**:
   - Sisipkan `<div id="chat-container">...</div>` berdampingan dengan `#terminal-container`.
   - Tambahkan tombol switcher view di header.
3. **JavaScript Engine**:
   - Fungsi `toggleViewMode('chat' | 'term')`.
   - Parser `cleanAnsiText(rawText)` untuk membersihkan artifak TUI, cursor positioning, dan escape sequence.
   - Manajemen percakapan `appendUserChat(text)` & `appendBotStream(textChunk)`.
   - Inisialisasi awal: jika membuka riwayat sesi lama, otomatis ekstrak output terkini menjadi bubble chat terstruktur.

---

## 4. Rencana Verifikasi & Pengujian

1. **Uji Sintaks & Integrasi**:
   - Validasi file `ssh.html` bebas error sintaks JavaScript.
2. **Uji Visual Playwright (Headless Browser)**:
   - Navigasi ke `http://127.0.0.1:8900/ssh/`.
   - Ambil screenshot tampilan Mode Chat (mobile viewport 390x844 & desktop 1280x720).
   - Verifikasi bubble user dan bubble bot ter-render dengan rapi tanpa glitch.
3. **Uji Fungsional Pengiriman Pesan**:
   - Ketik pesan/perintah lewat input bar di browser.
   - Verifikasi respon terminal masuk ke bubble bot dan diteruskan ke PTY ConPTY.
   - Toggle ke `[⌨️ Mode Terminal]` untuk membuktikan raw xterm tetap 100% sinkron.
