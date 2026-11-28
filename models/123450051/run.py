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
    """Arsitektur Spatio-Temporal 3D-CNN untuk jalur CNN Video (urutan 10 frame 64x64)."""

    def __init__(self, fitur_primer_dim: int | None = None):
        super().__init__()
        # Proyeksi fitur primer 1-detik ke representasi spatio-temporal (1, 10, 64, 64)
        # apabila sesi primer meja belum menyertakan folder kamera/
        self.proyeksi_primer = (
            nn.Linear(fitur_primer_dim, 10 * 16 * 16)
            if fitur_primer_dim is not None
            else None
        )

        # Inti model CNN Video: konvolusi 3D (temporal T=10 x spasial H x W)
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
            # Masukan langsung urutan video (B, T=10, H=64, W=64) -> (B, 1, 10, 64, 64)
            v = x.unsqueeze(1)
        elif x.ndim == 2 and self.proyeksi_primer is not None:
            # Adaptasi data primer meja saat kamera/ belum tersedia -> (B, 1, 10, 16, 16)
            v = self.proyeksi_primer(x).view(x.size(0), 1, 10, 16, 16)
        else:
            raise ValueError(f"Bentuk masukan tidak didukung untuk CNN Video: {tuple(x.shape)}")
        return self.head(self.conv3d(v)).squeeze(-1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-3)
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    t0 = time.time()

    X_train, y_train, X_val, y_val, _, _ = data.muat()
    dim_primer = X_train.shape[1] if X_train.ndim == 2 else None

    train_loader = DataLoader(
        TensorDataset(
            torch.tensor(X_train, dtype=torch.float32),
            torch.tensor(y_train, dtype=torch.float32),
        ),
        batch_size=args.batch_size,
        shuffle=True,
    )

    model = VideoKipasCNN3D(fitur_primer_dim=dim_primer)
    criterion = nn.L1Loss()  # Metrik utama MAE (% duty)
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

    durasi = time.time() - t0
    folder_output = os.path.join("results", "123450051")
    os.makedirs(folder_output, exist_ok=True)
    file_pred = os.path.join(folder_output, "pred_val.npy")
    np.save(file_pred, pred_val)

    subprocess.run(
        [
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
            "cpu laptop",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
