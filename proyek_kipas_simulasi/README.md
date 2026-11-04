# Simulasi proyek kipas

## Instalasi
```bash
python -m pip install pyyaml
```

## Jalankan
Dari folder proyek:
```bash
python meja.py --simulasi jalankan rencana/t17-kecepatan-kipas-video.yaml
```

## Hasil
Program membuat folder sesi di `data/simulasi/` berisi:
- `conditions.csv`: daftar 360 kondisi.
- `summary.json`: ringkasan konfigurasi dan estimasi durasi.
- `simulation_log.txt`: log simulasi.

Durasi 33 menit adalah estimasi: 360 x (5 detik rekaman + 0,5 detik overhead).
Program tidak menunggu 33 menit, tidak mengendalikan kipas/lampu/kamera, dan tidak
menghasilkan video. Pastikan label PWM sesuai dengan nilai yang benar-benar
diterapkan perangkat. Indikator persentase kipas portable tidak otomatis sama
dengan duty-cycle PWM.
