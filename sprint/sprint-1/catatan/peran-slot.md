# Peran slot meja (contoh)

Sesi tim 17 berjalan tanpa operator: 360 kondisi × 5,5 s (±33 menit), urutan acak dari `rencana.yaml`. Nama anggota
tidak ditulis di repo.

| Peran | Tugas | Selesai bila |
|---|---|---|
| Penanggung jawab kamera | Memastikan kipas mengisi bingkai dan selang kamera 0,1 s (`rekam.kamera.interval_detik`) | `kamera_index.csv` bingkai per kondisi ±50 |
| Pengamat | Mengecek kartu *Eksperimen berjalan* di awal dan akhir (n / 360) | Kondisi 360/360 selesai |
| Penjaga data | Mengunduh arsip, menjalankan `python -m src.protokol.mutu` | `reports/mutu-data.md` di-commit |

## Pelajaran dari sesi ini

Media rekaman pertama tim terhapus, jadi sesi diulang 20 Nov. Pada rekaman ulang, kipas belum berhenti ketika
kondisi duty 0 datang sesudah duty tinggi: 5 s per kondisi cukup untuk kipas mencapai putaran baru, tetapi tidak cukup
untuk berhenti. Sebelum slot berikutnya, ukur waktu berhenti kipas (gladi) dan pilih durasi kondisi yang cukup.
