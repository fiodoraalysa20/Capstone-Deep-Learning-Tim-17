# Catatan Sesi Akuisisi Data - Tim 17

- **Judul Sesi**: Program harian meja (rekaman dasar)
- **Metadata Perekam**: `versi_perekam: 1.8` | `tim: 0` | `host: sditera-civ` | `dibuat: 2026-11-13T22:39:04.446`
- **Data Hash (`data/MANIFEST.json`)**: `944ea9407b6856044eb5b87e085d8831c7f1ae465a5b1ba4d7eb4b4f7f632431`

## 1. Sesi yang Dipakai & Kelengkapan Berkas
- **Sesi dipakai**: Paket rekaman dasar (`tim: 0`, `seed: 2026`) yang diserahkan pengelola dalam format ZIP.
- **Berkas masuk ke `data/`**: `aktuator.csv`, `daya.csv`, `digital.csv`, `imu.csv`, `lingkungan.csv`, `log.txt`, `rencana.yaml`, dan `manifest.json` (disimpan sebagai `data/manifest_sesi.json`). Seluruh SHA-256 individual terverifikasi cocok dengan `manifest_sesi.json`.
- **Berkas tidak tersedia pada sesi ini**: `label.csv`, `kamera_index.csv`, serta data audio dan citra tidak dihasilkan karena pada `rencana.yaml` tercatat `rekam.audio.aktif: false` dan `rekam.kamera.aktif: false`.

## 2. Pemeriksaan Jumlah Kondisi
- **Rencana khusus Tim 17**: 360 kondisi (18 kombinasi × 20 ulangan).
- **Aktual diterima**: 0 kondisi eksperimen kombinasi (`faktor: {}` pada `rencana.yaml`, berkas `label.csv` belum tersedia karena sesi merupakan rekaman harian dasar `tim: 0` dengan aturan tetap: `lampu_jam: [8, 16]`, `kipas_ambang_suhu: 29.0`, `pompa_setiap_menit: 120`, `buzzer_jam: [12]`).
- **Selisih**: -360 kondisi terhadap target eksperimen otomatis Tim 17 (akan diperbarui setelah sesi slot khusus Tim 17 / berkas `label.csv` diserahkan pengelola).

## 3. Pemeriksaan Selang Antar-Frame (`kamera_index.csv`)
- **Target**: Mendekati 0,1 detik per frame.
- **Aktual**: Tidak dapat diperiksa karena `rekam.kamera.aktif: false` pada `rencana.yaml` sehingga berkas `kamera_index.csv` dan citra tidak direkam pada paket ini.

## 4. Kondisi yang Dikeluarkan & Alasannya
- **Kondisi dikeluarkan**: Tidak ada baris kondisi eksperimen yang dikeluarkan secara selektif; seluruh rekaman sensor dasar (`aktuator.csv`, `daya.csv`, `digital.csv`, `imu.csv`, `lingkungan.csv`) dipertahankan utuh sebagai data *baseline* awal sambil menunggu data sesi khusus Tim 17 (`label.csv` dan `kamera_index.csv`).