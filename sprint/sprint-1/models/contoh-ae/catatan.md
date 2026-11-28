# Catatan model contoh-ae (autoencoder, penyandi dibekukan)

**Hasil Sprint 1 (seed 1, validasi):** MAE 24,8 % duty (tanpa putaran sisa 24,0); 48.001 parameter,
52 s, epoch terbaik kepala 6. Penebak rata-rata 27,9.

## Pengaturan
Autoencoder konvolusi merekonstruksi klip [30, 64, 64] (25 epoch), encoder dibekukan, kepala kecil dari laten 32
menaksir duty (30 epoch).

## Bacaan
Hampir setara penebak rata-rata: taksirannya ±50 % untuk duty 96–255. Rekonstruksi didominasi bentuk kipas dan
dinding yang sama di semua klip; tingkat kabur bilah tidak tersimpan di laten. MAE validasi kepala datar sejak epoch 6.

## Sprint 2
Latih AE pada selisih bingkai (bukan bingkai mentah), atau setel ulang encoder bersama kepala.
