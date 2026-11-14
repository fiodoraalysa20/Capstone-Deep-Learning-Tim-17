# Tim 17: Pembagian Peran Slot dan Lembar Sesi

**Judul:** Taksiran kecepatan kipas dari video · **Pilar:** Citra · **Pembimbing:** Ade Lailani
**Slot operator:** Kamis, 5 Nov 2026, 14.00–15.00 · **Slot otomatis:** Jumat, 6 Nov 2026, 20.00 – 7 Nov 00.00 · **Uji purwarupa:** Selasa, 17 Nov 2026, 10.30–11.00

---

# Bagian A. Pembagian Peran Slot

Tim beranggotakan 4 orang, sehingga **pencatat kejadian dan penjaga bingkai dirangkap satu orang** (sesuai panduan metode bagian 4). Rencana tim 17 sepenuhnya otomatis dan tanpa partisipan manusia, jadi peran koordinator partisipan difokuskan pada koordinasi dengan pengelola meja dan pembimbing. Audio tidak direkam, sehingga peran "penjaga suara" tidak berlaku; yang dijaga hanya **bingkai kamera**.

## A.1 Tabel peran

| No | Peran | Pemegang | Jalur model | Tugas selama slot |
|---|---|---|---|---|
| 1 | Operator perekam | _(nama anggota 1)_ | CNN | Menjalankan `meja.py`, menjalankan uji satu-dua kondisi lalu sesi percobaan, menghentikan dengan Ctrl+C bila ada masalah, memastikan baris log "Selesai" dan `manifest.json` muncul |
| 2 | Operator alat | _(nama anggota 2)_ | TL | Mencocokkan posisi benda dengan foto acuan meja, memastikan tiang kamera tidak bergeser, membersihkan bingkai dari benda di luar rencana, mengembalikan meja ke keadaan acuan setelah slot |
| 3 | Koordinator (pengganti koordinator partisipan) | _(nama anggota 3)_ | RNN | Datang lebih awal, menyerahkan berkas `t17-….yaml` final ke pengelola, menyepakati keadaan lampu ruang selama slot otomatis, menghubungi pembimbing dan pengelola, mengurus penyalinan data ke flash disk tim |
| 4 | Pencatat kejadian + penjaga bingkai | _(nama anggota 4)_ | AE | Mengisi lembar sesi (nomor kondisi terganggu, waktu, keterangan); mengawasi pratinjau kamera dan memberi tanda bila ada orang lewat, bayangan, atau bingkai bergeser |

> Peran di atas adalah **peran slot**, terpisah dari jalur model. Kolom jalur model hanya pengingat satu jalur per anggota; boleh disesuaikan.

## A.2 Pengganti (cadangan)

Bila ada anggota berhalangan, peran diambil alih sebagai berikut (isi sebelum slot):

| Peran | Pengganti |
|---|---|
| Operator perekam | _(nama)_ |
| Operator alat | _(nama)_ |
| Koordinator | _(nama)_ |
| Pencatat + penjaga bingkai | _(nama)_ |

## A.3 Tugas per tahap

| Tahap | Operator perekam | Operator alat | Koordinator | Pencatat + penjaga bingkai |
|---|---|---|---|---|
| **Sebelum slot** (3–1 hari) | Menjalankan simulasi (360 kondisi, ±33 menit) | Menyiapkan daftar benda yang harus disingkirkan dari bingkai | Memastikan rencana final disetujui dan diserahkan sebelum 4 Nov 12.00; menyepakati keadaan lampu ruang | Mencetak lembar sesi; menguji pemotong jendela pada data simulasi |
| **Tiba** (10 menit awal) | Menyiapkan laptop dan repo | Membandingkan meja dengan foto acuan | Menyerahkan berkas YAML ke pengelola | Mengisi header lembar sesi |
| **Pemeriksaan perangkat** | Mendampingi `meja.py periksa` | Memeriksa bingkai kamera dan posisi tiang | Mencatat keadaan lampu ruang | Mencatat hasil pemeriksaan |
| **Uji satu kondisi** | Menjalankan dan menghentikan dengan Ctrl+C | Memeriksa citra kipas | Mengonfirmasi dengan pembimbing | Memberi catatan "uji" di lembar sesi |
| **Sesi percobaan** (±10 menit) | Menjalankan rencana asli | Mengawasi kipas dan lampu | Mendampingi pembimbing memeriksa citra | Mencatat gangguan dengan nomor kondisi `[n/360]` |
| **Setelah slot** | Menunggu `manifest.json` | Mengembalikan meja ke keadaan acuan | Meminta pengelola menyalin data | Memfoto lembar sesi |

