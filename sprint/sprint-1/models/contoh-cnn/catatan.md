# Catatan model contoh-cnn (CNN, 10 bingkai ditumpuk)

**Hasil Sprint 1 (seed 1, validasi):** MAE 14,4 % duty (tanpa putaran sisa 13,4); 249.089
parameter, latensi 0,8 ms, 50 s, epoch terbaik 24. Penebak rata-rata 27,9.

## Pengaturan
CNN kecil atas [30, 64, 64] (10 bingkai RGB sebagai kanal), 25 epoch, AdamW lr 2e-3, epoch terbaik menurut MAE validasi.

## Bacaan
Baik di duty rendah (9,5 pada duty 32), lemah di duty 255 (32,4; taksiran rata-rata 67,6).
Kurva validasi naik-turun tajam pada epoch awal (lihat `results/contoh-cnn/tambahan.json`): 648 klip latih kecil
untuk 25 epoch.

## Sprint 2
Augmentasi (geser/kecerahan); target klasifikasi taraf.
