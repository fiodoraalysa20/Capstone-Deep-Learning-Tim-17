# Rencana Eksperimen Tim 17: Taksiran Kecepatan Kipas dari Video

| Butir | Keterangan |
|---|---|
| Pilar | Citra |
| Pembimbing | Ade Lailani |
| Jumlah anggota | 4 orang (satu jalur per anggota) |
| Jenis tugas | Regresi (duty PWM kipas, 0–255) |
| Masukan model | Urutan 10 frame (10 fps) |
| Metrik utama | MAE (% duty) |
| Pembanding non-DL | Energi beda-frame + regresi linear |
| Purwarupa | Sprint 2: taksiran putaran dari kamera |
| Berkas rencana | `rencana/t17-kecepatan-kipas-video.yaml` |

> Dokumen ini dibaca bersama *Metode Eksperimen Lapangan di Meja Uji Ruang Cerdas 5 V* (bagian 2–3 untuk membaca rencana).

---

## 1. Persoalan yang Diteliti

Kecepatan kipas biasanya diukur dengan tachometer optik. Kamera ruangan dapat menjadi penggantinya bila mampu menaksir kecepatan dari urutan citra. Tantangannya: laju kamera 10 fps jauh lebih lambat daripada putaran kipas, sehingga terjadi **aliasing**. Tugas tim adalah menaksir **duty PWM kipas** dari urutan 10 frame (regresi).

Rencana ini **sepenuhnya otomatis** (tanpa faktor manual dan tanpa partisipan manusia) dan dijalankan penuh pada slot malam.

---

## 2. Rencana Eksperimen dalam Bahasa Sehari-hari

### 2.1 Faktor

| Faktor | Jenis | Taraf | Arti di meja |
|---|---|---|---|
| `kipas` | Otomatis | 0, 32, 64, 96, 128, 160, 192, 224, 255 | 9 taraf kecepatan, langkah 32 (255 sebagai batas penuh) |
| `lampu` | Otomatis | 128, 255 | Kecerahan lampu meja |

- **Faktor manual:** tidak ada → seluruh sesi hanya **satu blok**.
- **Faktor isyarat:** tidak ada.

### 2.2 Perhitungan jumlah kondisi

```
kombinasi faktor otomatis = 9 (kipas) × 2 (lampu) = 18
ulangan                   = 20
total kondisi             = 18 × 20 = 360
```

18 kombinasi diulang 20 kali, lalu **diacak** dengan `seed: 1017` (urutan sama persis bila diulang). Pengacakan mencegah model mempelajari waktu/suhu yang naik pelan-pelan alih-alih kondisi sebenarnya.

### 2.3 Durasi

| Parameter | Nilai |
|---|---|
| Durasi tiap kondisi | 5 detik |
| Jeda antar-kondisi | 0,5 detik (alat kembali mati) |
| Perekam aktif | Kamera 640×480, selang 0,1 detik (10 fps) |
| Audio | Nonaktif |
| Sensor ESP32 | Selalu merekam (getaran, arus, suhu, kelembapan, lux, PIR, pintu) |

```
waktu rekam = 360 × (5 + 0,5) = 1.980 detik ≈ 33 menit
```

---

## 3. Label dan Data untuk Model

- **Asal label:** perintah skrip (kolom `kipas` di `label.csv`), bukan tebakan manusia, sehingga dapat ditelusuri ulang.
- **Data masukan:** citra `kamera/` 640×480 tiap 0,1 detik, **dipotong pada daerah kipas**. Urutan 10 frame (1 detik) = 1 masukan.
- **Pembuangan awal:** 1 detik pertama setiap kondisi dibuang (alat masih dalam peralihan), sisa efektif 4 detik per kondisi.
- **Satuan pemisahan data uji:** per **ulangan**. Seluruh jendela dari satu ulangan harus berada pada lipatan yang sama, tidak pernah terbagi antara latih dan uji.

---

## 4. Pembagian Anggota dan Peran

### 4.1 Jalur model (satu per anggota)

| Anggota | Jalur model |
|---|---|
| Anggota 1: _(nama)_ | CNN |
| Anggota 2: _(nama)_ | TL (Transfer Learning) |
| Anggota 3: _(nama)_ | RNN |
| Anggota 4: _(nama)_ | AE (Autoencoder) |

Pembanding non-deep learning (**energi beda-frame + regresi linear**) dikerjakan bersama atau ditugaskan ke satu anggota (_tentukan: ______).

### 4.2 Peran saat slot (tim 4 orang: pencatat dan penjaga bingkai dirangkap)

