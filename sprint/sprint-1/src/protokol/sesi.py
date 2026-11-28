"""Membaca satu folder sesi Meja 5 Volt (keluaran ``meja.py jalankan``).

Isi folder sesi yang dipakai di sini::

    label.csv          satu baris per kondisi: faktor rencana + t_mulai_host, t_selesai_host (detik epoch)
    audio_index.csv    berkas, t_mulai_host, sample_rate, jumlah_sampel (satu baris per potongan WAV)
    audio/*.wav        rekaman bersambung, dipotong per 60 detik
    daya.csv, imu.csv, aktuator.csv, lingkungan.csv   sensor ESP32 (t_host = jam komputer meja)
    manifest.json      sha256 tiap berkas (ditulis saat sesi ditutup)

Semua waktu memakai jam komputer meja (``t_host``), sehingga label dan audio dapat dipotong
tanpa menebak. Sejak perekam 1.7 audio disimpan pada laju asli mikrofon (48 kHz); ``Audio.potong``
menurunkan ke laju yang diminta.
"""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from math import gcd
from pathlib import Path


def baca_label(folder: Path) -> list[dict]:
    """Baris label.csv; t_mulai_host/t_selesai_host menjadi float."""
    with (Path(folder) / "label.csv").open(encoding="utf-8") as f:
        baris = list(csv.DictReader(f))
    for b in baris:
        b["t_mulai_host"] = float(b["t_mulai_host"])
        b["t_selesai_host"] = float(b["t_selesai_host"])
    return baris


def baca_csv(folder: Path, nama: str) -> list[dict]:
    p = Path(folder) / nama
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def periksa_manifest(folder: Path, hanya: tuple[str, ...] = ()) -> list[str]:
    """Bandingkan sha256 berkas dengan manifest.json sesi. Kembalikan daftar berkas yang beda/hilang."""
    folder = Path(folder)
    m = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))["berkas"]
    masalah = []
    for nama, info in m.items():
        if nama == "log.txt" or (hanya and not nama.startswith(hanya)):
            continue
        p = folder / nama
        if not p.exists():
            masalah.append(f"hilang: {nama}")
            continue
        h = hashlib.sha256()
        with p.open("rb") as f:
            for blok in iter(lambda: f.read(1 << 20), b""):
                h.update(blok)
        if h.hexdigest() != info["sha256"]:
            masalah.append(f"beda: {nama}")
    return masalah


@dataclass
class Potongan:
    berkas: Path
    t0: float
    sr: float          # laju sampel yang dipakai untuk memetakan waktu (efektif bila ``Audio(kontinu=True)``)
    n: int

    @property
    def t1(self) -> float:
        return self.t0 + self.n / self.sr


