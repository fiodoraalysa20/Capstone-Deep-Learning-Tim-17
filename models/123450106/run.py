"""Jalur RNN: Jaringan berulang (GRU / LSTM) atas urutan 10 frame (10 fps).

    python models/123450106/run.py --seed 1 [--final]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

AKAR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AKAR))
from src.protokol import data  # noqa: E402

NIM = Path(__file__).resolve().parent.name
JALUR = "rnn"


class VideoKipasRNN(nn.Module):
    """Model Spatio-Temporal CNN + GRU untuk urutan 10 frame video kipas (B, 10, 64, 64)."""

    def __init__(self, fitur_primer_dim: int | None = None, hidden_dim: int = 32):
        super().__init__()
        self.proyeksi_2d = (
            nn.Linear(fitur_primer_dim, 10 * 64)
            if fitur_primer_dim is not None
            else None
        )
        # Ekstraktor fitur spasial per-frame (citra 64x64)
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),  # -> 16 x 32 x 32
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),  # -> 32 x 16 x 16
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((2, 2)),  # -> 64 x 2 x 2 = 256
            nn.Flatten(),
            nn.Linear(256, 64),
            nn.ReLU(),
        )
        # Jaringan berulang atas urutan 10 langkah waktu
        self.rnn = nn.GRU(
            input_size=64,
            hidden_size=hidden_dim,
            num_layers=1,
            batch_first=True,
        )
        # Kepala regresi taksiran % duty kipas (0 - 100%)
        self.head = nn.Sequential(
            nn.Linear(hidden_dim, 16),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(16, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.ndim == 4:
            # Masukan urutan 10 frame citra: (B, 10, 64, 64)
            B, T, H, W = x.shape
            x_frames = x.view(B * T, 1, H, W)
            feat = self.cnn(x_frames)         # (B * 10, 64)
            seq_feat = feat.view(B, T, -1)     # (B, 10, 64)
        elif x.ndim == 2 and self.proyeksi_2d is not None:
            B = x.shape[0]
            seq_feat = self.proyeksi_2d(x).view(B, 10, 64)
        else:
            raise ValueError(f"Bentuk masukan tidak didukung: {tuple(x.shape)}")

        out, _ = self.rnn(seq_feat)            # (B, 10, hidden_dim)
        last_step = out[:, -1, :]              # ambil langkah waktu terakhir (t=10)
        return self.head(last_step).squeeze(-1) # (B,)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--final", action="store_true", help="evaluasi data uji sekali")
    parser.add_argument("--perangkat", default="cpu laptop")
    parser.add_argument("--sesi-dir", type=str, default=None, help="Opsional: folder sesi simulasi")
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    t0 = time.time()

    X_train, y_train, X_val, y_val, X_test, y_test = data.muat(args.sesi_dir)
    dim_primer = X_train.shape[1] if X_train.ndim == 2 else None

    print(f"[{JALUR.upper()}] Masukan X_train: {X_train.shape} | y_train: {y_train.shape}")
    print(f"[{JALUR.upper()}] Masukan X_val  : {X_val.shape} | y_val: {y_val.shape}")
    print(f"[{JALUR.upper()}] Masukan X_test : {X_test.shape} | y_test: {y_test.shape}")

    model = VideoKipasRNN(fitur_primer_dim=dim_primer, hidden_dim=32)
    train_loader = DataLoader(
        TensorDataset(
            torch.tensor(X_train, dtype=torch.float32),
            torch.tensor(y_train, dtype=torch.float32),
        ),
        batch_size=args.batch_size,
        shuffle=True,
    )

    criterion = nn.L1Loss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    model.train()
    for ep in range(args.epochs):
        loss_total = 0.0
        for bx, by in train_loader:
            optimizer.zero_grad()
            pred = model(bx)
            loss = criterion(pred, by)
            loss.backward()
            optimizer.step()
            loss_total += loss.item() * len(by)
        loss_mean = loss_total / len(y_train)

    model.eval()
    with torch.no_grad():
        pred_val = model(torch.tensor(X_val, dtype=torch.float32)).numpy()
        pred_test = None
        if args.final and X_test is not None:
            pred_test = model(torch.tensor(X_test, dtype=torch.float32)).numpy()

    assert pred_val.shape == y_val.shape, f"Ukuran keluaran {pred_val.shape} != {y_val.shape}"
    print(f"[{JALUR.upper()}] Keluaran pred_val: {pred_val.shape} (sesuai target {y_val.shape})")

    durasi = time.time() - t0
    folder_output = AKAR / "results" / NIM
    folder_output.mkdir(parents=True, exist_ok=True)
    file_pred_val = folder_output / "pred_val.npy"
    np.save(file_pred_val, pred_val)

    cmd = [
        sys.executable,
        "-m",
        "src.common.evaluate",
        "--nim",
        NIM,
        "--model",
        JALUR,
        "--seed",
        str(args.seed),
        "--pred-val",
        str(file_pred_val),
        "--durasi",
        f"{durasi:.1f}",
        "--perangkat",
        args.perangkat,
    ]
    if pred_test is not None:
        file_pred_test = folder_output / "pred_test.npy"
        np.save(file_pred_test, pred_test)
        cmd.extend(["--pred-test", str(file_pred_test)])

    subprocess.run(cmd, check=True, cwd=AKAR)


if __name__ == "__main__":
    main()
