"""Jalur CNN: CNN 2-D kecil atas citra RGB [3, H, W].

Empat blok Conv 3×3 → BatchNorm → ReLU → MaxPool 2 (32 → 64 → 128 → 128), rata-rata global, dropout, linear.
"""
from __future__ import annotations

HIPER = {"epoch": 25, "lr": 2e-3, "batch": 32, "wd": 1e-4, "dropout": 0.2}


def buat(n_keluaran: int, n_kanal: int = 3):
    import torch.nn as nn

    def blok(a, b):
        return nn.Sequential(nn.Conv2d(a, b, 3, padding=1, bias=False), nn.BatchNorm2d(b), nn.ReLU(), nn.MaxPool2d(2))

    return nn.Sequential(blok(n_kanal, 32), blok(32, 64), blok(64, 128), blok(128, 128), nn.AdaptiveAvgPool2d(1),
                         nn.Flatten(), nn.Dropout(HIPER["dropout"]), nn.Linear(128, n_keluaran))


def jalankan(Xtr, ytr, Xva, yva, Xte, *, seed, latih, cetak="", keluaran=None, kodek=None):
    model = buat(keluaran or int(ytr.max()) + 1, Xtr.shape[1])
    info = latih.latih(model, Xtr, ytr, Xva, yva, seed=seed, epoch=HIPER["epoch"], lr=HIPER["lr"],
                       batch=HIPER["batch"], wd=HIPER["wd"], cetak=cetak, kodek=kodek)
    return model, info