| Peran | Pemegang | Tugas |
|---|---|---|
| Operator perekam | _(nama)_ | Menjalankan `meja.py`, menekan Enter bila diminta, menghentikan dengan Ctrl+C bila ada masalah |
| Operator alat | _(nama)_ | Mencocokkan posisi benda dengan foto acuan, memastikan tiang kamera tidak bergeser, membersihkan bingkai dari benda di luar rencana |
| Koordinator | _(nama)_ | Komunikasi dengan pengelola meja dan pembimbing (keadaan lampu ruang, penyerahan berkas, jadwal). Tidak ada partisipan manusia pada rencana ini |
| Pencatat kejadian + penjaga bingkai | _(nama)_ | Mengisi lembar sesi (nomor kondisi terganggu, waktu, keterangan) dan mengawasi pratinjau kamera (orang lewat, bayangan, perubahan cahaya) |

> Peran dapat dirotasi, tetapi setiap anggota harus bisa menjelaskan faktor, taraf, dan asal label.

---

## 5. Pemeriksaan: Rencana Muat di Slot

| Slot | Waktu | Kegunaan |
|---|---|---|
| Operator | Kamis, 5 Nov 2026, 14.00–15.00 | Memeriksa rencana, cek citra kipas bersama pembimbing, merekam sesi percobaan (~10 menit) |
| Otomatis | Jumat, 6 Nov 2026, 20.00 – 7 Nov 00.00 | Sesi penuh 360 kondisi dijalankan pengelola dengan `--tanpa-operator` |
| Cadangan | Kamis, 12 Nov 2026 | Bila sesi gagal |
| Uji purwarupa | Selasa, 17 Nov 2026, 10.30–11.00 | Uji 30 menit di laptop meja |

- Slot operator efektif: 60 − ±10 (persiapan/penutupan) = **±50 menit**.
- Sesi percobaan ±10 menit → **muat**.
- Sesi penuh ±33 menit → **muat** di slot otomatis (jendela 4 jam).
- Tidak ada waktu ketik isian (`catat_setiap_kondisi` tidak dipakai) dan tidak ada waktu ganti blok.

**Kesimpulan: rencana muat di slot, tidak perlu mengurangi ulangan atau durasi.**

---

## 6. Langkah Sebelum Slot (3–1 hari sebelumnya)

- [ ] Semua anggota membaca keterangan kasus dan rencana YAML; dapat menjelaskan faktor, taraf, dan asal label.
- [ ] Jalankan mode simulasi:
  ```bash
  python meja.py --simulasi jalankan ../rencana/t17-kecepatan-kipas-video.yaml
  ```
- [ ] Pastikan skrip mencetak **360 kondisi** dan perkiraan durasi **±33 menit**.
- [ ] Uji **pemotong jendela** pada folder `data/tim17/sesi-…/` hasil simulasi (potong dari `label.csv` dan berkas sensor, buang 1 detik pertama).
- [ ] Cocokkan bingkai kamera dengan foto acuan meja; **tiang kamera tidak digeser** sedikit pun selama sesi.
- [ ] Singkirkan benda di luar rencana dari bingkai (tas, botol minum tim, dll.).
- [ ] Sepakati dengan pengelola **keadaan lampu ruang** selama slot otomatis (mati/menyala) dan catat di lembar sesi.
- [ ] Siapkan lembar sesi, alat tulis, dan flash disk tim.

---

## 7. Langkah Saat Slot

### Slot operator (Kamis, 5 Nov, 14.00–15.00)

1. Datang 10 menit lebih awal; program harian dihentikan pengelola.
2. Serahkan berkas final `t17-….yaml` ke pengelola (isi sama persis dengan versi yang disetujui pembimbing).
3. Periksa perangkat: `python meja.py periksa` (ESP32, mikrofon, kamera terdeteksi); cocokkan posisi benda dengan foto acuan.
4. Uji satu-dua kondisi, hentikan dengan Ctrl+C; beri catatan **"uji"** di lembar sesi (bukan data).
5. Jalankan rencana, hentikan setelah ±10 menit, periksa citra kipas bersama pembimbing (fokus: kipas terlihat jelas, tidak gelap/buram, tidak bergeser).

### Slot otomatis (Jumat, 6 Nov, 20.00)

- Dijalankan pengelola dengan `--tanpa-operator`.
- Pencatat menulis nomor kondisi yang terganggu pada lembar sesi (bila ada informasi dari pengelola).

### Setelah slot

1. Tunggu `manifest.json` ditulis dan baris log terakhir berbunyi **"Selesai"**.
2. Penyalinan data dilakukan pengelola (ke flash disk tim dan cadangan meja).
3. Kembalikan meja ke keadaan acuan; foto lembar sesi dan simpan bersama data.
4. Masukkan ke repositori tim: `label.csv`, sensor CSV, `manifest.json` → `data/`; tulis `data/MANIFEST.json` (nama sesi + SHA-256 `label.csv`).
5. Citra kamera berukuran besar **tidak di-commit**; simpan di penyimpanan tim dan catat tautannya di papan Workbench.

