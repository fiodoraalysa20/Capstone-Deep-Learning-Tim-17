"""Tes bagian protokol yang tidak bergantung data nyata (jalan di laptop mana pun)."""
import numpy as np
import pytest

from src.protokol import fitur, pisah, sesi


def test_logmel_bentuk_dan_pita_nada():
    sr = 16000
    t = np.arange(2 * sr) / sr
    L = fitur.logmel(0.5 * np.sin(2 * np.pi * 1000 * t).astype(np.float32))
    assert L.shape == (64, 198)
    pusat = fitur._mel_ke_hz(np.linspace(fitur._hz_ke_mel(20), fitur._hz_ke_mel(8000), 66))[1:-1]
    assert abs(pusat[L.mean(1).argmax()] - 1000) < 120


def test_potong_melintasi_batas_berkas_dan_turun_laju(sesi_tiruan):
    folder = sesi_tiruan([{"x": 1}, {"x": 2}, {"x": 3}], sr=48000, potong_s=7.0, nada=lambda b: 500)
    a = sesi.Audio(folder)
    assert len(a.potongan) > 3 and max(abs(c) for c in a.celah()) < 1e-3
    x = a.potong(1000 + 6.0, 1000 + 8.0)            # melintasi batas 7 s
    assert x is not None and len(x) == 32000
    assert a.potong(500, 502) is None                 # di luar rekaman


def test_pisah_per_satuan_tidak_bocor():
    satuan = np.repeat(np.arange(1, 13), 50)
    lat, val, uji = pisah.bagi_satuan(satuan, 1 / 3, 0.25)
    assert (len(lat), len(val), len(uji)) == (6, 2, 4)
    pisah.periksa_tidak_bocor(*(satuan[pisah.topeng(satuan, d)] for d in (lat, val, uji)))
    with pytest.raises(AssertionError):
        pisah.periksa_tidak_bocor(np.array([1, 2]), np.array([2, 3]))
    assert pisah.bagi_satuan(satuan, 1 / 3, 0.25) == (lat, val, uji)   # beku: sama tiap kali
