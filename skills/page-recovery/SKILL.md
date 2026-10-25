---
name: page-recovery
description: "Pemulihan dan pembacaan halaman web yang diblokir Cloudflare, WAF, bot-detection, paywall, atau error 403/429. Menggunakan ladder mirror: Jina Reader live render -> Wayback Machine snapshot -> archive.today domain rotation."
---

# Page Recovery (Bypass Blokir Web & WAF Ladder)

Gunakan alat ini saat mengambil konten web tapi terhalang Cloudflare ("Just a moment..."), error 403 Forbidden, 429 Too Many Requests, atau paywall.

## Tangga Pemulihan (Recovery Ladder)
1. **Jina Reader (`r.jina.ai`)**: Render langsung sisi server (konten live).
2. **Wayback Machine (`archive.org`)**: Snapshot arsip terdekat dengan timestamp.
3. **archive.today**: Rotasi domain mirror (`archive.ph`, `archive.md`, `archive.is`).

Semua hasil diverifikasi otomatis: menolak stub redirect, halaman stub berukuran kecil (<2KB), dan judul blokir ("access denied", "attention required", "are you a robot").

## Perintah CLI

```powershell
# Baca dan tampilkan pratinjau teks halaman
page-recovery "https://contoh.com/artikel-terblokir"

# Format output JSON (untuk parsing agen)
page-recovery "https://contoh.com/artikel-terblokir" --json

# Simpan isi halaman yang dipulihkan ke berkas lokal
page-recovery "https://contoh.com/artikel-terblokir" --out "hasil_halaman.html"
```

## Disiplin Asal-Usul (Provenance)
- Jika berasal dari **`live`** (Jina): Data merupakan versi langsung saat ini.
- Jika berasal dari **`snapshot`** (Wayback / archive.today): Data merupakan rekaman historis; cantumkan tanggal snapshot jika relevan dengan informasi waktu sensitif.
