---
name: google-flow-prompting-standards
description: Standar prompting mendalam & cerewet di Google Flow untuk mencegah diskontinuitas adegan dan transisi patah
metadata:
  node_type: memory
  type: feedback
  originSessionId: e6b4e0c0-aad9-4bca-8f00-f04bca4d17c5
  modified: 2026-11-03T23:21:26.036Z
---

User mengoreksi video skor 55/100: transisi patah (dari botol kaca tiba-tiba lambung) dan deskripsi terlalu singkat.

**Prinsip Prompting Cerewet & Kontinuitas Google Flow:**
1. **Dilarang Jump Cut Konseptual**: Transisi antar-scene wajib memiliki jembatan fisik / spasial yang logis (contoh: kamera zoom-in tembus ke dalam tubuh manusia atau gelas beker diletakkan di samping model anatomi sebelum beralih).
2. **Deskripsi Ultra-Detail (Cerewet)**:
   - **Tekstur & Material**: kekasaran permukaan, viskositas cairan (tebal, berminyak, bening keemasan), refleksi kaca beker, kebasahan selaput mukosa.
   - **Posisi & Framing**: koordinat spasial subjek (kiri/kanan/tengah), arah pandang, orientasi pencahayaan (rim light, key light hangat 3200K).
   - **Pergerakan Kamera**: continuous pan, macro zoom-in 100mm, orbit smooth 45 derajat.
3. **Prompt Chaining**:
   - Scene N+1 wajib mengutip status akhir Scene N ("continuing from previous frame...").
