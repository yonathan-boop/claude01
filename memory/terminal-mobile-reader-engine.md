---
name: terminal-mobile-reader-engine
description: Arsitektur Mode Rapi (Reader/Chat View) dan Word Healing untuk Terminal SSH Mobile di Server YN
metadata:
  node_type: memory
  type: project
  originSessionId: 5c02ae63-a9ad-47d1-a6b8-e92acf72fef9
  modified: 2026-11-05T11:14:56.689Z
---

# Terminal Mobile Reader Engine (Mode Rapi)

Solusi arsitektur untuk mengatasi keterbatasan terminal VT100 / xterm.js pada layar smartphone (resolusi sempit ~36–42 kolom).

## Akar Masalah Terminal Klasik di Mobile
1. **Grid Monospace Terlalu Lebar**: Terminal standar mengasumsikan monitor 80 kolom. Di HP, font 16px mempersempit terminal menjadi ~36 karakter per baris.
2. **Pemotongan Kata Kasar (ConPTY Hard Cut)**: Windows ConPTY memotong teks pada kolom ke-36 tanpa memeriksa batas spasi, membelah kata di tengah huruf (`Reconnec` + `t:`, `a` + `ntarmuka`).
3. **Continuation Lines Hanging**: Baris sambungan dari sebuah poin bullet terlempar ke kolom 0 sebagai paragraf terpisah (`<p>`), membuat kata pelengkap seperti `Raw.` atau `jempol.` menggantung sendirian.
4. **Elemen UI Mengambang Menutupi Teks**: Kotak 4 tombol floating kanan dan pill jump-to-bottom menutupi kalimat ujung kanan dan baris pesan user.

## Solusi: Decoupling Eksekusi PTY dari Presentasi Layar
Memisahkan proses eksekusi CLI (tetap berjalan di background ConPTY) dari lapisan visual HP:

1. **Word Healing Engine (`line.isWrapped` + Heuristik)**:
   - Membaca properti `line.isWrapped` dari buffer xterm untuk menyambungkan baris yang terpotong tanpa menambahkan `\n`.
   - Dilengkapi heuristik batas kolom jika ConPTY menyisipkan hard CRLF pada karakter ke-34–36, sehingga kata-kata Indonesia yang terbelah otomatis utuh kembali.
2. **Block & Bullet Grouping (`groupBlocks`)**:
   - Menyatukan baris-baris sambungan ke dalam satu objek blok bullet (`.reader-bullet`) atau paragraf (`.reader-para`).
   - Tidak ada lagi kata menggantung di ujung kiri; seluruh poin mengalir dalam indentasi yang presisi.
   - Deteksi otomatis judul seksi bernomor (`2. Judul:`) menjadi header bergaris bawah.
   - Format prompt user (`> ...`) menjadi kartu chat bubble modern rata kanan.
3. **Ergonomi Kontrol Mobile & Anti-Freeze Scroll**:
   - **Touch Guard (`isUserTouchingReader`)**: Saat jari user menyentuh/menggeser layar, pembaruan DOM `innerHTML` dan auto-scroll seketika ditangguhkan agar browser tidak membatalkan gesture sentuh dan tidak menyentak posisi scroll kembali ke bawah saat AI sedang berpikir/streaming.
   - **Throttling Render 250ms**: Mengurangi beban CPU dan mencegah thrashing DOM berulang saat spinner animasi CLI berjalan.
   - **Pembersihan Artifak Kaki-kaki**: Memfilter petunjuk status bar interaktif CLI (`to cycle`, `esc to interrupt`, `ctrl+b`) dan memformat baris eksekusi tool CLI (`└ $ Start-Process...`, `curl.exe`) menjadi badge pill terisolasi (`.reader-tool-pill`) sehingga tidak merusak kartu chat prompt user.
   - **Bottom Padding 85px**: Memberikan ruang lega di bagian bawah agar baris terakhir tidak terpotong oleh composer input bar.
   - **Strict Wrap Merge**: Hanya menyambungkan baris yang benar-benar ditandai `item.isWrapped` oleh xterm untuk mencegah kata bertumpuk atau bercampur antar-baris.
