"""Peristiwa ucapan untuk sesi berisyarat dengan kondisi pendek (kata/frasa per kondisi).

Pada sesi meja 13–18 Nov, ucapan sering tidak jatuh di kondisinya sendiri (partisipan membaca isyarat yang terlambat,
dan kondisi hanya 2,5 s). Alih-alih memotong per kondisi, contoh dibangun dari peristiwa ucapan yang dideteksi dari
energi, lalu diberi label kondisi tempatnya jatuh digeser ``geser`` kondisi. Besar geseran diuji dari ISI ucapan
(``uji_geser``): ucapan berlabel sama harus saling mirip.

``cari(x, t0)``            → [(awal, akhir)] detik jam meja
``ciri_dtw(x)``            → MFCC 13 dinormalisasi per ucapan (bingkai 20 ms)
``dtw(A, B)``              → jarak DTW ternormalisasi (anti-diagonal, NumPy)
``kumpulkan(au, blok)``    → semua peristiwa per partisipan, dengan indeks kondisi tempatnya jatuh
``uji_geser(peristiwa, label, kolom)`` → {geser: ketepatan 1-NN di dalam penutur}
"""
from __future__ import annotations

from collections import defaultdict

import numpy as np

AMBANG_DB, CELAH_S, MIN_S = 12.0, 0.3, 0.25


def _bandpass(x: np.ndarray) -> np.ndarray:
    from scipy.signal import butter, sosfiltfilt
    return sosfiltfilt(butter(4, [300, 3400], "bandpass", fs=16000, output="sos"), x)


def cari(x: np.ndarray, t0: float, ambang_db: float = AMBANG_DB) -> list[tuple[float, float]]:
    xf = _bandpass(x)
    n = 160
    e = 10 * np.log10((xf[: len(xf) // n * n].reshape(-1, n) ** 2).mean(1) + 1e-12)
    idx = np.where(e > np.percentile(e, 20) + ambang_db)[0]
    ev = []
    if len(idx):
        s = p = idx[0]
        for i in idx[1:]:
            if i - p > CELAH_S * 100:
                ev.append((s, p)); s = i
            p = i
        ev.append((s, p))
    return [(t0 + s / 100, t0 + (p + 1) / 100) for s, p in ev if (p - s) >= MIN_S * 100]


def ciri_dtw(x: np.ndarray) -> np.ndarray:
    from src.protokol import fitur
    m = fitur.mfcc(fitur.logmel(x), 13)[:, ::2].T
    return (m - m.mean(0)) / (m.std(0) + 1e-6)


def dtw(A: np.ndarray, B: np.ndarray) -> float:
    D = np.sqrt(((A[:, None, :] - B[None, :, :]) ** 2).sum(-1))
    n, m = D.shape
    C = np.full((n + 1, m + 1), np.inf); C[0, 0] = 0.0
    for d in range(2, n + m + 1):
        i = np.arange(max(1, d - m), min(n, d - 1) + 1); j = d - i
        C[i, j] = D[i - 1, j - 1] + np.minimum(np.minimum(C[i - 1, j], C[i, j - 1]), C[i - 1, j - 1])
    return float(C[n, m] / (n + m))


def kumpulkan(au, label: list[dict], blok: dict[str, list[dict]], buntut_s: float = 7.0) -> list[dict]:
    """Peristiwa ucapan semua blok. Tiap peristiwa: awal, akhir, pusat, blok (kunci), j (indeks kondisi tempat
    pusatnya jatuh, dalam ``label`` urut nomor)."""
    mulai = np.array([b["t_mulai_host"] for b in label])
    akhir_audio = au.potongan[-1].t1
    keluar = []
    for k, bs in blok.items():
        t0 = bs[0]["t_mulai_host"]; t1 = min(bs[-1]["t_selesai_host"] + buntut_s, akhir_audio - 0.05)
        # satu rentang per blok bila audio bersambung; bila ada celah sungguhan, per potongan audio
        rentang = [(t0, t1)] if au.potong(t0, t1) is not None else \
            [(max(t0, p.t0 + 0.01), min(t1, p.t1 - 0.01)) for p in au.potongan]
        for a, z in rentang:
            if z - a < 1.0:
                continue
            x = au.potong(a, z)
            if x is None:
                continue
            for s, e in cari(x, a):
                c = (s + e) / 2
                keluar.append({"awal": s, "akhir": e, "pusat": c, "blok": k, "j": int(np.searchsorted(mulai, c) - 1)})
    return keluar


def uji_geser(au, peristiwa: list[dict], label: list[dict], kolom: str, kosong: str | None = None,
              rentang=range(0, 5)) -> dict[int, float]:
    ciri = []
    for ev in peristiwa:
        x = au.potong(ev["awal"] - 0.1, min(ev["akhir"] + 0.1, ev["awal"] + 2.5))
        ciri.append(None if x is None else ciri_dtw(x))
    hasil = {}
    for g in rentang:
        benar = tot = 0
        kel = defaultdict(list)
        for ev, m in zip(peristiwa, ciri):
            i = ev["j"] - g
            if m is not None and 0 <= i < len(label) and label[i][kolom] != kosong:
                kel[ev["blok"]].append((m, label[i][kolom]))
        for d in kel.values():
            for a, (q, l) in enumerate(d):
                if len(d) < 2:
                    continue
                nn = min((dtw(q, t), ll) for b, (t, ll) in enumerate(d) if b != a)
                benar += nn[1] == l; tot += 1
        hasil[g] = round(benar / max(tot, 1), 3)
    return hasil
