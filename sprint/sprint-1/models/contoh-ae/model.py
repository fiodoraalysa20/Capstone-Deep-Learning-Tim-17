"""Jalur AE: autoencoder konvolusi atas citra, lalu kepala dari ruang laten (encoder dibekukan)."""
from __future__ import annotations

HIPER = {"epoch_ae": 25, "lr_ae": 2e-3, "epoch": 30, "lr": 2e-3, "batch": 32, "wd": 1e-4, "laten": 32}


def _ae(c: int = 3):
    import torch.nn as nn

    k = HIPER["laten"]
    enc = nn.Sequential(nn.Conv2d(c, 32, 3, 2, 1), nn.BatchNorm2d(32), nn.ReLU(), nn.Conv2d(32, 64, 3, 2, 1),
                        nn.BatchNorm2d(64), nn.ReLU(), nn.Conv2d(64, k, 3, 2, 1))
    dek = nn.Sequential(nn.ConvTranspose2d(k, 64, 4, 2, 1), nn.BatchNorm2d(64), nn.ReLU(),
                        nn.ConvTranspose2d(64, 32, 4, 2, 1), nn.BatchNorm2d(32), nn.ReLU(), nn.ConvTranspose2d(32, c, 4, 2, 1))
    return enc, dek


def jalankan(Xtr, ytr, Xva, yva, Xte, *, seed, latih, cetak="", keluaran=None, kodek=None):
    import torch
    import torch.nn as nn

    enc, dek = _ae(Xtr.shape[1])
    g = torch.Generator().manual_seed(seed)
    X = torch.from_numpy(Xtr); V = torch.from_numpy(Xva)
    opt = torch.optim.AdamW(list(enc.parameters()) + list(dek.parameters()), lr=HIPER["lr_ae"], weight_decay=HIPER["wd"])
    riwayat = []
    for e in range(1, HIPER["epoch_ae"] + 1):
        enc.train(); dek.train()
        for j in torch.randperm(len(X), generator=g).split(HIPER["batch"]):
            opt.zero_grad(); loss = nn.functional.mse_loss(dek(enc(X[j])), X[j]); loss.backward(); opt.step()
        enc.eval(); dek.eval()
        with torch.no_grad():
            mse = float(sum(nn.functional.mse_loss(dek(enc(v)), v, reduction="sum") for v in V.split(128)) / V.numel())
        riwayat.append({"epoch": e, "val_mse": round(mse, 4)})
        if cetak:
            print(f"[{cetak}/ae] epoch {e:2d} val_mse {mse:.4f}", flush=True)
    for p in enc.parameters():
        p.requires_grad = False
    inti = nn.Sequential(enc, nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(HIPER["laten"], 64), nn.ReLU(),
                         nn.Dropout(0.2), nn.Linear(64, keluaran or int(ytr.max()) + 1))

    class BekuBN(nn.Module):
        def __init__(self, m):
            super().__init__()
            self.m = m

        def train(self, mode=True):
            super().train(mode)
            self.m[0].eval()
            return self

        def forward(self, x):
            return self.m(x)

    model = BekuBN(inti)
    info = latih.latih(model, Xtr, ytr, Xva, yva, seed=seed, epoch=HIPER["epoch"], lr=HIPER["lr"],
                       batch=HIPER["batch"], wd=HIPER["wd"], cetak=cetak, kodek=kodek)
    info["riwayat_ae"] = riwayat
    return model, info
