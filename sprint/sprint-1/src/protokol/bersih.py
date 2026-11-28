"""Bagian bersama jalur pembersihan ucapan (dipakai models/*/model.py): masukan [B, 1, F, T] = |Y|^0,3 (campuran), keluaran [B, F, T] = taksiran
|S|^0,3 = masker sigmoid × masukan. Ciri untuk jaringan = log masukan, dinormalisasi per pita frekuensi (BatchNorm1d:
rata-rata dan simpangan dipelajari dari data latih)."""
from __future__ import annotations


def ciri(n_pita: int):
    import torch
    import torch.nn as nn

    class Ciri(nn.Module):
        def __init__(self):
            super().__init__()
            self.bn = nn.BatchNorm1d(n_pita)

        def forward(self, x):                       # x [B, 1, F, T] → [B, F, T]
            return self.bn(torch.log(x[:, 0] + 1e-4))

    return Ciri()


def jalankan_umum(buat, HIPER, Xtr, ytr, Xva, yva, *, seed, latih, cetak, kodek):
    model = buat(Xtr.shape[2])
    info = latih.latih(model, Xtr, ytr, Xva, yva, seed=seed, epoch=HIPER["epoch"], lr=HIPER["lr"],
                       batch=HIPER["batch"], wd=HIPER["wd"], cetak=cetak, kodek=kodek)
    return model, info
