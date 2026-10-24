---
name: rule-enforcement-engine
description: "Arsitektur pagar fisik Rule Enforcement Engine di Node 01 via hook PreToolUse dan permanent-rules.json"
metadata:
  node_type: memory
  type: project
  originSessionId: a6562376-15b8-410d-9b8f-e803f7a93d16
  modified: 2026-10-24T07:09:10.549Z
---

Sistem pagar fisik di Node 01 menggunakan hook kernel Claude Code (`PreToolUse`) untuk menolak operasi terlarang secara fisik sebelum tool dieksekusi di Windows.

## Komponen:
1. **Hook Interceptor**: `C:\Users\yonat\.claude\hooks\rule-guard.js`
   - Terdaftar di `C:\Users\yonat\.claude\settings.json` event `PreToolUse`.
   - Intersep tool: `Write`, `Edit`, `MultiEdit`, `PowerShell`, `Bash`.
   - Menolak perintah terlarang dengan Exit Code 2 dan output format harness Claude Code.
2. **Database Aturan**: `C:\Users\yonat\.claude\rules\permanent-rules.json`
   - `RULE-PUSH-CLAUDE01-ONLY`: Blokir push ke `claude02`, `Opencode`, `11111`. Hanya izinkan push ke repositori Node 01.
   - `RULE-PROTECT-OPENCODE`: Blokir Write/Edit/terminal write ke `C:\Users\yonat\OPENCODE` dan `OneDrive\Desktop\memory`.
   - `RULE-PROTECT-OFFICE`: Blokir taskkill/Stop-Process pada `WINWORD.EXE`, `EXCEL.EXE`, `POWERPNT.EXE`.
   - `RULE-PAGAR-TEST`: Proteksi fisik file uji.

## Uji Verifikasi Fisik:
- `git push ... claude02` -> DITOLAK (PreToolUse hook error: Blocked by hook).
- `Write` ke `pagar-test.txt` -> DITOLAK (PreToolUse hook error: Blocked by hook).
- `git -C Opencode\memory push` -> DITOLAK (PreToolUse hook error: Blocked by hook).
- `Stop-Process -Name WINWORD` -> DITOLAK (PreToolUse hook error: Blocked by hook).
- Perintah normal -> DIIZINKAN (Exit code 0).
