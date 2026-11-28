"""Analisis validasi → reports/kesalahan.md + reports/kesalahan.json

    python -m src.protokol.analisis

Per model: MAE (% duty) keseluruhan, tanpa klip berputar sisa, per taraf duty, per lampu; pembanding nol: penebak
rata-rata latih.
"""
from __future__ import annotations

import json

import numpy as np

from src.common import manifest
from src.protokol import data

NAMA = {"rata-rata": "penebak rata-rata", "contoh-cnn": "CNN", "contoh-tl": "TL", "contoh-rnn": "RNN (CNN-LSTM)",
        "contoh-ae": "AE", "non-dl": "non-DL"}


def _f(x, d: int = 1) -> str:
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def main() -> None:
    akar = manifest.AKAR
    b = data.bagian(); c = b["c"]
    y = c["y"][b["val"]].astype(np.float64); lampu = c["lampu"][b["val"]]
    pred = {"rata-rata": np.full_like(y, c["y"][b["latih"]].mean())}
    for d in sorted((akar / "results").iterdir()):
        if (d / "pred_val.npy").exists():
            pred[d.name] = np.load(d / "pred_val.npy").reshape(-1).astype(np.float64)
    hasil = {}
    for nama, p in pred.items():
        e = np.abs(p - y)
        hasil[nama] = {**data.metrik_tim(y, p), **{f"mae_lampu_{la}": round(float(e[lampu == la].mean()), 4) for la in (0, 255)},
                       "pred_rata_per_duty": {str(d): round(float(p[np.isclose(y, data.persen(d))].mean()), 2) for d in data.DUTY}}
    kol = list(hasil)
    baris = ["# Analisis validasi (seed 1)", "",
             f"Validasi = ulangan {b['ulangan']['val']} ({len(y)} klip; {int(c['sisa_putar'][b['val']].sum())} klip duty 0 "
             "dengan kipas masih berputar sisa). Galat dalam % duty.", "",
             "| Ukuran | " + " | ".join(NAMA.get(k, k) for k in kol) + " |", "|---|" + "---|" * len(kol),
             "| **MAE** | " + " | ".join(f"**{_f(hasil[k]['val_mae'])}**" for k in kol) + " |",
             "| MAE tanpa sisa putar | " + " | ".join(_f(hasil[k]["val_mae_tanpa_sisa"]) for k in kol) + " |",
             "| MAE klip sisa putar | " + " | ".join(_f(hasil[k]["val_mae_sisa_putar"]) for k in kol) + " |"]
    for d in data.DUTY:
        baris.append(f"| MAE duty {d} ({_f(data.persen(d)[()], 0)} %) | "
                     + " | ".join(_f(hasil[k]["val_mae_rinci"].get(str(d))) for k in kol) + " |")
    baris += ["| MAE lampu mati | " + " | ".join(_f(hasil[k]["mae_lampu_0"]) for k in kol) + " |",
              "| MAE lampu nyala | " + " | ".join(_f(hasil[k]["mae_lampu_255"]) for k in kol) + " |", "",
              "## Rata-rata taksiran per duty (% duty)", "",
              "| Duty (target %) | " + " | ".join(NAMA.get(k, k) for k in kol) + " |", "|---|" + "---|" * len(kol),
              *[f"| {d} ({_f(data.persen(d)[()], 0)}) | " + " | ".join(_f(hasil[k]["pred_rata_per_duty"][str(d)]) for k in kol) + " |"
                for d in data.DUTY], ""]
    (akar / "reports" / "kesalahan.md").write_text("\n".join(baris), encoding="utf-8")
    (akar / "reports" / "kesalahan.json").write_text(json.dumps(hasil, indent=2, ensure_ascii=False) + "\n", "utf-8")
    print(f"{len(kol)} kolom → reports/kesalahan.md")


if __name__ == "__main__":
    main()
