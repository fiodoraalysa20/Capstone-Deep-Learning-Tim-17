# Protokol evaluasi tim — Tim 17: Taksiran kecepatan kipas dari video

| Butir | Isi |
|---|---|
| Kasus | Menaksir kecepatan kipas (duty PWM, %) dari urutan bingkai kamera |
| Sumber dataset | Sesi meja `sesi-20261120-095538` (20 Nov 2026 09.55–10.28, meja.py 1.14, kamera 10 fps); berkas + sha256 di `data/MANIFEST.json` |
| Rancangan | kipas 9 taraf (0, 32, …, 255) × lampu 2 taraf × 20 ulangan = 360 kondisi × 5 s, urutan acak |
| Jenis tugas (`TUGAS`) | regresi 1 nilai: duty yang diperintahkan, dalam persen (duty/255 · 100) |
| Masukan | klip 10 bingkai berurutan (1 s pada 10 fps, sesuai rencana) di **detik 2–5** tiap kondisi, tidak bertumpang tindih; tiap bingkai dipotong ke kipas lalu RGB 64 × 64, ditumpuk → `[30, 64, 64]` |
| Satuan pemisahan | **Ulangan** (tiap ulangan memuat 18 kondisi): validasi 3, 8, 14, 16, uji 1, 10, 15, 19, latih 12 sisanya (`pisah.bagi_satuan`, seed 2026). Tiga klip satu kondisi tidak pernah terbelah |
| Ukuran latih / validasi / uji | 633 / 216 / 214 klip |
| Metrik utama | MAE (% duty); MAE per taraf duty; MAE tanpa klip kipas berputar sisa |
| Pembanding | penebak rata-rata latih (MAE 27,9); baseline ridge starter **tidak dijalankan**: 122.880 fitur, matriks 122.880² tidak muat memori laptop (`BASELINE_STARTER = False`); non-DL rencana tim (energi beda-bingkai + regresi linear) |
| Praproses | normalisasi per kanal dari data latih saja |
| Anggaran komputasi | ≤ 20 menit CPU laptop per jalur per seed |
| Evaluasi data uji | Sekali, sprint terakhir |
| `data_hash` | `ac4b9ac3fc7d10f3063967af0dcc35b4` |

## Mengapa dua detik pertama dibuang

Energi beda-bingkai pada detik 0–1 mirip untuk semua duty (`reports/mutu-data.md`): kipas sedang menyesuaikan
putaran dari kondisi sebelumnya. Mulai detik 2 energi tiap duty stabil.

## Duty 0 dengan kipas masih berputar

Kondisi 5 s terlalu pendek untuk kipas berhenti. Bila kondisi sebelumnya duty ≥ 64, kipas pada kondisi duty 0 masih
berputar sampai detik ke-5 (energi beda-bingkai 40,0 vs 1,3 bila kipas diam). Label tetap duty
yang diperintahkan (rencana), tetapi 95 klip seperti itu (validasi 12, uji
18) ditandai `sisa_putar` dan MAE-nya dilaporkan terpisah. Untuk Sprint 2: kondisi lebih panjang,
atau label dari kecepatan sebenarnya.

## Mengapa ulangan

Klip berurutan dari satu kondisi hampir kembar. Pemisahan per ulangan menjaga tiap kondisi utuh di satu bagian, dan
karena tiap ulangan memuat 18 kondisi, ketiga bagian seimbang di semua taraf duty dan lampu.
