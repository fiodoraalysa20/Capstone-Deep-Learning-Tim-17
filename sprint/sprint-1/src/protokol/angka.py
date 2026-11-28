"""Kumpulkan angka laporan → reports/angka.json.

    python -m src.protokol.angka
"""
from __future__ import annotations

import json

from src.common import manifest
from src.protokol import data

KODE = {"rata-rata": "RATA", "contoh-cnn": "CNN", "contoh-tl": "TL", "contoh-rnn": "RNN", "contoh-ae": "AE",
        "non-dl": "NONDL"}


def _f(x, d: int = 1) -> str:
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def main() -> None:
    akar = manifest.AKAR
    a: dict = {}
    mutu = json.loads((akar / "reports" / "mutu.json").read_text("utf-8"))
    for k in ("kondisi", "bingkai", "klip", "klip_sisa_putar", "n_latih", "n_val", "n_uji", "sisa_val", "sisa_uji", "wifi_putus"):
        a[f"MUTU_{k}"] = mutu[k]
    a["ULANGAN_VAL"] = ", ".join(map(str, mutu["ulangan_val"])); a["ULANGAN_UJI"] = ", ".join(map(str, mutu["ulangan_uji"]))
    a["ARUS_255"] = _f(mutu["arus_mA"]["255"]); a["ARUS_32"] = _f(mutu["arus_mA"]["32"])
    for d in (32, 128, 255):
        a[f"E{d}"] = _f(mutu["energi_fase"][str(d)][3])
    a["E0_DIAM"] = _f(mutu["energi_duty0_menurut_sebelum"].get("0"))
    a["E0_SISA_MAKS"] = _f(max(mutu["energi_duty0_menurut_sebelum"].values()))
    kes = json.loads((akar / "reports" / "kesalahan.json").read_text("utf-8")) if (akar / "reports" / "kesalahan.json").exists() else {}
    for nama, r in kes.items():
        k = KODE.get(nama, nama.upper())
        a[f"{k}_MAE"] = _f(r["val_mae"]); a[f"{k}_TANPA"] = _f(r["val_mae_tanpa_sisa"]); a[f"{k}_SISA"] = _f(r["val_mae_sisa_putar"])
        for d in data.DUTY:
            a[f"{k}_D{d}"] = _f(r["val_mae_rinci"].get(str(d)))
            a[f"{k}_P{d}"] = _f(r["pred_rata_per_duty"][str(d)])
    for d in sorted((akar / "results").iterdir()):
        if not (d / "metrics.json").exists():
            continue
        m = json.loads((d / "metrics.json").read_text("utf-8"))
        t = json.loads((d / "tambahan.json").read_text("utf-8")) if (d / "tambahan.json").exists() else {}
        k = KODE.get(d.name, d.name.upper())
        a[f"{k}_DURASI"] = f"{m.get('durasi_detik', 0):.0f}"; a["DATA_HASH"] = m["data_hash"]
        if "parameter" in t:
            a[f"{k}_PARAM"] = f"{t['parameter']:,}".replace(",", ".")
        if "latensi_ms" in t:
            a[f"{k}_LATENSI"] = _f(t["latensi_ms"], 1)
        if "epoch_terbaik" in t:
            a[f"{k}_EPOCH"] = t["epoch_terbaik"]
        if k == "NONDL":
            a["NONDL_PILIH"] = t["dipilih"]
            a["NONDL_ENERGI_MAE"] = _f(t["calon"]["energi"]["val_mae"]); a["NONDL_F4_MAE"] = _f(t["calon"]["fitur4"]["val_mae"])
    (akar / "reports" / "angka.json").write_text(json.dumps(a, indent=2, ensure_ascii=False) + "\n", "utf-8")
    print(f"{len(a)} angka → reports/angka.json")


if __name__ == "__main__":
    main()
