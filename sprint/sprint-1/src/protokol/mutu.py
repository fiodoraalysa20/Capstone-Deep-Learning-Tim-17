"""Pemeriksaan mutu data tim 17 → reports/mutu-data.md + reports/mutu.json

    python -m src.protokol.mutu

Kelengkapan (kondisi, bingkai per kondisi, selang kamera), arus kipas per duty (kipas benar-benar menurut perintah),
energi beda-bingkai per duty dan per detik dalam kondisi (alasan membuang 2 detik pertama), kipas berputar sisa pada
duty 0, dan pengaruh lampu.
"""
from __future__ import annotations

import csv
import json
from collections import Counter

import numpy as np

from src.common import manifest
from src.protokol import citra, data

FASE = [(0, 1), (1, 2), (2, 3), (3, 5)]


def _f(x, d: int = 1) -> str:
    return "—" if x is None or x != x else f"{x:.{d}f}".replace(".", ",")


def _abu(jalur) -> np.ndarray:
    return citra.baca(jalur, 48, data.POTONG).mean(0)


def main() -> None:
    L = data.label()
    kam = citra.Kamera(data.FOLDER)
    h: dict = {"kondisi": len(L), "bingkai": len(kam.t)}
    sel = np.diff(kam.t)
    h["selang_median_s"] = round(float(np.median(sel)), 3); h["selang_maks_s"] = round(float(sel.max()), 3)
    log = (data.FOLDER / "log.txt").read_text(encoding="utf-8").splitlines()
    h["wifi_putus"] = sum("Wi-Fi ke ESP32 putus" in r for r in log)
    h["selesai"] = bool(log) and "Selesai" in log[-1]
    n_bingkai = [len(kam.bingkai(b["t_mulai_host"], b["t_selesai_host"])) for b in L]
    h["bingkai_per_kondisi"] = [int(min(n_bingkai)), int(np.median(n_bingkai)), int(max(n_bingkai))]
    h["rancangan"] = {f"{d}": Counter(int(b["lampu"]) for b in L if int(b["kipas"]) == d) for d in data.DUTY}
    # arus kipas (INA219 0x40) per duty, detik 1–5
    t_a, mA = [], []
    with (data.FOLDER / "daya.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                t_a.append(float(r["t_host"])); mA.append(float(r["arus_mA"]))
            except (ValueError, KeyError):
                pass
    t_a, mA = np.array(t_a), np.array(mA)
    arus = {d: [] for d in data.DUTY}
    for b in L:
        i0, i1 = np.searchsorted(t_a, [b["t_mulai_host"] + 1, b["t_selesai_host"]])
        if i1 > i0:
            arus[int(b["kipas"])].append(float(mA[i0:i1].mean()))
    h["arus_mA"] = {str(d): round(float(np.mean(v)), 1) for d, v in arus.items()}
    # energi beda-bingkai per duty × fase, duty sebelumnya (duty 0), dan lampu
    E = {(d, f): [] for d in data.DUTY for f in range(len(FASE))}
    sisa: dict[int, list[float]] = {}
    lampu: dict[tuple[int, int], list[float]] = {}
    for b in L:
        fr = kam.bingkai(b["t_mulai_host"], b["t_selesai_host"])
        if len(fr) < 2:
            continue
        G = np.stack([_abu(j) for _, j in fr]); t = np.array([x for x, _ in fr]) - b["t_mulai_host"]
        e = np.abs(np.diff(G, axis=0)).mean((1, 2)) * 1000; t = t[1:]
        d = int(b["kipas"])
        for k, (a, z) in enumerate(FASE):
            m = (t >= a) & (t < z)
            if m.any():
                E[(d, k)].append(float(e[m].mean()))
        akhir = float(e[t >= 2].mean())
        lampu.setdefault((d, int(b["lampu"])), []).append(akhir)
        if d == 0:
            sisa.setdefault(b["duty_sebelum"], []).append(akhir)
    h["energi_fase"] = {str(d): [round(float(np.mean(E[(d, k)])), 2) for k in range(len(FASE))] for d in data.DUTY}
    h["energi_duty0_menurut_sebelum"] = {str(k): round(float(np.mean(v)), 2) for k, v in sorted(sisa.items())}
    h["energi_lampu"] = {f"{d}/{la}": round(float(np.mean(v)), 2) for (d, la), v in sorted(lampu.items())}
    c = data.contoh(); bg = data.bagian()
    h["klip"] = int(len(c["y"])); h["klip_sisa_putar"] = int(c["sisa_putar"].sum())
    h["klip_duty0"] = int((c["duty"] == 0).sum())
    for n in ("latih", "val", "uji"):
        h[f"n_{n}"] = int(bg[n].sum()); h[f"sisa_{n}"] = int(c["sisa_putar"][bg[n]].sum())
        h[f"ulangan_{n}"] = bg["ulangan"][n]
    (manifest.AKAR / "reports").mkdir(exist_ok=True)
    (manifest.AKAR / "reports" / "mutu.json").write_text(json.dumps(h, indent=2, ensure_ascii=False) + "\n", "utf-8")

    ef, es = h["energi_fase"], h["energi_duty0_menurut_sebelum"]
    baris = ["# Mutu data tim 17 (sesi-20261120-095538)", "", "Dibangkitkan `python -m src.protokol.mutu`.", "",
             "## Kelengkapan", "",
             f"- {h['kondisi']} kondisi (9 duty × 2 lampu × 20 ulangan, urutan acak), sesi selesai normal: "
             f"{'ya' if h['selesai'] else 'tidak'}; Wi-Fi ESP32 putus {h['wifi_putus']}× (disambung ulang dalam ±5 s).",
             f"- {h['bingkai']} bingkai; selang median {_f(h['selang_median_s'], 3)} s, maksimum {_f(h['selang_maks_s'], 2)} s; "
             f"bingkai per kondisi {h['bingkai_per_kondisi'][0]}–{h['bingkai_per_kondisi'][2]} (median {h['bingkai_per_kondisi'][1]}).",
             f"- Klip 10 bingkai (detik 2–5): {h['klip']}; latih / validasi / uji = {h['n_latih']} / {h['n_val']} / {h['n_uji']} "
             f"(ulangan validasi {h['ulangan_val']}, uji {h['ulangan_uji']}).", "",
             "## Kipas mengikuti perintah (arus INA219 kanal kipas, detik 1–5)", "",
             "| Duty | " + " | ".join(str(d) for d in data.DUTY) + " |", "|---|" + "---|" * len(data.DUTY),
             "| arus (mA) | " + " | ".join(_f(h["arus_mA"][str(d)]) for d in data.DUTY) + " |", "",
             "## Energi beda-bingkai (×1000) per duty dan detik dalam kondisi", "",
             "| Duty | detik 0–1 | 1–2 | 2–3 | 3–5 |", "|---|---|---|---|---|",
             *[f"| {d} | " + " | ".join(_f(x) for x in ef[str(d)]) + " |" for d in data.DUTY], "",
             "## Duty 0: energi detik 2–5 menurut duty kondisi sebelumnya", "",
             "| Duty sebelumnya | " + " | ".join(es) + " |", "|---|" + "---|" * len(es),
             "| energi (×1000) | " + " | ".join(_f(v) for v in es.values()) + " |", "",
             "## Temuan", "",
             f"- **Kipas menurut perintah**: arus naik hampir sebanding duty (0 → {_f(h['arus_mA']['255'])} mA). Label duty sah.",
             f"- **Beda-bingkai turun saat duty naik** (detik 2–5: duty 32 = {_f(ef['32'][3])}, duty 255 = {_f(ef['255'][3])}). "
             "Pada 10 fps bilah yang berputar cepat kabur merata sehingga bingkai berurutan mirip; bilah lambat bergeser "
             "nyata antarbingkai. Energi beda-bingkai tidak naik bersama kecepatan.",
             f"- **Taraf tinggi sulit dibedakan**: duty 160–255 energinya {_f(min(ef[str(d)][3] for d in (160, 192, 224, 255)))}–"
             f"{_f(max(ef[str(d)][3] for d in (160, 192, 224, 255)))}, hampir sama.",
             f"- **Detik 0–1 mirip untuk semua duty** ({_f(min(v[0] for v in ef.values()))}–{_f(max(v[0] for v in ef.values()))}): "
             "kipas sedang berubah putaran. Dua detik pertama dibuang.",
             f"- **Duty 0 sesudah duty ≥ {data.AMBANG_SISA}: kipas masih berputar sisa** (energi detik 2–5 sampai "
             f"{_f(max(es.values()))} vs {_f(es.get('0'))} bila sebelumnya juga 0). Kondisi 5 s terlalu pendek untuk kipas "
             f"berhenti. {h['klip_sisa_putar']} klip (val {h['sisa_val']}, uji {h['sisa_uji']}) berlabel 0 % padahal kipas "
             "berputar; dilaporkan terpisah (`val_mae_tanpa_sisa`).",
             f"- **Duty 0 hampir selalu berarti 'sedang melambat'**: {h['klip_sisa_putar']} dari {h['klip_duty0']} klip duty 0. "
             "Hanya kondisi yang didahului duty 0 atau 32 menampilkan kipas diam.",
             "- **Lampu** (ruang sudah terang, sesi pukul 09.55–10.28) menggeser energi terutama pada duty rendah, tidak "
             "searah di semua taraf; dijaga seimbang di tiap bagian karena tiap ulangan memuat kedua taraf lampu:", "",
             "| Lampu | " + " | ".join(str(d) for d in data.DUTY) + " |", "|---|" + "---|" * len(data.DUTY),
             *[f"| {'mati' if la == 0 else 'nyala'} | " + " | ".join(_f(h['energi_lampu'][f'{d}/{la}']) for d in data.DUTY) + " |"
               for la in (0, 255)], ""]
    (manifest.AKAR / "reports" / "mutu-data.md").write_text("\n".join(baris), encoding="utf-8")
    print(json.dumps({k: v for k, v in h.items() if k not in ("rancangan",)}, ensure_ascii=False)[:900])


if __name__ == "__main__":
    main()
