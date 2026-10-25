---
name: openjarvis-9router-bridge
description: Konfigurasi OpenJarvis Desktop menghubungkan ke 9router lokal model campur via shim port 11434 & server port 8000
metadata:
  node_type: memory
  type: project
  originSessionId: cde1a58a-89a3-4b06-a36e-76dfe5f5804c
  modified: 2026-10-25T12:36:10.995Z
---

OpenJarvis Desktop (v1.0.1) di-bypass dari dependensi Ollama lokal dan dihubungkan langsung ke 9router port 20128 dengan model `campur`.

**Arsitektur & Konfigurasi:**
1. **Ollama Compatibility Shim (`C:\Users\yonat\OpenJarvis\ollama-shim.js`):**
   - Mendengarkan pada `127.0.0.1:11434`.
   - Mengembalikan fake tags (`qwen3.5:4b`, `campur`) agar OpenJarvis Desktop setup check lolos instan tanpa download model lokal.
   - Meneruskan `/api/chat` ke 9router (`127.0.0.1:20128/v1/chat/completions`) dengan bearer key 9router.
2. **OpenJarvis API Server (`127.0.0.1:8000`):**
   - Daemon dijalankan via `uv run jarvis start -e lmstudio -m campur`.
   - Engine `lmstudio` diarahkan ke `http://127.0.0.1:20128`.
   - Kredensial tersimpan di `C:\Users\yonat\.openjarvis\credentials.toml` dan `config.toml`.
3. **Desktop Launcher & Shortcut:**
   - Shortcut `C:\Users\yonat\Desktop\OpenJarvis.lnk` mengarah ke `C:\Users\yonat\OpenJarvis\launch-openjarvis.vbs`.
   - Menjamin port 11434 dan port 8000 otomatis aktif sebelum GUI desktop dibuka tanpa console popup.
