# Hasil komparasi (dibangkitkan run_all.py)

| Folder | Model | seed | val_mae | val_rmse | MAE (% duty) | parameter | latensi (ms) | durasi (s) |
|---|---|---|---|---|---|---|---|---|
| contoh-ae | ae | 1 | 24.7826 | 29.8150 | 24.7826 | 48001 | 0.35 | 52 |
| contoh-cnn | cnn | 1 | 14.3637 | 20.6471 | 14.3637 | 249089 | 0.81 | 50 |
| contoh-rnn | rnn | 1 | 14.4120 | 20.9917 | 14.4120 | 57041 | 2.31 | 173 |
| contoh-tl | tl | 1 | 12.3928 | 20.2140 | 12.3928 | 1518974 | 38.48 | 316 |
| non-dl | non-dl-fitur4 | 1 | 19.2577 | 24.6947 | 19.2577 | — | — | 0 |
