---
name: web-reach
description: "Alat jelajah internet & konten lintas platform (Web, GitHub, YouTube, Reddit, V2EX, Bilibili) tanpa API key berbayar. Gunakan untuk mencari materi web, membaca artikel/dokumentasi bersih, membaca repositori & issue GitHub, serta membaca transkrip/subtitle video."
---

# Web Reach (Jelajah Web & Platform Terbuka)

Modul jelajah internet mandiri Node 01. Menyediakan pencarian semantik web bersih, ekstraksi artikel bebas iklan, dan pembacaan konten platform publik tanpa biaya API.

## Perintah CLI Utama

```powershell
# 1. Pencarian Web Bersih (Semantic Search via Exa)
web-reach web search "kata kunci pencarian"

# 2. Baca Halaman Web sebagai Teks / Markdown Bersih
web-reach web read "https://contoh.com/artikel"

# 3. GitHub (Cari & Baca Repositori, README, Issue, PR)
web-reach github search "query repo"
web-reach github read "https://github.com/owner/repo"

# 4. YouTube (Metadata & Subtitle)
web-reach youtube search "query video"
web-reach youtube read "https://www.youtube.com/watch?v=..."
web-reach youtube subtitle "https://www.youtube.com/watch?v=..."

# 5. Reddit & Forum Terbuka
web-reach reddit search "query topik"
web-reach reddit read "https://www.reddit.com/r/.../comments/..."
web-reach v2ex hot
```

## Karakteristik Operasional
- **Zero API Fee:** Mengambil data publik langsung tanpa butuh kredensial berbayar.
- **Isolasi Lingkungan:** Berjalan sepenuhnya di bawah Node 01 dengan wrapper eksekusi Windows aman.
- **Read-Only:** Khusus untuk membaca, mencari, dan menganalisis informasi, tanpa interaksi mutasi.
