---
name: aturan-kelas-default-a
description: "Aturan baku penamaan kelas pada kop naskah soal SD wajib berakhiran sub-kelas A secara default (contoh VIA SD, VA SD)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 46537ccd-f052-4d92-a2a1-c74c63e93d79
  modified: 2026-11-05T02:53:23.908Z
---

Aturan baku penulisan nama kelas pada tabel kop naskah ujian jenjang SD (Methodist-11):

- **Wajib Sub-Kelas `A` secara default**:
  - Kelas 1: `IA SD`
  - Kelas 2: `IIA SD`
  - Kelas 3: `IIIA SD`
  - Kelas 4: `IVA SD`
  - Kelas 5: `VA SD`
  - Kelas 6: `VIA SD`
- **Pengecualian**: Hanya jika draf guru secara eksplisit menyebutkan sub-kelas lain (misal `Kelas 6B` -> `VIB SD`). Jika guru hanya menulis `Kelas 6` atau `VI`, wajib default ke `VIA SD`.

**Implementasi:**
Tersimpan di engine `editor_soal_claude01.py` fungsi `resolve_kop_metadata()`.
Link terkait: [[aturan-editing-soal-sd]], [[editor-soal-claude01]].
