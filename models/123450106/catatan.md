# Catatan model 123450106 (RNN)

## Alasan optimizer
Adam dipilih untuk menangani gradien pada permodelan sequence dan dependensi temporal sensor.

## Regularisasi
Dropout dan gradient clipping untuk mencegah exploding/vanishing gradient.

## Pencarian hyperparameter (tabel)
| Percobaan | Hidden Dim | LR | Epochs | Val MAE |
|---|---|---|---|---|
| 1 | 16 | 0.01 | 5 | 0.71 |

## Ablation (>= 2)
1. Perbandingan model feed-forward vs recurrent unit
2. Pengaruh aktivasi non-linear pada dense head

## Hasil 3 seed konfigurasi akhir
- Hasil dievaluasi pada seed 1, 2, 3 melalui run_all.py.
