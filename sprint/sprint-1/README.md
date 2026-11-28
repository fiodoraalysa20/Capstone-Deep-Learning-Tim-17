# Tim 17 — Taksiran kecepatan kipas dari video (kunci Sprint 1)

Repo tim yang sudah dikerjakan sampai akhir Sprint 1, dalam bentuk template `capstone-dl-2026-starter`
(@e8fdb7f). Angka di sini adalah satu hasil yang dapat dipertahankan pada data timmu, bukan target.

**Ringkasnya:** dari klip 1 s (10 bingkai, 10 fps), MAE validasi **TL 12,4 % duty**, CNN 14,4, RNN
14,4, non-DL 19,3, AE 24,8; penebak rata-rata 27,9. Dua batas datang dari rekamannya,
bukan dari model: pada 10 fps bilah kipas cepat **kabur merata** sehingga duty 224 dan 255 hampir tidak terbedakan,
dan **kipas belum berhenti** saat kondisi duty 0 datang sesudah duty tinggi.

## Menjalankan

1. Unduh arsip `tim17_sesi-20261120-095538` dari kartu *Data meja* dan ekstrak ke `data/sesi-20261120-095538/`
   (`imu.csv` boleh dibuang).
2. Pasang dan jalankan:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m src.protokol.mutu          # reports/mutu-data.md (arus kipas, energi beda-bingkai, putaran sisa)
python -m pytest -q
python run_all.py --seeds 1
python -m src.protokol.analisis      # reports/kesalahan.md (MAE per duty, per lampu, putaran sisa)
```

Baseline ridge starter dilewati (`BASELINE_STARTER = False`): 122.880 fitur per klip tidak muat memori laptop.

## Hasil Sprint 1 (validasi, seed 1)

Validasi = ulangan 3, 8, 14, 16 (216 klip); uji = ulangan 1, 10, 15, 19 (214 klip), belum
disentuh. Galat dalam % duty (0–100).

| Jalur | **MAE** | MAE tanpa putaran sisa | duty 0 | duty 32 | duty 128 | duty 224 | duty 255 | Parameter | Latensi (ms) |
|---|---|---|---|---|---|---|---|---|---|
| **TL (MobileNetV3-Small)** | **12,4** | 11,3 | 21,8 | 10,3 | 7,4 | 6,3 | 16,9 | 1.518.974 | 38,5 |
| CNN (10 bingkai ditumpuk) | 14,4 | 13,4 | 20,4 | 9,5 | 9,9 | 14,2 | 32,4 | 249.089 | 0,8 |
| RNN (CNN-LSTM) | 14,4 | 13,6 | 18,4 | 9,5 | 15,1 | 9,9 | 27,9 | 57.041 | 2,3 |
| Non-DL (energi beda-bingkai + 3 fitur, regresi linear) | 19,3 | 18,7 | 22,2 | 23,1 | 14,3 | 21,9 | 36,7 | 5 koefisien | — |
| AE (penyandi dibekukan) | 24,8 | 24,0 | 20,6 | 38,6 | 0,7 | 36,0 | 50,9 | 48.001 | 0,3 |
| Penebak rata-rata latih | 27,9 | 26,5 | 50,1 | 37,6 | 0,1 | 37,7 | 49,9 | — | — |

Rata-rata taksiran untuk duty 224 dan 255 (target 88 % dan 100 %): TL 84,8 dan 84,8, CNN 74,0
dan 67,6. Model terbaik pun menyamakan dua taraf tertinggi. Tabel lengkap per duty dan lampu ada di
`reports/kesalahan.md`.

Cara membaca:
- **Penebak rata-rata unggul di duty 128** karena 50 % adalah rata-ratanya; lihat MAE keseluruhan, bukan satu taraf.
- **Klip putaran sisa** (duty 0 yang kipasnya masih berputar): MAE semua model 28–39 % duty, karena kipas yang
  melambat memang tampak seperti kipas lambat. Label yang diperintahkan dan putaran sebenarnya berbeda di sini.
- **AE hampir setara penebak rata-rata**: laten yang dilatih merekonstruksi bingkai didominasi bentuk kipas yang sama
  di semua klip; perbedaan kabur bilah tidak tersimpan.
- **Non-DL rencana tim** (energi saja) MAE 25,3; dengan tiga fitur tambahan (log energi, simpangan
  temporal, tekstur) 19,3, dan inilah yang terpilih. Energi beda-bingkai **turun** saat duty naik, jadi
  koefisiennya negatif.

## Keputusan utama (dan alternatif yang ditolak)

| Keputusan | Pilihan | Alternatif yang ditolak, dan alasannya |
|---|---|---|
| Target | duty yang diperintahkan, % | putaran sebenarnya: tidak terukur (tak ada sensor RPM); arus kipas tersedia tetapi bukan masukan kamera |
| Jendela | detik 2–5 tiap kondisi, 3 klip 1 s | seluruh 5 s: detik 0–1 kipas sedang berubah putaran, semua duty mirip |
| Duty 0 berputar sisa | label tetap 0, klip ditandai dan dilaporkan terpisah | dibuang: menyembunyikan masalah rancangan; dilabel ulang: tidak ada ukuran putaran |
| Satuan pemisahan | ulangan (4 val, 4 uji) | acak per klip: tiga klip satu kondisi hampir kembar |
| Pembanding nol | penebak rata-rata | ridge starter: 122.880 fitur, tidak muat memori |

## Temuan pada data tim ini

1. **Kipas mengikuti perintah**: arus INA219 naik sebanding duty (duty 32 = 23,7 mA, duty 255 = 246,8 mA).
2. **Kabur gerak membatasi taraf tinggi**: energi beda-bingkai duty 32 = 16,3, duty 128 = 5,9, duty 255 = 6,0
   (×1000). Pada 10 fps putaran cepat tampak sebagai cakram kabur yang sama.
3. **Kipas tidak sempat berhenti dalam 5 s**: 95 klip duty 0 berputar sisa (energi sampai
   40,0 vs 1,3 saat diam).
4. **Wi-Fi ESP32 putus 3×**, tersambung ulang dalam ±5 s; tidak ada kondisi yang hilang.

## Apa artinya untuk Sprint 2

- **Kondisi lebih panjang** atau jeda berhenti sebelum duty 0 (ukur waktu berhenti kipas di gladi).
- **fps lebih tinggi atau pajanan kamera lebih pendek** supaya bilah duty tinggi tidak kabur; atau pita/tanda pada
  satu bilah sebagai penanda putaran.
- Klasifikasi taraf (9 kelas) di samping regresi, 3 seed, pilih model dari MAE tanpa putaran sisa; uji sekali.

## Peta backlog Sprint 1 → bukti

| Tugas backlog | Bukti di repo ini |
|---|---|
| Rencana final disetujui dan diserahkan | `rencana.yaml` |
| Peran slot meja | `catatan/peran-slot.md` |
| Sprint Goal, Log Sprint, Demo | `sprint-goal.md`, `log-sprint-contoh.md`, `DEMO.md` |
| Pemotong klip dan PROTOKOL.md | `src/protokol/data.py`, `src/protokol/PROTOKOL.md`, `tests/test_t17.py` |
| Terima data, MANIFEST.json, pemeriksaan mutu | `data/MANIFEST.json`, `src/protokol/mutu.py` → `reports/mutu-data.md` |
| Repo tim siap, run_all pada simulasi | `models/contoh-*/`, `models/non-dl/`, `run_all.py`, `catatan/gladi.md` |
| Merge komponen, run_all pada data primer | `reports/hasil_komparasi.md` |
| Pembanding non-DL | `models/non-dl/` (energi beda-bingkai + regresi linear) |
| Rekaman Demo Sprint 1 | `DEMO.md` |
| [Jalur] Kerangka run.py dan latih seed 1 | `models/contoh-{cnn,tl,rnn,ae}/`, `results/*/metrics.json` |

## Yang berubah dari starter

- `run_all.py`: starter memanggil `src.common.baseline_mlp` yang tidak ada; diganti `src.common.baseline`, dan
  baseline dilewati bila `BASELINE_STARTER = False`.
- Folder model `contoh-<jalur>` pengganti NIM. `src/common/` tidak diubah.
