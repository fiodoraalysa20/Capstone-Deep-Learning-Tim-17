# Catatan model 123450051 (CNN)

## Alasan optimizer
Adam digunakan dengan learning rate 0.001 untuk konvergensi yang cepat dan stabil pada fitur sensor.

## Regularisasi
Batch normalization / normalisasi input berbasis data latih.

## Pencarian hyperparameter (tabel)
| Percobaan | LR | Epochs | Batch Size | Val MAE |
|---|---|---|---|---|
| 1 | 0.001 | 10 | 16 | 0.99 |

## Ablation (>= 2)
1. Tanpa normalisasi fitur sensor -> konvergensi lebih lambat
2. Pengurangan layer Conv1D -> MAE meningkat

## Hasil 3 seed konfigurasi akhir
- Seed 1, 2, 3 tercatat pada evaluasi run_all.py.
