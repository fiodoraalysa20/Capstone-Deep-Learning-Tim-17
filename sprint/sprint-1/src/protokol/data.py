"""Pemuat data tim 17: taksiran kecepatan kipas (duty PWM, %) dari urutan 10 bingkai kamera (10 fps).

Kontrak starter: ``TUGAS`` dan ``muat() -> X_train, y_train, X_val, y_val, X_test, y_test``.

Keputusan protokol (rinciannya di PROTOKOL.md):
- Rancangan faktorial: kipas 9 taraf (0, 32, …, 255) × lampu 2 taraf × 20 ulangan = 360 kondisi × 5 s, urutan acak
  dalam satu blok. Kamera 10 fps (selang 0,1 s), ±50 bingkai per kondisi.
- Label = **duty yang diperintahkan** (rencana: "otomatis: duty PWM kipas"), dinyatakan dalam persen (duty/255·100).
- **Dua detik pertama tiap kondisi dibuang** (``BUANG_AWAL_S``): kipas butuh waktu menyesuaikan putaran. Dari uji
  beda-bingkai (reports/mutu-data.md) detik 0–1 kondisi mana pun mirip satu sama lain; detik 2–5 stabil untuk duty > 0.
- **Duty 0 sesudah duty tinggi: kipas masih berputar sisa sampai detik ke-5** (kondisi berikutnya datang sebelum kipas
  berhenti). Label tetap 0 (yang diperintahkan); klip itu ditandai ``sisa_putar`` (duty 0, kondisi sebelumnya
  ≥ ``AMBANG_SISA``) dan dilaporkan terpisah di metrik dan analisis.
- Satu contoh = klip ``N_BINGKAI`` bingkai berurutan (1 s), tidak bertumpang tindih, di detik 2–5 → 3 klip per
  kondisi. Tiap bingkai dipotong ke kipas (``POTONG``), RGB ``UKURAN`` × ``UKURAN``, ditumpuk → [30, 64, 64].
- Satuan pemisahan = **ulangan** (20; tiap ulangan memuat 18 kondisi lengkap): 4 uji, 4 validasi, 12 latih
  (``pisah.bagi_satuan``, seed 2026). Klip dari satu kondisi tidak pernah terbelah antarbagian.
- Baseline ridge starter atas 122.880 piksel tidak muat memori (``BASELINE_STARTER = False``); pembanding nol =
  penebak rata-rata latih (reports/kesalahan.md).
- Normalisasi per kanal dari data latih.
"""
from __future__ import annotations

import hashlib
import json

import numpy as np

from src.common import manifest
from src.protokol import citra, pisah, sesi
from src.protokol.kodek import KodekRegresi

TUGAS = "regresi"
KODEK: KodekRegresi | None = None
METRIK_TIM = ("val_mae", "MAE (% duty)")
BASELINE_STARTER = False          # ridge atas 30 × 64 × 64 = 122.880 fitur: matriks 122.880² tidak muat; PROTOKOL.md

SESI = "sesi-20261120-095538"
DUTY = [0, 32, 64, 96, 128, 160, 192, 224, 255]
UKURAN = 64
POTONG = (0.1, 0.15, 0.78, 1.0)       # bingkai kipas; dinding kanan dibuang
BUANG_AWAL_S = 2.0
N_BINGKAI = 10
AMBANG_SISA = 64                      # duty 0 yang kondisi sebelumnya ≥ ini = kipas masih berputar sisa
VERSI_FITUR = "t17-klip-v1"

FOLDER = manifest.AKAR / "data" / SESI
CACHE = manifest.AKAR / "data" / "cache"


def persen(duty) -> np.ndarray:
    return np.asarray(duty, np.float64) / 255 * 100


def label() -> list[dict]:
    """Label urut waktu, ditambah ``duty_sebelum`` (duty kondisi sebelumnya; −1 untuk kondisi pertama)."""
    L = sorted(sesi.baca_label(FOLDER), key=lambda b: b["t_mulai_host"])
    for i, b in enumerate(L):
        b["duty_sebelum"] = int(L[i - 1]["kipas"]) if i else -1
    return L


def _sidik() -> str:
    h = hashlib.sha256(VERSI_FITUR.encode())
    h.update((FOLDER / "label.csv").read_bytes())
    h.update((FOLDER / "kamera_index.csv").read_bytes())
    h.update(json.dumps([UKURAN, POTONG, BUANG_AWAL_S, N_BINGKAI]).encode())
    return h.hexdigest()[:16]


