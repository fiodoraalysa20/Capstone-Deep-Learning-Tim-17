# Mutu data tim 17 (sesi-20261120-095538)

Dibangkitkan `python -m src.protokol.mutu`.

## Kelengkapan

- 360 kondisi (9 duty × 2 lampu × 20 ulangan, urutan acak), sesi selesai normal: ya; Wi-Fi ESP32 putus 3× (disambung ulang dalam ±5 s).
- 19810 bingkai; selang median 0,100 s, maksimum 0,14 s; bingkai per kondisi 48–51 (median 50).
- Klip 10 bingkai (detik 2–5): 1063; latih / validasi / uji = 633 / 216 / 214 (ulangan validasi [3, 8, 14, 16], uji [1, 10, 15, 19]).

## Kipas mengikuti perintah (arus INA219 kanal kipas, detik 1–5)

| Duty | 0 | 32 | 64 | 96 | 128 | 160 | 192 | 224 | 255 |
|---|---|---|---|---|---|---|---|---|---|
| arus (mA) | -0,1 | 23,7 | 52,6 | 83,4 | 118,8 | 153,3 | 182,4 | 212,6 | 246,8 |

## Energi beda-bingkai (×1000) per duty dan detik dalam kondisi

| Duty | detik 0–1 | 1–2 | 2–3 | 3–5 |
|---|---|---|---|---|
| 0 | 20,9 | 20,0 | 24,7 | 25,0 |
| 32 | 12,9 | 11,4 | 13,2 | 16,3 |
| 64 | 13,3 | 10,0 | 8,5 | 10,1 |
| 96 | 16,4 | 9,9 | 8,9 | 10,8 |
| 128 | 13,1 | 8,4 | 7,5 | 5,9 |
| 160 | 12,7 | 6,5 | 5,9 | 5,3 |
| 192 | 15,2 | 7,1 | 5,4 | 4,9 |
| 224 | 11,7 | 6,3 | 4,8 | 4,3 |
| 255 | 14,9 | 6,3 | 5,6 | 6,0 |

## Duty 0: energi detik 2–5 menurut duty kondisi sebelumnya

| Duty sebelumnya | 0 | 32 | 64 | 96 | 128 | 160 | 192 | 224 | 255 |
|---|---|---|---|---|---|---|---|---|---|
| energi (×1000) | 1,3 | 1,3 | 8,7 | 33,8 | 37,2 | 40,0 | 24,4 | 33,0 | 38,4 |

## Temuan

- **Kipas menurut perintah**: arus naik hampir sebanding duty (0 → 246,8 mA). Label duty sah.
- **Beda-bingkai turun saat duty naik** (detik 2–5: duty 32 = 16,3, duty 255 = 6,0). Pada 10 fps bilah yang berputar cepat kabur merata sehingga bingkai berurutan mirip; bilah lambat bergeser nyata antarbingkai. Energi beda-bingkai tidak naik bersama kecepatan.
- **Taraf tinggi sulit dibedakan**: duty 160–255 energinya 4,3–6,0, hampir sama.
- **Detik 0–1 mirip untuk semua duty** (11,7–20,9): kipas sedang berubah putaran. Dua detik pertama dibuang.
- **Duty 0 sesudah duty ≥ 64: kipas masih berputar sisa** (energi detik 2–5 sampai 40,0 vs 1,3 bila sebelumnya juga 0). Kondisi 5 s terlalu pendek untuk kipas berhenti. 95 klip (val 12, uji 18) berlabel 0 % padahal kipas berputar; dilaporkan terpisah (`val_mae_tanpa_sisa`).
- **Duty 0 hampir selalu berarti 'sedang melambat'**: 95 dari 119 klip duty 0. Hanya kondisi yang didahului duty 0 atau 32 menampilkan kipas diam.
- **Lampu** (ruang sudah terang, sesi pukul 09.55–10.28) menggeser energi terutama pada duty rendah, tidak searah di semua taraf; dijaga seimbang di tiap bagian karena tiap ulangan memuat kedua taraf lampu:

| Lampu | 0 | 32 | 64 | 96 | 128 | 160 | 192 | 224 | 255 |
|---|---|---|---|---|---|---|---|---|---|
| mati | 25,6 | 18,2 | 11,1 | 9,1 | 6,4 | 5,2 | 6,2 | 4,5 | 5,7 |
| nyala | 24,1 | 12,4 | 8,0 | 11,2 | 6,4 | 5,9 | 3,9 | 4,5 | 6,0 |
