# Skill Observation Log

## Observation: 2026-11-05 - Decoupled Terminal Mobile Reader & Word Healing
- **Trigger**: User mengeluhkan teks di HP berantakan, kata terbelah dua (`Reconnec` + `t:`), dan kelanjutan kalimat jatuh sendirian di kolom 0 (`Raw.`, `jempol.`).
- **Akar Masalah**:
  1. Terminal VT100 / xterm pada smartphone menyusutkan kolom ke ~36 karakter saat font diperbesar.
  2. Windows ConPTY memotong teks pada kolom ke-36 tanpa memeriksa spasi kata.
  3. Baris kelanjutan dari sebuah poin bullet diperlakukan sebagai paragraf baru `<p>` yang jatuh ke kolom 0.
  4. Floating nav dan unread pill menutupi baris teks di layar sentuh sempit.
- **Solusi**:
  1. Memisahkan proses CLI (PTY backend) dari presentasi visual mobile (`Reader Mode`).
  2. Word healing menggunakan `line.isWrapped` buffer xterm dan heuristik batas kolom ConPTY.
  3. Block & Bullet Grouping (`groupBlocks`) yang menyatukan baris-baris sambungan ke dalam satu poin bullet atau satu paragraf utuh.
  4. Kontrol non-intrusif: tombol floating pad dinonaktifkan di layar HP, chip `⤒ Top` & `⤓ Bawah` diletakkan di toolbar bawah, tombol unread pill digeser ke pojok kanan bawah.
- **Status**: IMPLEMENTED & VERIFIED (`dashboard/public/ssh.html`).
