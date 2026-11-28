"""Fitur audio yang dipakai bersama semua jalur (NumPy saja, tanpa librosa/torchaudio).

``logmel(x)``: log-mel 64 pita, jendela 25 ms (400 sampel), langkah 10 ms (160 sampel), 20–8000 Hz.
``mfcc(L)``: DCT tipe II atas log-mel, 20 koefisien pertama.
Normalisasi per pita dihitung dari data latih saja (``Standar``), tidak di sini.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

SR = 16000
N_FFT = 512
WIN = 400
HOP = 160
N_MELS = 64
FMIN, FMAX = 20.0, 8000.0


def _hz_ke_mel(f):
    return 2595.0 * np.log10(1.0 + np.asarray(f) / 700.0)


def _mel_ke_hz(m):
    return 700.0 * (10 ** (np.asarray(m) / 2595.0) - 1.0)


@lru_cache(maxsize=4)
def bank_mel(sr: int = SR, n_fft: int = N_FFT, n_mels: int = N_MELS) -> np.ndarray:
    """Bank filter segitiga (HTK) berbentuk [n_mels, n_fft//2+1]."""
    titik = _mel_ke_hz(np.linspace(_hz_ke_mel(FMIN), _hz_ke_mel(min(FMAX, sr / 2)), n_mels + 2))
    frek = np.linspace(0, sr / 2, n_fft // 2 + 1)
    B = np.zeros((n_mels, len(frek)), np.float32)
    for i in range(n_mels):
        kiri, tengah, kanan = titik[i], titik[i + 1], titik[i + 2]
        naik = (frek - kiri) / (tengah - kiri)
        turun = (kanan - frek) / (kanan - tengah)
        B[i] = np.maximum(0, np.minimum(naik, turun))
    return B


def logmel(x: np.ndarray, sr: int = SR) -> np.ndarray:
    """Sinyal 1-D → log-mel [N_MELS, bingkai]. Bingkai = 1 + (len(x) - WIN) // HOP."""
    x = np.asarray(x, np.float32)
    n = 1 + (len(x) - WIN) // HOP
    idx = np.arange(WIN)[None, :] + HOP * np.arange(n)[:, None]
    bingkai = x[idx] * np.hanning(WIN).astype(np.float32)[None, :]
    spek = np.abs(np.fft.rfft(bingkai, n=N_FFT, axis=1)) ** 2          # [bingkai, n_fft/2+1]
    mel = spek @ bank_mel(sr).T                                          # [bingkai, n_mels]
    return np.log(mel + 1e-8).T.astype(np.float32)


def mfcc(L: np.ndarray, n: int = 20) -> np.ndarray:
    """log-mel [..., N_MELS, T] → MFCC [..., n, T] (DCT-II ortonormal sepanjang sumbu pita)."""
    from scipy.fft import dct
    return dct(L, type=2, axis=-2, norm="ortho")[..., :n, :]


def dbfs(x: np.ndarray) -> float:
    """Tingkat RMS dalam dBFS (0 dBFS = sinus penuh skala)."""
    r = float(np.sqrt(np.mean(np.square(x, dtype=np.float64))))
    return 20 * np.log10(max(r, 1e-10))


class Standar:
    """Rata-rata dan simpangan per pita mel dari data latih; dipakai ulang untuk validasi dan uji."""

    def __init__(self, X_latih: np.ndarray):
        # X [N, pita, T]
        self.mu = X_latih.mean(axis=(0, 2), keepdims=True)
        self.sd = X_latih.std(axis=(0, 2), keepdims=True) + 1e-6

    def __call__(self, X: np.ndarray) -> np.ndarray:
        return ((X - self.mu) / self.sd).astype(np.float32)
