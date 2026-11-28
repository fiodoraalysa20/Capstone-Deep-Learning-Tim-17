# Catatan model contoh-rnn (CNN-LSTM atas 10 bingkai)

**Hasil Sprint 1 (seed 1, validasi):** MAE 14,4 % duty (tanpa putaran sisa 13,6); 57.041
parameter, latensi 2,3 ms, 173 s, epoch terbaik 21. Penebak rata-rata 27,9.

## Pengaturan
CNN bersama per bingkai → LSTM 64 unit atas 10 langkah → 1 keluaran; 25 epoch.

## Bacaan
Setara CNN. Urutan bingkai tidak membantu banyak karena pada duty tinggi bingkai berurutan hampir sama (kabur); gerak
antarbingkai hanya terbaca pada duty rendah.

## Sprint 2
fps lebih tinggi supaya ada gerak yang bisa diikuti LSTM.
