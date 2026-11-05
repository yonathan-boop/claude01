---
name: hermes-agent-9router
description: Konfigurasi Hermes Agent terhubung ke 9router lokal model campur via provider custom
metadata:
  node_type: memory
  type: project
  originSessionId: 79304f31-18fe-476b-94f5-79b7e70d0772
  modified: 2026-10-27T03:32:05.144Z
---

Hermes Agent (`~/.hermes/config.yaml` / `AppData/Local/hermes/config.yaml`) dikonfigurasi ke 9router lokal (`http://127.0.0.1:20128/v1`) dengan model `campur`.

**Format Konfigurasi Valid:**
```yaml
model:
  default: campur
  provider: custom
  base_url: http://127.0.0.1:20128/v1
  api_key: sk-550b04f93399b7a7-cdmmjm-b8b1e5c3
  api_mode: chat_completions

providers:
  9router:
    name: 9router
    api: http://127.0.0.1:20128/v1
    api_key: sk-550b04f93399b7a7-cdmmjm-b8b1e5c3
    api_mode: chat_completions
    default_model: campur
    models:
      - campur
```

**Penting:**
- `providers.9router` wajib didefinisikan agar Hermes v51 mengenali canonical custom identity (`custom:9router`) dan tidak me-reset endpoint saat session resume atau cold-start.
- Desktop app menyimpan sticky selection di Chromium `Local Storage` (`hermes.desktop.composer.model-source...`). Jika pernah fallback ke Gemini, bersihkan cache `AppData\Roaming\Hermes\Local Storage` dan hapus sesi Gemini lama agar Desktop otomatis mengadopsi default `campur` dari gateway.
- Gateway Hermes otomatis mendeteksi context window 1M tokens saat connect ke 9router.
