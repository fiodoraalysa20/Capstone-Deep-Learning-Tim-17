"""Uji "sidik blok": seberapa mudah dua blok yang LABELNYA SAMA dibedakan dari datanya.

Bila tiap kelas latih hanya punya satu blok dan validasi diambil dari blok yang sama, model bisa saja mengenali
blok (posisi kertas/klem yang dipasang ulang, tinggi air, suhu) alih-alih kelasnya, dan validasi tetap tampak
sempurna. Uji ini memakai fitur non-DL dan validasi silang per kondisi untuk membedakan blok A dan blok B dari
kelas yang sama. Akurasi mendekati 1 = setiap blok punya sidik yang kuat → validasi di dalam blok tidak bermakna.

Ini pemeriksaan DATA: label kelas blok uji tidak dipakai untuk memilih model atau hiperparameter apa pun.
"""
from __future__ import annotations

import numpy as np


def uji_sidik(F: np.ndarray, y: np.ndarray, satuan: np.ndarray, kondisi: np.ndarray, kelas: list[str],
              min_contoh: int = 20) -> dict[str, float | None]:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import GroupKFold, cross_val_score

    hasil: dict[str, float | None] = {}
    for k, nama in enumerate(kelas):
        m = y == k
        blok = sorted(set(satuan[m].tolist()))
        if len(blok) != 2:
            hasil[nama] = None
            continue
        yb = (satuan[m] == blok[1]).astype(int)
        if np.bincount(yb, minlength=2).min() < min_contoh:
            hasil[nama] = None
            continue
        s = cross_val_score(RandomForestClassifier(200, random_state=0, n_jobs=1), F[m], yb, groups=kondisi[m],
                            cv=GroupKFold(4))
        hasil[nama] = round(float(s.mean()), 3)
    return hasil
