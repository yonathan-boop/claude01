---
name: browser-cdp
description: "Automasi peramban Google Chrome via Chrome DevTools Protocol (CDP) tanpa mencuri kursor mouse fisik pengguna. Gunakan untuk membaca DOM halaman aktif, inspeksi sesi web login, interaksi formulir/tombol, dan navigasi web interaktif di Node 01."
---

# Browser CDP (Otomasi Chrome Tanpa Pembajakan Mouse)

Modul automasi peramban Google Chrome berbasis Chrome DevTools Protocol (CDP). Menggunakan alat Playwright MCP (`mcp__playwright__*`) langsung terhadap struktur DOM sehingga pengguna tetap bisa mengetik dan menggerakkan mouse secara normal tanpa terganggu.

## Keunggulan
- **Zero Cursor Hijack**: Tidak ada pergerakan kursor fisik atau konflik resolusi/scaling Windows.
- **Akses Tab Nyata**: Mampu membaca tab aktif, sesi cookie yang sudah login, dan struktur DOM rendered.

## Menyiapkan Chrome CDP di PC Lokal

### Cara 1: Jalankan Chrome Mode CDP (1-Perintah)
```powershell
start-chrome-debug
```
Perintah ini otomatis membuka Google Chrome dengan port debugging `9222` dan profil terisolasi tanpa merusak profil utama pengguna.

### Cara 2: Aktifkan di Chrome yang Sedang Berjalan
1. Buka tab baru di Chrome: `chrome://inspect/#remote-debugging`
2. Centang opsi: **Allow remote debugging for this browser instance**

## Alur Kerja Automasi AI (Playwright MCP)
1. **Daftar Tab:**
   Gunakan tool `mcp__playwright__browser_tabs` dengan action `list` untuk melihat semua tab aktif.
2. **Pilih Tab:**
   Gunakan `mcp__playwright__browser_tabs` dengan action `select` dan index target.
3. **Baca DOM (Snapshot):**
   Gunakan `mcp__playwright__browser_snapshot` untuk mendapatkan hierarki elemen teks, tombol, dan input.
4. **Klik / Ketik:**
   Gunakan `mcp__playwright__browser_click` atau `mcp__playwright__browser_type` dengan selektor yang terbaca dari snapshot DOM.
5. **Tangkapan Layar:**
   Gunakan `mcp__playwright__browser_take_screenshot` untuk melihat tampilan visual jika dibutuhkan.

## Pantangan
- Dilarang menggunakan simulasi klik mouse fisik koordinat Windows jika elemen bisa dijangkau via Playwright/CDP DOM.
