---
name: aturan-penamaan-file-edit-vs-ok
description: Larangan mutlak menambahkan label OK pada nama berkas ujian; unit editing hanya berhak menambahkan kata edit
metadata:
  node_type: memory
  type: feedback
  originSessionId: 46537ccd-f052-4d92-a2a1-c74c63e93d79
  modified: 2026-11-05T01:08:57.637Z
---

AI dilarang keras menambahkan label `OK` pada nama berkas hasil editing naskah ujian.

Label `OK` memiliki arti yuridis/institusional bahwa naskah soal sudah diperiksa dan disetujui oleh tim pemeriksa/penelaah (bagian pemeriksaan), bukan oleh bagian editing. AI bertindak sebagai unit editing tata letak/layout, sehingga otoritas penamaan AI HANYA menambahkan kata `edit`.

**Aturan Penamaan Berkas:**
1. Jika nama berkas asal **TIDAK ada** kata `OK` (contoh: `Bahasa Inggris 6 Winna.docx`):
   - Wajib dinamai: `Bahasa Inggris 6 Winna edit.docx`.
   - Dilarang menambahkan kata `OK`.
2. Jika nama berkas asal dari guru **SUDAH ada** kata `OK` sejak awal (contoh: `Agama 1 Rio OK.docx`):
   - Boleh mempertahankan kata `OK` bawaan tersebut lalu menambahkan `edit`: `Agama 1 Rio OK edit.docx`.

**Why:**
Menambahkan kata `OK` secara sepihak adalah pelanggaran fatal wewenang operasional karena memalsukan status naskah yang belum disidang/diperiksa oleh tim penelaah ujian sekolah.

**How to apply:**
Dalam setiap script pembuatan dokumen, pipeline penamaan naskah ujian, atau eksekusi command:
Gunakan formula: `f"{nama_asal_tanpa_ekstensi} edit.docx"`. Jangan pernah menyisipkan substring `OK` jika berkas input tidak memilikinya.
Link terkait: [[aturan-editing-soal-sd]], [[feedback-strict-surgical-edits]].
