---
name: agent-model-policy
description: Semua agen baru di-hire atau ditugaskan wajib menggunakan model campur dan effort high via 9router lokal
metadata:
  node_type: memory
  type: feedback
  originSessionId: 9a9dd048-8eb1-4220-816e-2c0e06b3fbad
  modified: 2026-10-23T14:41:24.876Z
---

Setiap agen baru yang di-hire, di-scale, atau ditugaskan di seluruh lantai WAJIB menggunakan model `campur` dengan effort `high` saja. Jangan pernah gunakan atau usulkan model atau effort lain.

**Why:** Sistem berjalan sepenuhnya lewat 9router lokal yang melayani model `campur` dengan 8 akun berbeda (disarankan mode round-robin oleh manajer). Model cloud lain tidak didukung/tidak diizinkan oleh manajer.

**How to apply:** Saat memanggil `scale_team` atau `configure_agent`, selalu tentukan `model: "campur"` dan `effort: "high"`.
