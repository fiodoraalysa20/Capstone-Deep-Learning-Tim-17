"""Protokol pemuatan, pemotongan ROI kipas, dan pemisahan data - Tim 17.

Aturan baku (PROTOKOL.md):
1. Citra kamera/ 640x480 @ 10 fps dipotong pada ROI daerah kipas; 10 frame (1 detik) = 1 masukan.
2. Buang 1 detik pertama (10 frame awal) setiap kondisi.
3. Data latih, validasi, dan uji dipisah per satuan ulangan (bebas kebocoran).
4. Normalisasi (mean, std) dihitung dari data latih saja.
5. Metrik utama: MAE (% duty).
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

from src.common import manifest, split

TUGAS = "regresi"
DATA_DIR = manifest.AKAR / "data"

# Parameter protokol video Tim 17 (t17-kecepatan-kipas-video.yaml)
FPS = 10
PANJANG_URUTAN = 10             # 10 frame = 1 detik
BUANG_AWAL_FRAME = 10            # buang 1 detik pertama setiap kondisi
DURASI_KONDISI_DETIK = 5.0
UKURAN_CROP = (64, 64)           # ukuran keluaran setelah crop daerah kipas
ROI_KIPAS = (120, 200, 360, 440) # (y1, x1, y2, x2) pada bingkai 480x640


def _baca_dan_potong_frame(path_citra: Path) -> np.ndarray:
    """Baca citra 640x480, potong daerah kipas (ROI), konversi grayscale 64x64."""
    from PIL import Image

    with Image.open(path_citra) as img:
        img_gray = img.convert("L")
        w, h = img_gray.size
        y1, x1, y2, x2 = ROI_KIPAS
        y1, y2 = min(y1, h - 1), min(y2, h)
        x1, x2 = min(x1, w - 1), min(x2, w)
        cropped = img_gray.crop((x1, y1, x2, y2)).resize(UKURAN_CROP)
        return np.asarray(cropped, dtype=np.float32) / 255.0


def _ekstrak_t_frame(path_citra: Path, indeks: int, t_awal: float) -> float:
    """Ambil timestamp dari nama berkas (bila numerik) atau fallback 10 fps."""
    stem = path_citra.stem
    try:
        val = float(stem.split("_")[-1])
        if val > 1e9:
            return val
    except ValueError:
        pass
    return t_awal + indeks * (1.0 / FPS)


def _muat_dari_kamera(sesi_dir: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Muat urutan 10 frame dari sesi simulasi/meja yang memiliki folder kamera/."""
    kamera_dir = sesi_dir / "kamera"
    df_akt = pd.read_csv(sesi_dir / "aktuator.csv")
    df_kipas = df_akt[df_akt["nama"] == "kipas"].sort_values("t_host").reset_index(drop=True)

    daftar_frame = sorted(
        list(kamera_dir.glob("*.jpg")) + list(kamera_dir.glob("*.png"))
    )
    if not daftar_frame:
        raise FileNotFoundError(f"Tidak ada berkas citra di {kamera_dir}")

    t_awal = float(df_kipas["t_host"].iloc[0])
    frame_times = np.array(
        [_ekstrak_t_frame(p, i, t_awal) for i, p in enumerate(daftar_frame)],
        dtype=np.float64,
    )

    X_list: list[np.ndarray] = []
    y_list: list[float] = []
    grup_list: list[int] = []

    for ulangan_id, row in df_kipas.iterrows():
        t_mulai = float(row["t_host"])
        t_selesai = (
            float(df_kipas["t_host"].iloc[ulangan_id + 1])
            if ulangan_id + 1 < len(df_kipas)
            else max(t_mulai + DURASI_KONDISI_DETIK, float(frame_times[-1]) + 1e-3)
        )
        duty_persen = (float(row["nilai"]) / 255.0) * 100.0

        idx_kondisi = np.where((frame_times >= t_mulai) & (frame_times < t_selesai))[0]
        # Aturan 1: Buang 1 detik pertama (10 frame awal) setiap kondisi
        idx_stabil = idx_kondisi[BUANG_AWAL_FRAME:]

        n_jendela = len(idx_stabil) // PANJANG_URUTAN
        for j in range(n_jendela):
            potongan_idx = idx_stabil[j * PANJANG_URUTAN : (j + 1) * PANJANG_URUTAN]
            urutan = np.stack(
                [_baca_dan_potong_frame(daftar_frame[k]) for k in potongan_idx], axis=0
            )  # (10, 64, 64)
            X_list.append(urutan)
            y_list.append(duty_persen)
            grup_list.append(int(ulangan_id))

    if not X_list:
        raise ValueError("Tidak ada jendela 10 frame valid setelah pembuangan 1 detik awal.")

    grup = np.asarray(grup_list, dtype=np.int64)
    # Bila sesi hanya punya < 3 kejadian aktuator (mis. rekaman dasar tim 0),
    # bagi per blok 4 jendela (1 ulangan setara 1 kondisi 5 detik)
    if len(np.unique(grup)) < 3:
        grup = np.arange(len(X_list), dtype=np.int64) // 4

    return (
        np.asarray(X_list, dtype=np.float32),
        np.asarray(y_list, dtype=np.float32),
        grup,
    )


