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


class SensorCNN1D(nn.Module):
    def __init__(self, n_fitur: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(1, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv1d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(4),
            nn.Flatten(),
            nn.Linear(32 * 4, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x).squeeze(-1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--lr", type=float, default=1e-3)
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    t0 = time.time()

    X_train, y_train, X_val, y_val, _, _ = data.muat()

    mu = X_train.mean(axis=0, keepdims=True)
    sd = X_train.std(axis=0, keepdims=True) + 1e-6
    X_train_norm = ((X_train - mu) / sd)[:, None, :]
    X_val_norm = ((X_val - mu) / sd)[:, None, :]

    train_ds = TensorDataset(
        torch.tensor(X_train_norm, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.float32),
    )
    train_loader = DataLoader(train_ds, batch_size=16, shuffle=True)

    model = SensorCNN1D(n_fitur=X_train.shape[1])
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
        pred_val = model(torch.tensor(X_val_norm, dtype=torch.float32)).numpy()

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