class Audio:
    """Rekaman bersambung satu sesi; potong berdasarkan jam komputer meja.

    ``kontinu=True`` (rekaman web): potongan dianggap SATU aliran bersambung dan waktunya dipetakan dengan laju sampel
    efektif hasil regresi linear awal potongan terhadap jumlah sampel kumulatif. Dipakai bila jam sampel mikrofon
    laptop tidak tepat 48 kHz: penanda waktu tiap potongan lalu tampak "bercelah" padahal gelombangnya bersambung."""

    def __init__(self, folder: Path, kontinu: bool = False):
        folder = Path(folder)
        self.potongan = [Potongan(folder / "audio" / b["berkas"], float(b["t_mulai_host"]), int(b["sample_rate"]),
                                  int(b["jumlah_sampel"]))
                         for b in baca_csv(folder, "audio_index.csv")]
        self.potongan.sort(key=lambda p: p.t0)
        self.laju_efektif = None
        if kontinu and len(self.potongan) > 2:
            import numpy as np
            kum = np.r_[0, np.cumsum([p.n for p in self.potongan])[:-1]].astype(float)
            t0 = np.array([p.t0 for p in self.potongan])
            b, a = np.polyfit(kum, t0, 1)
            self.laju_efektif = float(1 / b)
            for p, k in zip(self.potongan, kum):
                p.t0, p.sr = float(a + b * k), self.laju_efektif

    def celah(self) -> list[float]:
        """Selisih (detik) antara akhir satu potongan dan awal potongan berikutnya (positif = celah)."""
        return [b.t0 - a.t1 for a, b in zip(self.potongan, self.potongan[1:])]

    def potong(self, t_awal: float, t_akhir: float, sr: int = 16000) -> np.ndarray | None:
        """Sinyal float32 [-1, 1] antara dua waktu host, diturunkan ke ``sr``. None bila tidak tertutup audio."""
        import numpy as np
        import soundfile as sf

        bagian, t = [], t_awal
        for p in self.potongan:
            if p.t1 <= t or p.t0 >= t_akhir:
                continue
            if p.t0 - t > 0.05:            # celah > 50 ms di tengah jendela: jendela ditolak
                return None
            a = max(0, int(round((t - p.t0) * p.sr)))
            b = min(p.n, int(round((t_akhir - p.t0) * p.sr)))
            x, sr_asli = sf.read(p.berkas, start=a, stop=b, dtype="float32", always_2d=True)
            x = x.mean(axis=1)
            if sr_asli != sr:
                from scipy.signal import resample_poly
                g = gcd(sr, sr_asli)
                x = resample_poly(x, sr // g, sr_asli // g).astype(np.float32)
            if abs(p.sr - sr_asli) > 1:                   # laju efektif ≠ header: regangkan ke laju sebenarnya
                m = int(round(len(x) * sr_asli / p.sr))
                x = np.interp(np.linspace(0, len(x) - 1, m), np.arange(len(x)), x).astype(np.float32)
            bagian.append(x)
            t = p.t0 + b / p.sr
            if t >= t_akhir - 1e-3:
                break
        if not bagian or t < t_akhir - 0.05:
            return None
        x = np.concatenate(bagian)
        n = int(round((t_akhir - t_awal) * sr))
        return np.pad(x, (0, max(0, n - len(x))))[:n]


def lampu_terbalik(label: list[dict]) -> bool | None:
    """Apakah perintah lampu di sesi ini tercatat terbalik (salah program perekam/relai: perintah 255 memadamkan
    bohlam)? Diputuskan dari data, bukan diasumsikan: lux BH1750 di ``label.csv`` (median per kondisi, tanpa nilai basi)
    lebih rendah saat perintah lampu > 0 → terbalik. None bila sesi tanpa faktor lampu atau tanpa lux."""
    urut = sorted((b for b in label if "lampu" in b and b.get("lux") not in (None, "")), key=lambda b: int(b["no"]))
    lux = [float(b["lux"]) for b in urut]
    # lux basi: nilai yang sama persis ≥ 3 kondisi berturut-turut (Wi-Fi ESP32 putus, sensor tidak diperbarui) diabaikan
    basi = set()
    i = 0
    while i < len(lux):
        j = i
        while j + 1 < len(lux) and lux[j + 1] == lux[i]:
            j += 1
        if j - i >= 2:
            basi.update(range(i, j + 1))
        i = j + 1
    nyala = [x for k, (b, x) in enumerate(zip(urut, lux)) if k not in basi and float(b["lampu"]) > 0]
    mati = [x for k, (b, x) in enumerate(zip(urut, lux)) if k not in basi and float(b["lampu"]) == 0]
    if not nyala or not mati:
        return None
    from statistics import median
    return median(nyala) < median(mati)


def koreksi_lampu(label: list[dict]) -> tuple[list[dict], bool | None]:
    """Praproses: bila ``lampu_terbalik``, kolom ``lampu`` diganti keadaan FISIK (0 ↔ 255) dan nilai aslinya disimpan
    di ``lampu_perintah`` (dipakai untuk mencocokkan aktuator.csv, yang mencatat perintah). Label lain tidak berubah."""
    terbalik = lampu_terbalik(label)
    keluar = []
    for b in label:
        b = dict(b)
        if "lampu" in b:
            b["lampu_perintah"] = b["lampu"]
            if terbalik:
                b["lampu"] = "0" if float(b["lampu"]) > 0 else "255"
        keluar.append(b)
    return keluar, terbalik
