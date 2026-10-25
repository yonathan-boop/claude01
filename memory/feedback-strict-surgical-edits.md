---
name: feedback-strict-surgical-edits
description: "User menegur keras: dilarang sembarangan edit, tambah fitur liar, atau merombak hal di luar instruksi spesifik"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 715e0d9f-023d-45b7-8bfc-fe25f39b4aa6
  modified: 2026-10-24T11:35:51.555Z
---

User trauma dan sangat terganggu jika AI mengedit sembarangan, menambah elemen/fitur yang tidak diminta (seperti tombol ekstra liar), atau merombak kode di luar sasaran yang diminta secara spesifik.

**Why:**
Perubahan di luar instruksi merusak tata letak yang sudah nyaman bagi user, membuat user bingung/jantungan, dan menimbulkan efek samping yang tidak diinginkan (contoh: tombol baru mendorong tombol penting keluar layar).

**How to apply:**
1. Bedah bedah (surgical edits): hanya sentuh dan ubah baris yang persis diminta oleh user.
2. Jangan pernah berinisiatif menambah tombol, widget, atau fitur baru tanpa izin/permintaan eksplisit user.
3. Sebelum mengedit berkas yang sudah stabil, pastikan perubahan seminimal mungkin (shortest working diff) dan tidak menggeser/mengorbankan elemen yang sudah ada.
