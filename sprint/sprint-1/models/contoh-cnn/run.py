"""Jalur CNN (10 bingkai ditumpuk) (contoh kunci). Arsitektur dan hiperparameter di model.py folder ini.

    python models/contoh-cnn/run.py --seed 1 [--final]
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
import time
from pathlib import Path

import numpy as np

AKAR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AKAR))
from src.protokol import data  # noqa: E402  (protokol tim yang dibekukan)
from src.tim import latih  # noqa: E402

FOLDER = Path(__file__).resolve().parent.name
JALUR = "cnn"


def muat_model():
    spec = importlib.util.spec_from_file_location("model_jalur", Path(__file__).with_name("model.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--final", action="store_true", help="sprint terakhir: evaluasi data uji sekali")
    ap.add_argument("--perangkat", default="cpu laptop")
    a = ap.parse_args()

    latih.atur_seed(a.seed)
    t0 = time.time()
    Xtr, ytr, Xva, yva, Xte, _ = data.muat()
    kodek = getattr(data, "KODEK", None)                       # tugas multi-label (lihat src/protokol/kodek.py)
    keluaran = kodek.n_keluaran if kodek else int(ytr.max()) + 1
    dekode = kodek.dekode if kodek else (lambda z: z.argmax(1))
    jalur = muat_model()
    model, info = jalur.jalankan(Xtr, ytr, Xva, yva, Xte, seed=a.seed, latih=latih, cetak=FOLDER,
                                 keluaran=keluaran, kodek=kodek)
    logit_val = latih.prediksi(model, Xva)
    pred_val = dekode(logit_val)
    pred_test = dekode(latih.prediksi(model, Xte)) if a.final else None
    durasi = time.time() - t0
    tambahan = {"jalur": JALUR, "seed": a.seed, "hiper": jalur.HIPER, "parameter": latih.jumlah_parameter(model),
                "latensi_ms": latih.latensi_ms(model, Xva), **data.metrik_tim(yva, pred_val, logit=logit_val), **info}
    latih.tulis_hasil(FOLDER, JALUR, a.seed, pred_val, pred_test, durasi, a.perangkat, tambahan)
    np.save(AKAR / "results" / FOLDER / "logit_val.npy", logit_val)      # untuk analisis (tidak di-commit)
    np.save(AKAR / "results" / FOLDER / "logit_val.npy", logit_val)      # untuk analisis kesalahan (tidak di-commit)


if __name__ == "__main__":
    main()
