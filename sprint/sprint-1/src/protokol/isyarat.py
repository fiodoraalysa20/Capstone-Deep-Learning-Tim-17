"""Koreksi label faktor isyarat yang meleset, dan uji yang membuktikannya.

Latar (17 Nov 2026): pada sesi meja 16–17 Nov, bunyi aksi operator terdengar **dua kondisi setelah** kondisi
yang labelnya memuat aksi itu. Jedanya tetap sepanjang sesi dan sama dalam satuan kondisi (bukan detik),
sehingga bukan reaksi operator yang lambat. Dugaan sebabnya: operator membaca kartu "Eksperimen berjalan" di
web, yang menyorot kondisi yang SUDAH SELESAI (dilaporkan setelah kondisi berakhir, ditahan ≥ 5 s), bukan
halaman isyarat komputer meja yang tampil seketika.

Label alat (kipas, pompa, buzzer, lampu) TIDAK terdampak: alat disetel skrip tepat di awal kondisi.

``pasangkan(label, geser)``: setiap baris kondisi k dipasangkan dengan baris k−geser (urutan waktu) sebagai
sumber label isyarat; ``geser`` kondisi pertama tiap sesi tidak punya pasangan (isyarat yang dilihat operator
tidak diketahui) dan dikeluarkan.

``uji_geser(...)``: untuk setiap pergeseran, AUROC "ada aksi" vs "tidak ada aksi" dengan skor = lonjakan
bunyi terkuat dalam klip kondisi. Pergeseran yang benar memberi AUROC tertinggi; tanpa kesalahan tampilan,
puncaknya ada di 0.
"""
from __future__ import annotations

import numpy as np


def pasangkan(label: list[dict], geser: int) -> list[tuple[dict, dict | None]]:
    """[(baris kondisi k, baris sumber isyarat k−geser atau None)], urut waktu dalam SATU sesi."""
    urut = sorted(label, key=lambda b: b["t_mulai_host"])
    return [(b, urut[i - geser] if i >= geser else None) for i, b in enumerate(urut)]


def skor_lonjakan(x: np.ndarray, sr: int = 16000) -> float:
    """Lonjakan terkuat (dB) energi 50 ms terhadap median klip."""
    n = int(0.05 * sr)
    r = np.sqrt(np.convolve(np.square(x, dtype=np.float64), np.ones(n) / n, "valid"))
    return float(20 * np.log10(r.max() / max(np.median(r), 1e-12)))


def uji_geser(sesi_list, kolom: str, nilai_kosong: str, rentang=range(-2, 5)) -> dict[int, float]:
    """{geser: AUROC} atas semua sesi. ``sesi_list`` = [(label, Audio)], ``nilai_kosong`` = taraf "tanpa aksi"."""
    from sklearn.metrics import roc_auc_score

    hasil = {}
    for g in rentang:
        y, s = [], []
        for label, audio in sesi_list:
            urut = sorted(label, key=lambda b: b["t_mulai_host"])
            skor = []
            for b in urut:
                x = audio.potong(b["t_mulai_host"], b["t_selesai_host"])
                skor.append(None if x is None else skor_lonjakan(x))
            for i, b in enumerate(urut):
                j = i + g                                   # audio kondisi j memuat aksi berlabel kondisi i?
                if 0 <= j < len(urut) and skor[j] is not None:
                    y.append(b[kolom] != nilai_kosong); s.append(skor[j])
        hasil[g] = round(float(roc_auc_score(y, s)), 3)
    return hasil
