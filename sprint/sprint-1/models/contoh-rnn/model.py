"""Jalur RNN untuk urutan bingkai: CNN-LSTM.

Masukan [3·T, H, W] = T bingkai RGB berurutan. Setiap bingkai dikodekan CNN kecil yang sama (bobot dibagi), lalu
LSTM 1 lapis (64 unit) atas T langkah; keadaan terakhir → linear. Perbedaan antarbingkai (kipas berputar vs diam)
bisa ditangkap LSTM.
"""
from __future__ import annotations

HIPER = {"epoch": 25, "lr": 2e-3, "batch": 32, "wd": 1e-4, "unit": 64, "dropout": 0.2}


def buat(n_keluaran: int, n_kanal: int):
    import torch.nn as nn

    T = n_kanal // 3

    def blok(a, b):
        return nn.Sequential(nn.Conv2d(a, b, 3, padding=1, bias=False), nn.BatchNorm2d(b), nn.ReLU(), nn.MaxPool2d(2))

    class CnnLstm(nn.Module):
        def __init__(self):
            super().__init__()
            self.cnn = nn.Sequential(blok(3, 16), blok(16, 32), blok(32, 64), nn.AdaptiveAvgPool2d(1), nn.Flatten())
            self.lstm = nn.LSTM(64, HIPER["unit"], batch_first=True)
            self.kepala = nn.Sequential(nn.Dropout(HIPER["dropout"]), nn.Linear(HIPER["unit"], n_keluaran))

        def forward(self, x):                                   # x [B, 3T, H, W]
            B, _, H, W = x.shape
            z = self.cnn(x.reshape(B * T, 3, H, W)).reshape(B, T, -1)
            out, _ = self.lstm(z)
            return self.kepala(out[:, -1])

    return CnnLstm()


def jalankan(Xtr, ytr, Xva, yva, Xte, *, seed, latih, cetak="", keluaran=None, kodek=None):
    model = buat(keluaran or int(ytr.max()) + 1, Xtr.shape[1])
    info = latih.latih(model, Xtr, ytr, Xva, yva, seed=seed, epoch=HIPER["epoch"], lr=HIPER["lr"],
                       batch=HIPER["batch"], wd=HIPER["wd"], cetak=cetak, kodek=kodek)
    return model, info
