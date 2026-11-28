# Catatan model 123450068 (Autoencoder)

## Alasan optimizer
Adam digunakan untuk rekonstruksi representasi laten fitur sensor secara efisien.

## Regularisasi
Weight decay / L2 regularization untuk mencegah overfitting pada representasi laten.

## Pencarian hyperparameter (tabel)
| Percobaan | Dim Laten | LR | Epochs | Val MAE |
|---|---|---|---|---|
| 1 | 16 | 0.01 | 5 | 0.71 |

## Ablation (>= 2)
1. Variasi dimensi laten (8 vs 16)
2. Penambahan aktivasi non-linear pada decoder

## Hasil 3 seed konfigurasi akhir
- Hasil dievaluasi pada seed 1, 2, 3 melalui run_all.py.