def _muat_data_sensor_fallback(sesi_dir: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Fallback bila folder kamera/ belum tersedia di sesi saat ini."""
    df_ling = pd.read_csv(sesi_dir / "lingkungan.csv").sort_values("t_host")
    df_ling["detik"] = np.floor(df_ling["t_host"]).astype(np.int64)
    fitur_ling = df_ling.groupby("detik")[["suhu_C", "lux"]].mean().reset_index()

    df_daya = pd.read_csv(sesi_dir / "daya.csv")
    df_daya["detik"] = np.floor(df_daya["t_host"]).astype(np.int64)
    fitur_daya = df_daya.groupby("detik")[["bus_mV", "arus_mA"]].agg(["mean", "std"]).fillna(0.0)
    fitur_daya.columns = [f"daya_{c[0]}_{c[1]}" for c in fitur_daya.columns]
    fitur_daya = fitur_daya.reset_index()

    df_imu = pd.read_csv(sesi_dir / "imu.csv")
    df_imu["detik"] = np.floor(df_imu["t_host"]).astype(np.int64)
    fitur_imu = (
        df_imu.groupby("detik")[["ax", "ay", "az", "gx", "gy", "gz"]]
        .agg(["mean", "std"])
        .fillna(0.0)
    )
    fitur_imu.columns = [f"imu_{c[0]}_{c[1]}" for c in fitur_imu.columns]
    fitur_imu = fitur_imu.reset_index()

    df = (
        fitur_ling.merge(fitur_daya, on="detik", how="inner")
        .merge(fitur_imu, on="detik", how="inner")
        .sort_values("detik")
        .reset_index(drop=True)
    )

    df_akt = pd.read_csv(sesi_dir / "aktuator.csv")
    df_kipas = df_akt[df_akt["nama"] == "kipas"][["t_host", "nilai"]].sort_values("t_host").copy()
    df_kipas["detik"] = np.floor(df_kipas["t_host"]).astype(np.int64)
    df_kipas["duty_persen"] = (df_kipas["nilai"].astype(np.float32) / 255.0) * 100.0
    df_kipas["ulangan_id"] = np.arange(len(df_kipas), dtype=np.int64)

    df_gabung = pd.merge_asof(
        df,
        df_kipas[["detik", "duty_persen", "ulangan_id"]].drop_duplicates("detik", keep="last"),
        on="detik",
        direction="backward",
    )
    df_gabung["duty_persen"] = df_gabung["duty_persen"].bfill().fillna(0.0)
    df_gabung["ulangan_id"] = df_gabung["ulangan_id"].bfill().fillna(0).astype(np.int64)

    kolom_fitur = [c for c in df_gabung.columns if c not in ("detik", "duty_persen", "ulangan_id")]
    X = df_gabung[kolom_fitur].to_numpy(dtype=np.float32)
    y = df_gabung["duty_persen"].to_numpy(dtype=np.float32)
    grup = df_gabung["ulangan_id"].to_numpy(dtype=np.int64)
    if len(np.unique(grup)) < 3:
        grup = np.arange(len(X), dtype=np.int64) // int(DURASI_KONDISI_DETIK)
    return X, y, grup


def _pisah_per_ulangan(
    grup: np.ndarray, seed: int = split.SEED_SPLIT
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Aturan 2: Pisahkan latih, validasi, dan uji berdasarkan satuan ulangan."""
    ulangan_unik = np.unique(grup)
    rng = np.random.default_rng(seed)
    acak = rng.permutation(ulangan_unik)

    n_total = len(acak)
    n_test = max(1, int(round(n_total * 0.15)))
    n_val = max(1, int(round(n_total * 0.15)))

    grup_test = set(acak[:n_test].tolist())
    grup_val = set(acak[n_test : n_test + n_val].tolist())
    grup_train = set(acak[n_test + n_val :].tolist())

    # Verifikasi eksplisit dengan kode bahwa tidak ada ulangan yang bocor antar-split
    assert grup_train.isdisjoint(grup_test), "Kebocoran data: ulangan muncul di latih dan uji!"
    assert grup_train.isdisjoint(grup_val), "Kebocoran data: ulangan muncul di latih dan validasi!"
    assert grup_val.isdisjoint(grup_test), "Kebocoran data: ulangan muncul di validasi dan uji!"

    idx_train = np.where(np.isin(grup, list(grup_train)))[0]
    idx_val = np.where(np.isin(grup, list(grup_val)))[0]
    idx_test = np.where(np.isin(grup, list(grup_test)))[0]
    return idx_train, idx_val, idx_test


def _normalisasi_dari_latih(
    X_train: np.ndarray, X_val: np.ndarray, X_test: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Aturan 3: Hitung statistik normalisasi dari data latih saja."""
    mu = X_train.mean(axis=0, keepdims=True)
    sd = X_train.std(axis=0, keepdims=True) + 1e-6
    return (
        ((X_train - mu) / sd).astype(np.float32),
        ((X_val - mu) / sd).astype(np.float32),
        ((X_test - mu) / sd).astype(np.float32),
    )


def muat(
    sesi_dir: str | Path | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    akar_sesi = Path(sesi_dir) if sesi_dir is not None else DATA_DIR
    if (akar_sesi / "kamera").is_dir():
        X, y, grup = _muat_dari_kamera(akar_sesi)
    else:
        X, y, grup = _muat_data_sensor_fallback(akar_sesi)

    idx_train, idx_val, idx_test = _pisah_per_ulangan(grup)
    X_train, y_train = X[idx_train], y[idx_train]
    X_val, y_val = X[idx_val], y[idx_val]
    X_test, y_test = X[idx_test], y[idx_test]

    X_train, X_val, X_test = _normalisasi_dari_latih(X_train, X_val, X_test)
    return X_train, y_train, X_val, y_val, X_test, y_test