def contoh() -> dict:
    """Semua klip (belum dinormalisasi), di-cache. Kunci: X [N, 30, 64, 64], y (% duty), duty, lampu, ulangan,
    kondisi, duty_sebelum, sisa_putar (bool)."""
    if not FOLDER.exists():
        raise FileNotFoundError(f"data/{SESI}/ belum ada: unduh arsip sesi tim dari kartu Data meja lalu ekstrak ke "
                                "data/ (lihat data/MANIFEST.json).")
    berkas = CACHE / f"{_sidik()}.npz"
    if berkas.exists():
        with np.load(berkas) as z:
            return {k: (z[k].astype(np.float32) if k == "X" else z[k]) for k in z.files}
    kam = citra.Kamera(FOLDER)
    kol = {k: [] for k in ("X", "y", "duty", "lampu", "ulangan", "kondisi", "duty_sebelum", "sisa_putar")}
    for b in label():
        fr = [citra.baca(j, UKURAN, POTONG) for _, j in kam.bingkai(b["t_mulai_host"] + BUANG_AWAL_S, b["t_selesai_host"])]
        for i in range(0, len(fr) - N_BINGKAI + 1, N_BINGKAI):
            kol["X"].append(np.concatenate(fr[i:i + N_BINGKAI]))
            kol["y"].append(float(persen(int(b["kipas"]))))
            kol["duty"].append(int(b["kipas"])); kol["lampu"].append(int(b["lampu"]))
            kol["ulangan"].append(int(b["ulangan"])); kol["kondisi"].append(int(b["no"]))
            kol["duty_sebelum"].append(b["duty_sebelum"])
            kol["sisa_putar"].append(int(b["kipas"]) == 0 and b["duty_sebelum"] >= AMBANG_SISA)
    hasil = {k: np.asarray(v, np.float32 if k in ("X", "y") else None) for k, v in kol.items()}
    CACHE.mkdir(parents=True, exist_ok=True)
    np.savez(berkas, **{k: (v.astype(np.float16) if k == "X" else v) for k, v in hasil.items()})
    hasil["X"] = hasil["X"].astype(np.float16).astype(np.float32)
    return hasil


def bagian() -> dict:
    c = contoh()
    lat, val, uji = pisah.bagi_satuan(c["ulangan"], porsi_uji=0.2, porsi_val=0.25)
    return {"c": c, "ulangan": {"latih": lat, "val": val, "uji": uji},
            **{k: pisah.topeng(c["ulangan"], v) for k, v in (("latih", lat), ("val", val), ("uji", uji))}}


def _sisa_val(n: int) -> np.ndarray | None:
    b = bagian()
    return b["c"]["sisa_putar"][b["val"]] if int(b["val"].sum()) == n else None


def metrik_tim(y: np.ndarray, p: np.ndarray, logit: np.ndarray | None = None) -> dict:
    """MAE (% duty) keseluruhan dan per taraf duty; bila y = validasi: MAE tanpa klip kipas berputar sisa."""
    y, p = np.asarray(y, np.float64).ravel(), np.asarray(p, np.float64).ravel()
    e = np.abs(p - y)
    m = {"val_mae": round(float(e.mean()), 4),
         "val_mae_rinci": {str(d): round(float(e[np.isclose(y, persen(d))].mean()), 4)
                           for d in DUTY if np.isclose(y, persen(d)).any()}}
    s = _sisa_val(len(y))
    if s is not None:
        m.update(val_mae_tanpa_sisa=round(float(e[~s].mean()), 4),
                 val_mae_sisa_putar=round(float(e[s].mean()), 4) if s.any() else None, val_n_sisa=int(s.sum()))
    return m


def muat(standar: bool = True):
    """X [N, 30, 64, 64] float32 (10 bingkai RGB; dinormalisasi per kanal dari data latih bila ``standar``), y % duty."""
    global KODEK
    b = bagian(); c = b["c"]
    pisah.periksa_tidak_bocor(c["ulangan"][b["latih"]], c["ulangan"][b["val"]], c["ulangan"][b["uji"]])
    X, y = c["X"], c["y"].astype(np.float32)
    if standar:
        X = citra.StandarRGB(X[b["latih"]])(X)
    KODEK = KodekRegresi(y[b["latih"]].mean(), y[b["latih"]].std())
    return (X[b["latih"]], y[b["latih"]], X[b["val"]], y[b["val"]], X[b["uji"]], y[b["uji"]])
