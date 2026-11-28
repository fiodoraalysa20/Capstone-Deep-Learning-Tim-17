# Catatan pembanding non-deep learning (energi beda-bingkai + regresi linear)

**Hasil Sprint 1 (seed 1, validasi):** terpilih `fitur4`, MAE 19,3 % duty (tanpa putaran sisa
18,7); energi saja 25,3. Penebak rata-rata 27,9.

## Calon
Sesuai rencana tim: rata-rata |bingkai t − bingkai t−1| (abu-abu) per klip, lalu regresi linear. Calon kedua menambah
log energi, simpangan temporal per piksel, dan simpangan spasial (tekstur). Dipilih dengan MAE validasi; koefisien
keduanya di `tambahan.json`.

## Bacaan
Energi beda-bingkai **turun** saat duty naik (bilah cepat kabur merata), dan tidak linear: duty 160–255 energinya
hampir sama. Satu garis lurus tidak menangkap itu; tekstur (seberapa kabur) membantu.

## Sprint 2
Regresi tak linear (mis. isotonik atau pohon) atas fitur yang sama.
