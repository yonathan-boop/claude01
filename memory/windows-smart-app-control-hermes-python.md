---
name: windows-smart-app-control-hermes-python
description: Solusi bug Hermes Desktop suruh setup berulang kali akibat Smart App Control memblokir DLL Python tool
metadata:
  node_type: memory
  type: project
  originSessionId: b993c0cf-3f55-41c9-9569-df2f0027625f
  modified: 2026-10-29T09:06:55.145Z
---

Pada Windows 11 dengan Smart App Control (SAC / WDAC) aktif (`VerifiedAndReputablePolicyState: 1`), binary/DLL Python yang belum memiliki cloud reputation (seperti build pre-release `python-3.14.9+20261021`) diblokir dengan error:
`ImportError: DLL load failed while importing _socket: An Application Control policy has blocked this file.`

**Dampak:**
- Launcher `hermes.exe` crash saat dipanggil.
- Hermes Desktop (`Hermes.exe`) gagal melakukan probe versi runtime (`hermes --version` exit code 1).
- Hermes Desktop menganggap runtime belum terpasang (`no usable Hermes install`) dan membuka layar First-Run Setup ulang.
- Setup ulang gagal di tahap `python-deps`.

**Solusi Terverifikasi:**
Gantikan direktori tool `AppData\Local\hermes\tools\python-3.14.9+20261021-win32-x64` dengan CPython 3.14 yang sudah memiliki cloud reputation Microsoft (misal `cpython-3.14.7-windows-x86_64-none` dari `AppData\Roaming\uv\python\`). Launcher `hermes.exe` dan Hermes Desktop langsung kembali normal dan mendeteksi gateway.
