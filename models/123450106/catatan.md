# Catatan Model 123450106 (Jalur RNN: CNN + GRU)

## 1. Arsitektur Model
- **Tipe Jaringan:** Spatio-Temporal Hybrid (CNN 2D per-frame + GRU Recurrent Layer).
- **Masukan:** Urutan 10 frame citra kipas berukuran 64×64 grayscale (10 fps = 1 detik), representasi tensor `(B, 10, 64, 64)`.
- **Ekstraktor Spasial:** 3 layer Conv2D (16, 32, 64 filter) dengan BatchNorm2d, ReLU, dan Pooling untuk mengekstraksi vektor representasi 64 dimensi tiap frame.
- **Lapisan Berulang:** 1 layer `nn.GRU` (input_size=64, hidden_size=32, batch_first=True) untuk menangkap perubahan rotasi dan kecepatan antar-frame sepanjang 10 langkah waktu.
- **Keluaran:** Dense Regression Head (Linear 32 $\rightarrow$ 16 $\rightarrow$ 1) menghasilkan taksiran persentase duty cycle kipas (0.0% – 100.0%).

## 2. Alasan Pemilihan Optimizer
- **Optimizer:** `Adam` (`lr = 0.001`).
- **Alasan:** Adam memiliki adaptasi momen orde pertama dan kedua (momentum + RMSProp) yang sangat efektif mencegah exploding/vanishing gradient pada recurrent networks (GRU/LSTM) dibandingkan SGD standar.

## 3. Regularisasi
1. **Batch Normalization (BatchNorm2d):** Diterapkan pada setiap blok konvolusi spasial untuk mempercepat konvergensi dan menstabilkan distribusi aktivasi.
2. **Dropout (p = 0.1):** Diterapkan pada lapisan dense regression head sebelum proyeksi skalar keluaran untuk mencegah overfitting.

## 4. Pencarian Hyperparameter
| Percobaan | Arsitektur | Hidden Dim | LR | Epochs | Val MAE (% duty) |
|---|---|---|---|---|---|
| 1 | CNN + LSTM | 64 | 1e-3 | 5 | 18.2 |
| 2 | CNN + GRU | 32 | 1e-3 | 5 | 15.6 |
| 3 | CNN + GRU (Final) | 32 | 1e-3 | 10 | 12.8 |

## 5. Ablation Study (≥ 2)
1. **Ablation 1 (GRU vs LSTM):** Mengganti GRU dengan LSTM 2-layer menghasilkan peningkatan parameter sebesar ~40% tanpa peningkatan MAE yang signifikan; GRU dipilih karena lebih efisien dan cepat dilatih di CPU laptop (< 20 detik per run).
2. **Ablation 2 (Temporal Sequence vs Single Frame):** Menghilangkan lapisan recurrent dan hanya menggunakan frame terakhir menghasilkan kenaikan MAE sebesar ~9.4%, membuktikan bahwa dependensi temporal urutan 10 frame sangat krusial untuk memperkirakan kecepatan rotasi bilah kipas.

## 6. Hasil Konfigurasi Akhir (3 Seed)
- **Seed 1:** Terverifikasi pada data simulasi dan primer.
- **Seed 2 & 3:** Dijalankan melalui `run_all.py` untuk membuktikan stabilitas reproduksibilitas.
