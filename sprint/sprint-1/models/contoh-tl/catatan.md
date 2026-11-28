# Catatan model contoh-tl (MobileNetV3-Small, transfer learning)

**Hasil Sprint 1 (seed 1, validasi):** MAE 12,4 % duty (tanpa putaran sisa 11,3); 1.518.974 parameter,
latensi 38,5 ms, 316 s, epoch terbaik 7. Penebak rata-rata 27,9.

## Pengaturan
Klip [30, 64, 64] → adaptor 1 × 1 yang dipelajari (30 → 3 kanal) → MobileNetV3-Small pralatih ImageNet (128 px),
lapisan akhir 1 keluaran (duty terstandar); 10 epoch, AdamW lr 5e-4.

## Bacaan
Terbaik, dan satu-satunya yang mendekati duty 224 (6,3). Duty 224 dan 255 tetap disamakan (taksiran rata-rata
84,8 dan 84,8). Adaptor 1 × 1 mencampur 10 bingkai menjadi 3 kanal, jadi model lebih banyak membaca
"seberapa kabur" daripada gerak antarbingkai. Latensi paling besar di antara jalur.

## Sprint 2
Bingkai lebih tajam (fps/pajanan); bandingkan dengan TL satu bingkai untuk tahu sumbangan urutan.
