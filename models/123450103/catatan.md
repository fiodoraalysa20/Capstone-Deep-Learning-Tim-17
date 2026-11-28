# Catatan model 123450103 (Transfer Learning)

## Alasan optimizer
Adam optimizer digunakan untuk kestabilan adaptasi representasi bobot fitur.

## Regularisasi
Dropout dan normalisasi input.

## Pencarian hyperparameter (tabel)
| Percobaan | LR | Epochs | Batch Size | Val MAE |
|---|---|---|---|---|
| 1 | 0.01 | 5 | 128 | 0.71 |

## Ablation (>= 2)
1. Pembekuan backbone vs unfreeze layer
2. Penambahan dense classification/regression head

## Hasil 3 seed konfigurasi akhir
- Hasil dievaluasi pada seed 1, 2, 3 melalui run_all.py.
