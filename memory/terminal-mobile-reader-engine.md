---
name: terminal-mobile-reader-engine
description: Arsitektur Mode Rapi (Reader/Chat View) dan Word Healing untuk Terminal SSH Mobile di Server YN
metadata:
  node_type: memory
  type: project
  originSessionId: 5c02ae63-a9ad-47d1-a6b8-e92acf72fef9
  modified: 2026-11-05T10:04:34.787Z
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
