# Gladi rencana dengan mode simulasi

```bash
cd meja-uji-5v/perekam
python meja.py --simulasi --tim 17 --rencana ../rencana/t17-kecepatan-kipas-video.yaml
```

Simulasi menulis `label.csv`, `kamera_index.csv`, dan bingkai tiruan. Cek jumlah kondisi (360), lama sesi
(±33 menit), dan bahwa `kamera_index.csv` berselang 0,1 s. Waktu berhenti kipas hanya bisa diukur di meja sungguhan:
jalankan kipas 255 lalu 0 dan hitung detik sampai bilah diam di kamera.
