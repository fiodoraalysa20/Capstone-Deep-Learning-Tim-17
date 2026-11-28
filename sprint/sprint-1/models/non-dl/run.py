"""Pembanding non-deep learning tim 17 (rencana tim): energi beda-bingkai + regresi linear.

    python models/non-dl/run.py --seed 1 [--final]

Per klip 10 bingkai (abu-abu, belum dinormalisasi): ``energi`` = rata-rata |bingkai t − bingkai t−1| atas 9 pasang,
``temporal`` = rata-rata simpangan baku tiap piksel atas waktu, ``tekstur`` = simpangan baku spasial (bilah kabur →
kecil). Dua calon regresi linear (kuadrat terkecil), dipilih dengan MAE validasi; keduanya di tambahan.json:
- ``energi``: duty ~ energi (rencana tim apa adanya);
- ``fitur4``: duty ~ energi, log energi, temporal, tekstur.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

AKAR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AKAR))
from src.protokol import data  # noqa: E402
from src.tim import latih  # noqa: E402

FOLDER = Path(__file__).resolve().parent.name
CALON = {"energi": ["energi"], "fitur4": ["energi", "log_energi", "temporal", "tekstur"]}


def fitur(X: np.ndarray) -> dict[str, np.ndarray]:
    N = len(X)
    G = X.reshape(N, data.N_BINGKAI, 3, *X.shape[2:]).mean(2)            # [N, T, H, W] abu-abu
    e = np.abs(np.diff(G, axis=1)).mean((1, 2, 3))
    return {"energi": e, "log_energi": np.log(e + 1e-4), "temporal": G.std(1).mean((1, 2)),
            "tekstur": G.std((2, 3)).mean(1)}


def _desain(F: dict, nama: list[str]) -> np.ndarray:
    return np.column_stack([np.ones(len(F[nama[0]]))] + [F[n] for n in nama])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--perangkat", default="cpu laptop")
    a = ap.parse_args()
    t0 = time.time()
    Xtr, ytr, Xva, yva, Xte, _ = data.muat(standar=False)
    Ftr, Fva, Fte = fitur(Xtr), fitur(Xva), fitur(Xte)
    koef, skor = {}, {}
    for nama, kol in CALON.items():
        w, *_ = np.linalg.lstsq(_desain(Ftr, kol), ytr.astype(np.float64), rcond=None)
        koef[nama] = w
        skor[nama] = data.metrik_tim(yva, np.clip(_desain(Fva, kol) @ w, 0, 100))
    pilih = min(skor, key=lambda k: skor[k]["val_mae"])
    w = koef[pilih]
    pred_val = np.clip(_desain(Fva, CALON[pilih]) @ w, 0, 100).astype(np.float32)
    pred_test = np.clip(_desain(Fte, CALON[pilih]) @ w, 0, 100).astype(np.float32) if a.final else None
    rata = {d: round(float(Ftr["energi"][np.isclose(ytr, data.persen(d))].mean()), 5) for d in data.DUTY}
    tambahan = {"jalur": "non-dl", "seed": a.seed, "dipilih": pilih, "calon": skor,
                "koefisien": {k: [round(float(x), 4) for x in v] for k, v in koef.items()},
                "energi_rata_latih_per_duty": rata, **data.metrik_tim(yva, pred_val)}
    latih.tulis_hasil(FOLDER, f"non-dl-{pilih}", a.seed, pred_val, pred_test, time.time() - t0, a.perangkat, tambahan)


if __name__ == "__main__":
    main()
