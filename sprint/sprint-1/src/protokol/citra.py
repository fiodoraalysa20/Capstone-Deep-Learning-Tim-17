"""Bingkai kamera meja (``kamera/*.jpg`` + ``kamera_index.csv``; ``t_host`` = saat bingkai diambil).

``Kamera(folder).bingkai(t0, t1)`` → daftar (waktu, jalur) bingkai di antara dua waktu host.
``baca(jalur, ukuran, potong)`` → larik float32 [3, ukuran, ukuran] bernilai 0–1. ``potong`` = (kiri, atas, kanan,
bawah) dalam pecahan lebar/tinggi, untuk memusatkan bagian meja yang relevan sebelum diperkecil.
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np


class Kamera:
    def __init__(self, folder: Path):
        folder = Path(folder)
        with (folder / "kamera_index.csv").open(encoding="utf-8") as f:
            baris = list(csv.DictReader(f))
        self.t = np.array([float(b["t_host"]) for b in baris])
        self.jalur = [folder / "kamera" / b["berkas"] for b in baris]
        urut = np.argsort(self.t, kind="stable")
        self.t = self.t[urut]
        self.jalur = [self.jalur[i] for i in urut]

    def bingkai(self, t0: float, t1: float) -> list[tuple[float, Path]]:
        i0, i1 = np.searchsorted(self.t, [t0, t1])
        return [(float(self.t[i]), self.jalur[i]) for i in range(i0, i1)]


def baca(jalur: Path, ukuran: int = 64, potong: tuple[float, float, float, float] | None = None) -> np.ndarray:
    from PIL import Image

    with Image.open(jalur) as im:
        im = im.convert("RGB")
        if potong:
            w, h = im.size
            im = im.crop((int(potong[0] * w), int(potong[1] * h), int(potong[2] * w), int(potong[3] * h)))
        im = im.resize((ukuran, ukuran), Image.BILINEAR)
        return (np.asarray(im, np.float32) / 255.0).transpose(2, 0, 1).copy()


class StandarRGB:
    """Rata-rata dan simpangan per kanal warna dari data latih; X [N, 3, H, W]."""

    def __init__(self, X_latih: np.ndarray):
        self.mu = X_latih.mean(axis=(0, 2, 3), keepdims=True)
        self.sd = X_latih.std(axis=(0, 2, 3), keepdims=True) + 1e-6

    def __call__(self, X: np.ndarray) -> np.ndarray:
        return ((X - self.mu) / self.sd).astype(np.float32)
