import argparse
import os
import subprocess
import sys
import time
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.protokol import data


class VideoKipasCNN3D(nn.Module):
    """Arsitektur Spatio-Temporal 3D-CNN untuk urutan 10 frame citra kipas (B, 1, 10, 64, 64)."""

    def __init__(self, fitur_primer_dim: int | None = None):
        super().__init__()
        self.proyeksi_primer = (
            nn.Linear(fitur_primer_dim, 10 * 16 * 16)
            if fitur_primer_dim is not None
            else None
        )
        self.conv3d = nn.Sequential(
            nn.Conv3d(1, 16, kernel_size=(3, 3, 3), padding=1),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=(1, 2, 2)),
            nn.Conv3d(16, 32, kernel_size=(3, 3, 3), padding=1),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=(2, 2, 2)),
            nn.Conv3d(32, 64, kernel_size=(3, 3, 3), padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool3d((1, 1, 1)),
        )
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.ndim == 4:
            # Masukan langsung urutan 10 frame citra: (B, 10, 64, 64) -> (B, 1, 10, 64, 64)
            v = x.unsqueeze(1)
        elif x.ndim == 2 and self.proyeksi_primer is not None:
            v = self.proyeksi_primer(x).view(x.size(0), 1, 10, 16, 16)
        else:
            raise ValueError(f"Bentuk masukan tidak didukung: {tuple(x.shape)}")
        return self.head(self.conv3d(v)).squeeze(-1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--final", action="store_true", help="evaluasi data uji sekali")
    parser.add_argument("--perangkat", default="cpu laptop")
    parser.add_argument("--sesi-dir", type=str, default=None, help="Opsional: folder sesi simulasi")
    parser.add_argument("--tanpa-evaluate", action="store_true", help="Lewati penulisan metrics.json saat uji simulasi")
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    t0 = time.time()

    X_train, y_train, X_val, y_val, X_test, y_test = data.muat(args.sesi_dir)
    dim_primer = X_train.shape[1] if X_train.ndim == 2 else None

    model = VideoKipasCNN3D(fitur_primer_dim=dim_primer)
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
    for _ in range(args.epochs):
        for bx, by in train_loader:
            optimizer.zero_grad()
            loss = criterion(model(bx), by)
            loss.backward()
            optimizer.step()

    model.eval()
    with torch.no_grad():
        pred_val = model(torch.tensor(X_val, dtype=torch.float32)).numpy()
        pred_test = None
        if args.final and X_test is not None:
            pred_test = model(torch.tensor(X_test, dtype=torch.float32)).numpy()

    assert pred_val.shape == y_val.shape, f"Ukuran keluaran {pred_val.shape} != {y_val.shape}"

    durasi = time.time() - t0
    if not args.tanpa_evaluate:
        folder_output = os.path.join("results", "123450051")
        os.makedirs(folder_output, exist_ok=True)
        file_pred = os.path.join(folder_output, "pred_val.npy")
        np.save(file_pred, pred_val)

        cmd = [
            sys.executable,
            "-m",
            "src.common.evaluate",
            "--nim",
            "123450051",
            "--model",
            "cnn",
            "--seed",
            str(args.seed),
            "--pred-val",
            file_pred,
            "--durasi",
            f"{durasi:.1f}",
            "--perangkat",
            args.perangkat,
        ]
        if pred_test is not None:
            file_pred_test = os.path.join(folder_output, "pred_test.npy")
            np.save(file_pred_test, pred_test)
            cmd.extend(["--pred-test", file_pred_test])

        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