## A.4 Teks untuk komentar tugas (siap salin)

```
Pembagian peran slot Tim 17 (slot operator Kamis 5 Nov 2026, 14.00–15.00):
- Operator perekam: [nama anggota 1]
- Operator alat: [nama anggota 2]
- Koordinator (pengganti koordinator partisipan; rencana tanpa partisipan manusia): [nama anggota 3]
- Pencatat kejadian + penjaga bingkai (dirangkap, tim 4 orang): [nama anggota 4]
Penjaga suara tidak diperlukan karena audio nonaktif.
Lembar sesi sudah disiapkan dan siap dibawa.
```

---

# Bagian B. Lembar Sesi (siap cetak)

> Cetak satu lembar per sesi (satu untuk slot operator, satu untuk slot otomatis). Tanpa partisipan manusia, jadi tidak ada formulir persetujuan dan ID samaran. Foto lembar ini setelah slot dan simpan bersama data.

## B.1 Identitas sesi

| Butir | Isian |
|---|---|
| Tim / judul | 17 / Taksiran kecepatan kipas dari video |
| Berkas rencana | `t17-kecepatan-kipas-video.yaml` (seed 1017) |
| Jenis sesi | ☐ Operator (percobaan)  ☐ Otomatis (penuh)  ☐ Cadangan 12 Nov |
| Tanggal / jam mulai / jam selesai | ____ / ____ / ____ |
| Nama folder sesi (`sesi-…`) | ______________________ |
| Pembimbing pendamping | ______________________ |
| Pengelola meja | ______________________ |
| Keadaan lampu ruang | ☐ Mati  ☐ Menyala (disepakati dengan pengelola) |

## B.2 Peran pada sesi ini

| Peran | Nama |
|---|---|
| Operator perekam | |
| Operator alat | |
| Koordinator | |
| Pencatat + penjaga bingkai | |

## B.3 Checklist sebelum rekam

| ✓ | Butir |
|---|---|
| ☐ | Program harian dihentikan pengelola |
| ☐ | Berkas YAML final diserahkan (nama `t17-….yaml`, isi sama dengan versi disetujui) |
| ☐ | `python meja.py periksa`: ESP32, mikrofon, kamera terdeteksi |
| ☐ | Posisi benda cocok dengan foto acuan |
| ☐ | Tiang kamera (75 cm, miring 45°) tidak bergeser |
| ☐ | Bingkai bersih dari benda di luar rencana (tas, botol minum) |
| ☐ | Kipas terlihat jelas di bingkai, citra tidak gelap/buram |
| ☐ | Tidak ada cairan di dekat ESP32 dan laptop |
| ☐ | Uji satu kondisi dilakukan dan dicatat "uji" (bukan data) |

## B.3a Catatan sesi uji

| Nomor kondisi diuji | Hasil bingkai | Hasil instruksi layar | Catatan |
|---|---|---|---|
| | | | |

## B.4 Catatan gangguan

Tulis **nomor kondisi** persis seperti tampil di layar, mis. `[37/360]`.