4. **Prompt History & Quick Navigator Engine (`▲ Prompt` / `▼ Prompt` & Drawer Sheet)**:
   - **Sticky Task Banner**: Menampilkan ringkasan tugas aktif terkini di baris teratas reader view (`📌 Tugas Terkini: "..." [Lompat ➔]`), sehingga saat user berganti-ganti terminal banyak, langsung paham tugas terminal ini dalam 0 detik tanpa perlu mencari-cari ke atas.
   - **Drawer Riwayat Pesan (`💬 N`)**: Tombol header yang membuka modal bottom sheet berisi semua riwayat prompt user (#1, #2, #3, ...) dari yang terbaru. Mengetuk item langsung melakukan *smooth-scroll* ke posisi pesan tersebut dan memicu animasi pulse glow biru terang (`.reader-prompt-highlight`).
   - **Tombol Navigasi Toolbar (`▲ Prompt` / `▼ Prompt`)**: Melompat mundur/maju antar pesan user secara instan langsung dari toolbar chip bawah dengan notifikasi toast urutan pesan.
5. **Hierarki Warna Semantik & Deduplikasi Prompt (Anti-Spam)**:
   - **Pewarnaan Semantik Kaya (Tidak Lagi Putih Monoton)**:
     * Judul / Header Seksi: Biru Langit cerah (`#38bdf8`).
     * Kata Kunci / Teks Tebal (`**...**`): Kuning Emas / Amber Gold (`#fbbf24`) agar langsung tertangkap mata saat *scanning* cepat.
     * Kode / Path / Perintah (`code`): Hijau Zamrud (`#34d399`) dengan kontras tinggi.
     * Eksekusi Tool CLI: Ungu Violet (`#c084fc`).
     * Gelembung Pesan Pengguna: Kartu Biru Navy elegan (`#bfdbfe`).
     * Teks Paragraf Biasa: Abu Slate ramah mata (`#cbd5e1`), tidak menyilaukan.
   - **Deduplikasi Prompt Bertingkat**: Mengatasi bug pesan ganda berulang (seperti 5x pesan yang sama di drawer dan tampilan chat) akibat *terminal character echo* atau *re-render* TUI ConPTY, sehingga setiap instruksi user hanya tampil tepat 1 kali.
6. **Buku Besar Prompt Persisten (`localStorage` per Sesi)**:
   - **Akar Masalah Reset ke 0**: Sebelumnya riwayat prompt hanya disimpan di variabel memori JS dan mengandalkan pembacaan layar xterm. Begitu respon AI melebihi 30 baris (tinggi layar terminal), prompt terdorong keluar dari buffer alternate screen (`baseY === 0`), sehingga saat browser di-refresh atau dibuka ulang, counter kembali menjadi 0 pesan.
   - **Solusi Buku Besar Persisten**: Menyimpan riwayat prompt secara otomatis dan permanen di `localStorage` per ID sesi (`ssh_prompts_${sessionId}`) seketika user menekan tombol Kirim.
   - **Tahan Refresh & Antar Sesi Mandiri**: Riwayat pesan tidak pernah ter-reset ke 0 meskipun halaman di-refresh, browser ditutup, atau koneksi terputus. Tiap tab terminal memiliki daftar riwayatnya masing-masing secara terisolasi.
   - **Fitur Cepat Setiap Pesan**: Setiap entri di drawer dilengkapi tombol 'Lompat ➔' (menuju posisi pesan), 'Pakai Lagi ↺' (memasukkan kembali ke kotak ketik untuk diedit/dikirim ulang), dan 'Salin 📋'.
7. **Perbaikan Spasi Non-Breaking (` `) & Anti-Spam Redraw Claude Code**:
   - **Akar Masalah Non-Breaking Space**: Claude Code CLI menggunakan simbol `❯ ` (karakter spasi `0xC2 0xA0`, bukan spasi ASCII biasa). Akibatnya `startsWith('❯ ')` gagal mencocokkan prompt dan counter selalu 0. Dilakukan normalisasi global `  -> ' '` dan regex `/^[>❯❯]\s*(.+)/`.
   - **Akar Masalah Balasan Terulang 7 Kali (Spam)**: Ketika Claude sedang memproses perintah, antarmuka Ink/React CLI me-*redraw* pesan antrean bersama teks `ctrl+x ctrl+s to send now` dan `Press up to edit queued messages` setiap putaran spinner. ConPTY merekam setiap putaran layar itu ke scrollback. Diterapkan pembersihan trailing widget CLI dan pelacak `seenPromptTexts` global sehingga tiap pesan hanya tampil tepat 1 kali di layar.
