# AI_LOG — Tim 17 (contoh kunci)

| Tanggal | Siapa | Alat | Untuk apa | Apa yang diperiksa/diubah dari keluarannya |
|---|---|---|---|---|
| 2026-11-20 | penyusun kunci | Claude | memeriksa sesi (kelengkapan, arus kipas per duty, energi beda-bingkai per detik dan per duty sebelumnya) | kisi bingkai duty 0/128/255 dilihat langsung: duty 0 pertama tampak kabur (kipas masih berputar) → dasar penanda `sisa_putar` |
| 2026-11-20 | penyusun kunci | Claude | kode protokol (klip 10 bingkai, ulangan sebagai satuan, metrik per taraf) dan naskah kunci ini | diperiksa dengan tes (persen duty, metrik per taraf, ulangan terpisah dan seimbang, target acak); tes keseimbangan pertama salah (menghitung klip, bukan kondisi; sebagian kondisi hanya 2 klip) dan diperbaiki; klaim "lampu hampir tidak berpengaruh" diganti tabel karena data menunjukkan geseran pada duty rendah |
