# Protokol evaluasi tim — Tim 17 (Taksiran Kecepatan Kipas dari Video)

Diisi Penjaga Data & Evaluasi pada Sprint 0, digabung ke `main` lewat *pull request* yang
disetujui pembimbing, lalu **dibekukan**. Perubahan setelah itu hanya lewat *pull request*
baru yang disetujui pembimbing.

| Butir | Isi |
|---|---|
| Kasus (dari kartu Kasus tim) | Taksiran kecepatan kipas (`% duty`) dari video urutan 10 frame (10 fps) |
| Sumber dataset | Sesi meja eksperimen & simulasi (`data/`, spesifikasi `t17-kecepatan-kipas-video.yaml`) |
| Jenis tugas (`TUGAS`) | `regresi` |
| Target / label | Persentase *duty cycle* kipas (`0.0%` – `100.0%`, dari nilai PWM `0` – `255` pada `aktuator.csv`) |
| Ukuran data latih / validasi / uji | Dibagi per satuan ulangan kondisi (`70%` latih / `15%` validasi / `15%` uji) |
| Cara split | Pemisahan berbasis kelompok ulangan (*group split* deterministik `SEED_SPLIT = 2026`); tidak ada ulangan yang muncul di latih dan uji sekaligus |
| Metrik utama untuk komparasi | `MAE (% duty)` (didampingi `RMSE` dan `R2`) |
| Praproses yang sama untuk semua model | 1) Citra `kamera/` `640×480` (10 fps) dipotong (*crop*) pada Region of Interest (ROI) daerah kipas dan diubah ke skala keabuan `64×64`; 2) Buang `1 detik pertama` (`10 frame` awal) setiap kondisi untuk menghilangkan transien inersia; 3) Susun urutan `10 frame` (1 detik) menjadi satu sampel masukan `(10, 64, 64)`; 4) Normalisasi Z-score `(x - mean) / std` dihitung **hanya dari data latih** |
| Anggaran komputasi per run | ≤ 20 menit CPU laptop |
| Evaluasi data uji | Sekali, oleh Penjaga Data, pada sprint terakhir (`--pred-test`) |
| `data_hash` saat dibekukan | `eb790c5fb3d49a3537b2b9220ba8dbc8` |

Disetujui pembimbing pada: *(tautan pull request ke `main`)*
