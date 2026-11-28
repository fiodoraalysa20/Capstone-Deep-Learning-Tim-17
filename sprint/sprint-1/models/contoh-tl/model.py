"""Jalur TL: MobileNetV3-Small pralatih ImageNet, disetel ulang.

Citra terstandar diperbesar ke 128 × 128 (64 × 64 terlalu kecil untuk peta fitur terakhir), lapisan akhir diganti,
momentum BatchNorm dikembalikan ke 0,1.
Bobot diunduh sekali ke cache torch pengguna, tidak di repositori.
"""
from __future__ import annotations

HIPER = {"epoch": 10, "lr": 5e-4, "batch": 32, "wd": 1e-4, "ukuran": 128}


def buat(n_keluaran: int, n_kanal: int = 3):
    import torch.nn as nn
    from torchvision.models import MobileNet_V3_Small_Weights, mobilenet_v3_small

    inti = mobilenet_v3_small(weights=MobileNet_V3_Small_Weights.IMAGENET1K_V1)
    inti.classifier[-1] = nn.Linear(inti.classifier[-1].in_features, n_keluaran)
    # torchvision memasang momentum BatchNorm 0,01 di MobileNetV3: dengan beberapa ratus langkah latih statistik
    # berjalan masih statistik ImageNet, sehingga mode evaluasi jauh berbeda dari mode latih (loss latih turun,
    # validasi setara penebak tetap). Momentum 0,1 (bawaan PyTorch) membuat statistik mengikuti data meja.
    for m in inti.modules():
        if isinstance(m, nn.BatchNorm2d):
            m.momentum = 0.1

    class TL(nn.Module):
        def __init__(self):
            super().__init__()
            # >3 kanal (mis. 4 bingkai × RGB): adaptor 1×1 yang dipelajari memetakan ke 3 kanal masukan pralatih
            self.adaptor = nn.Conv2d(n_kanal, 3, 1) if n_kanal != 3 else nn.Identity()
            self.inti = inti

        def forward(self, x):
            x = nn.functional.interpolate(x, size=(HIPER["ukuran"], HIPER["ukuran"]), mode="bilinear", align_corners=False)
            return self.inti(self.adaptor(x))

    return TL()


def jalankan(Xtr, ytr, Xva, yva, Xte, *, seed, latih, cetak="", keluaran=None, kodek=None):
    model = buat(keluaran or int(ytr.max()) + 1, Xtr.shape[1])
    info = latih.latih(model, Xtr, ytr, Xva, yva, seed=seed, epoch=HIPER["epoch"], lr=HIPER["lr"],
                       batch=HIPER["batch"], wd=HIPER["wd"], cetak=cetak, kodek=kodek)
    return model, info