---

## 8. Pemeriksaan Mutu Data (hari yang sama)

**Khusus tim 17**
- [ ] Sesi otomatis berisi **360 kondisi** (18 kombinasi × 20 ulangan).
- [ ] Selang antar-frame di `kamera_index.csv` mendekati **0,1 detik**; catat bila sering lebih.

**Umum**
- [ ] Jumlah baris `label.csv` sesuai rencana (atau ada catatan di lembar sesi).
- [ ] Kelengkapan sensor (mis. IMU ≥ ±350 sampel/detik).
- [ ] Buka beberapa citra dari awal, tengah, dan akhir sesi: tidak gelap, buram, bingkai bergeser, atau ada orang yang tidak semestinya.
- [ ] Plot sinyal utama (mis. arus kipas/getaran) per kondisi, warnai menurut label: kondisi berlabel "menyala" tidak boleh sama dengan "mati".
- [ ] Cocokkan lembar sesi dengan `label.csv`; gangguan masuk daftar kondisi yang dikeluarkan.
- [ ] Tulis ringkasan di `data/CATATAN-SESI.md`.

---

## 9. Aturan Pemakaian Data untuk Pemodelan

1. Buang **1 detik pertama** setiap kondisi.
2. Pisahkan data uji **per ulangan** (grup), bukan acak per jendela.
3. Normalisasi dihitung dari data latih saja, lalu diterapkan apa adanya ke validasi dan uji.
4. Data tim lain hanya sebagai uji tambahan; data bersama dipakai sesuai keterangan kasus.
5. Laporkan hasil akhir sebagai **rata-rata ± simpangan dari 3 seed**, beserta ukuran model ONNX (KB) dan latensi (ms) di laptop meja.
6. Tabel komparasi utama, pemilihan jalur purwarupa, dan uji purwarupa selalu dihitung pada **data uji dari meja**.

> **Catatan teknis untuk dicek di simulasi:** pastikan indeks ulangan (1–20) dapat ditelusuri dari `label.csv`/log, karena urutan kondisi diacak dan pemisahan data bergantung pada informasi ini.

---

## 10. Kekeliruan yang Perlu Dihindari

- Menganggap putaran dapat dihitung langsung dari frame, padahal laju kamera terlalu rendah (aliasing).
- Mengabaikan stempel waktu frame yang tidak teratur.
- Memisahkan data uji acak per jendela (metrik menjadi tinggi semu).
- Menggeser tiang kamera atau mengubah pencahayaan ruang di tengah sesi.

---

## 11. Kedudukan Data Sekunder

Model yang dilatih hanya pada data eksternal **tidak memenuhi tujuan kasus ini**, tetapi sah sebagai:

- pralatih / transfer learning sebelum fine-tuning pada data meja;
- augmentasi (dilaporkan);
- uji generalisasi tambahan (tabel terpisah);
- pembanding "latih di data sekunder, uji di data meja" untuk menunjukkan pergeseran domain (dianjurkan).

Tidak sah: menggantikan data meja sebagai data latih utama, dicampur ke data uji utama, atau metrik data sekunder dilaporkan sebagai capaian kasus.

---

## 12. Kriteria Selesai

- [ ] Rencana final disetujui pembimbing (komentar persetujuan di tugas).
- [ ] Berkas final diserahkan ke pengelola meja **sebelum 4 Nov 2026, 12.00**.
- [ ] Perkiraan waktu sesi muat di slot (lihat bagian 5: ±33 menit, muat).

---

## Lampiran: Rencana Asli (YAML)

```yaml
# Rencana eksperimen tim 17: Taksiran kecepatan kipas dari video
# Label: Otomatis: duty PWM kipas
tim: 17
judul: Taksiran kecepatan kipas dari video
pembimbing: Ade Lailani
pilar: Citra
seed: 1017
ulangan: 20
durasi_kondisi_detik: 5
jeda_detik: 0.5
rekam:
  audio:
    aktif: false
  kamera:
    aktif: true
    interval_detik: 0.1
    lebar: 640
    tinggi: 480
faktor:
  kipas:
    - 0
    - 32
    - 64
    - 96
    - 128
    - 160
    - 192
    - 224
    - 255
  lampu:
    - 128
    - 255
metode:
  jenis_tugas: Regresi
  masukan_model: Urutan 10 frame (10 fps)
  metrik_utama: MAE (% duty)
  jalur:
    - CNN
    - TL
    - RNN
    - AE
  pembanding_non_dl: Energi beda-frame + regresi linear
```