| No | Nomor kondisi | Waktu | Jenis gangguan | Keterangan | Dikeluarkan? |
|---|---|---|---|---|---|
| 1 | [   /360] | | ☐ Bayangan/orang lewat ☐ Alat tersentuh ☐ Bingkai bergeser ☐ Kabel/alat lepas ☐ Lain | | ☐ Ya ☐ Tidak |
| 2 | [   /360] | | ☐ Bayangan/orang lewat ☐ Alat tersentuh ☐ Bingkai bergeser ☐ Kabel/alat lepas ☐ Lain | | ☐ Ya ☐ Tidak |
| 3 | [   /360] | | ☐ Bayangan/orang lewat ☐ Alat tersentuh ☐ Bingkai bergeser ☐ Kabel/alat lepas ☐ Lain | | ☐ Ya ☐ Tidak |
| 4 | [   /360] | | ☐ Bayangan/orang lewat ☐ Alat tersentuh ☐ Bingkai bergeser ☐ Kabel/alat lepas ☐ Lain | | ☐ Ya ☐ Tidak |
| 5 | [   /360] | | ☐ Bayangan/orang lewat ☐ Alat tersentuh ☐ Bingkai bergeser ☐ Kabel/alat lepas ☐ Lain | | ☐ Ya ☐ Tidak |
| 6 | [   /360] | | ☐ Bayangan/orang lewat ☐ Alat tersentuh ☐ Bingkai bergeser ☐ Kabel/alat lepas ☐ Lain | | ☐ Ya ☐ Tidak |
| 7 | [   /360] | | ☐ Bayangan/orang lewat ☐ Alat tersentuh ☐ Bingkai bergeser ☐ Kabel/alat lepas ☐ Lain | | ☐ Ya ☐ Tidak |
| 8 | [   /360] | | ☐ Bayangan/orang lewat ☐ Alat tersentuh ☐ Bingkai bergeser ☐ Kabel/alat lepas ☐ Lain | | ☐ Ya ☐ Tidak |

Bila gangguan berlangsung lama (mis. kabel tercabut): hentikan dengan Ctrl+C, data yang sudah terekam tetap disimpan, sesi dapat dilanjutkan pada **slot cadangan 12 November**.

## B.5 Pemeriksaan setelah slot

| ✓ | Butir |
|---|---|
| ☐ | `manifest.json` tertulis dan log terakhir berbunyi "Selesai" |
| ☐ | Data disalin pengelola ke flash disk tim dan cadangan meja |
| ☐ | Meja dikembalikan ke keadaan acuan (area objek kosong, pintu kotak tertutup) |
| ☐ | Lembar sesi difoto dan disimpan bersama data |
| ☐ | Data masuk repositori tim; `data/MANIFEST.json` (SHA-256 `label.csv`) ditulis |
| ☐ | Citra besar disimpan di penyimpanan tim, tautan dicatat di papan Workbench |

## B.6 Pemeriksaan mutu (hari yang sama)

| Pemeriksaan | Hasil | Catatan |
|---|---|---|
| Jumlah kondisi di `label.csv` (rencana: 360 = 18 × 20) | ______ | |
| Selang antar-frame di `kamera_index.csv` ≈ 0,1 detik | ☐ Ya ☐ Sering lebih | |
| Kelengkapan sensor (mis. IMU ≥ ±350 sampel/detik) | ☐ Baik ☐ Bermasalah | |
| Citra awal/tengah/akhir sesi: terang, fokus, bingkai tetap | ☐ Baik ☐ Bermasalah | |
| Plot sinyal per kondisi sesuai label (kipas menyala ≠ mati) | ☐ Sesuai ☐ Janggal | |
| Gangguan di lembar sesi sudah masuk daftar kondisi dikeluarkan | ☐ Ya ☐ Belum | |
| Ringkasan ditulis di `data/CATATAN-SESI.md` | ☐ Sudah | |

## B.7 Pengesahan

| Peran | Nama | Tanda tangan |
|---|---|---|
| Pencatat | | |
| Pembimbing | | |
| Pengelola meja | | |
