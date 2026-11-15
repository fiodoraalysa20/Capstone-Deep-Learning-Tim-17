"""Protokol pemuatan data primer meja - Tim 17.

Tugas: Regresi (% duty kipas) dari fitur gabungan sensor lingkungan, daya, dan IMU.
Split: Kronologis (split.indeks_urut) agar bebas kebocoran deret waktu.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.common import manifest, split

TUGAS = "regresi"
DATA_DIR = manifest.AKAR / "data"


def _muat_data_primer() -> tuple[np.ndarray, np.ndarray]:
    # 1. Sensor lingkungan per detik (suhu_C, lux)
    df_ling = pd.read_csv(DATA_DIR / "lingkungan.csv").sort_values("t_host")
    df_ling["detik"] = np.floor(df_ling["t_host"]).astype(np.int64)
    fitur_ling = df_ling.groupby("detik")[["suhu_C", "lux"]].mean().reset_index()

    # 2. Sensor daya per detik (mean & std bus_mV, arus_mA)
    df_daya = pd.read_csv(DATA_DIR / "daya.csv")
    df_daya["detik"] = np.floor(df_daya["t_host"]).astype(np.int64)
    fitur_daya = (
        df_daya.groupby("detik")[["bus_mV", "arus_mA"]]
        .agg(["mean", "std"])
        .fillna(0.0)
    )
    fitur_daya.columns = [f"daya_{c[0]}_{c[1]}" for c in fitur_daya.columns]
    fitur_daya = fitur_daya.reset_index()

    # 3. Sensor IMU per detik (mean & std ax, ay, az, gx, gy, gz)
    df_imu = pd.read_csv(DATA_DIR / "imu.csv")
    df_imu["detik"] = np.floor(df_imu["t_host"]).astype(np.int64)
    fitur_imu = (
        df_imu.groupby("detik")[["ax", "ay", "az", "gx", "gy", "gz"]]
        .agg(["mean", "std"])
        .fillna(0.0)
    )
    fitur_imu.columns = [f"imu_{c[0]}_{c[1]}" for c in fitur_imu.columns]
    fitur_imu = fitur_imu.reset_index()

    # Gabungkan seluruh fitur sensor berdasarkan detik
    df = (
        fitur_ling.merge(fitur_daya, on="detik", how="inner")
        .merge(fitur_imu, on="detik", how="inner")
        .sort_values("detik")
        .reset_index(drop=True)
    )

    # 4. Target regresi: % duty kipas (konversi PWM 0-255 ke 0-100%)
    df_akt = pd.read_csv(DATA_DIR / "aktuator.csv")
    df_kipas = df_akt[df_akt["nama"] == "kipas"][["t_host", "nilai"]].sort_values("t_host").copy()
    df_kipas["detik"] = np.floor(df_kipas["t_host"]).astype(np.int64)
    df_kipas["duty_persen"] = (df_kipas["nilai"].astype(np.float32) / 255.0) * 100.0

    df_gabung = pd.merge_asof(
        df,
        df_kipas[["detik", "duty_persen"]].drop_duplicates("detik", keep="last"),
        on="detik",
        direction="backward",
    )
    df_gabung["duty_persen"] = df_gabung["duty_persen"].bfill().fillna(0.0)

    kolom_fitur = [c for c in df_gabung.columns if c not in ("detik", "duty_persen")]
    X = df_gabung[kolom_fitur].to_numpy(dtype=np.float32)
    y = df_gabung["duty_persen"].to_numpy(dtype=np.float32)
    return X, y


def muat() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    X, y = _muat_data_primer()
    idx_trainval, idx_test = split.indeks_urut(len(X), porsi_val=0.15)
    X_tv, y_tv = X[idx_trainval], y[idx_trainval]
    X_test, y_test = X[idx_test], y[idx_test]

    idx_train, idx_val = split.indeks_urut(len(X_tv), porsi_val=0.15)
    return X_tv[idx_train], y_tv[idx_train], X_tv[idx_val], y_tv[idx_val], X_test, y_test
