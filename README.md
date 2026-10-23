# Claude Workspace & Config

Repositori backup dan sinkronisasi workspace Claude:
- `CLAUDE.md`: Global instructions (Karpathy Guidelines, Superpowers, Caveman style, Curator, dll).
- `agents/`: Custom subagents (misal `curator.md`).
- `skills/`: Custom prompt skills & tools (`comment-refactor`, `handoff`, `session-resume`, `task-observer`, `unslop-ui`).
- `hooks/`: Custom hooks (misal `caveman-statusline.ps1`).
- `memory/`: Persistent memory catatan konteks dan preferensi user (`MEMORY.md`, `user-preferences.md`).
- `plugins/`: Manifest plugin terpasang (`installed_plugins.json`, `known_marketplaces.json`).
- `settings.example.json`: Template konfigurasi Claude Code (tanpa API key).
- `sync.ps1`: Script otomatis untuk update dan push data terbaru ke GitHub.

## Cara Update / Sinkronisasi

Jalankan script `sync.ps1` dari terminal PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File "$HOME\Desktop\Claude\sync.ps1"
```

Atau minta langsung ke Claude:
> *"Tolong update data ke GitHub"*
