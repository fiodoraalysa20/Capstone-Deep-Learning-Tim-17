import csv
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def tulis_sesi(folder: Path, kondisi: list[dict], sr: int = 16000, t0: float = 1000.0, potong_s: float = 60.0,
               nada: dict | None = None) -> Path:
    """Folder sesi tiruan: label.csv + audio bersambung (dipotong per ``potong_s``) + audio_index.csv.

    ``kondisi``: baris faktor; tiap kondisi 20 s diikuti jeda 2 s. ``nada(baris) -> Hz`` mengisi audio.
    """
    import soundfile as sf

    (folder / "audio").mkdir(parents=True)
    rng = np.random.default_rng(0)
    t, label, sinyal = t0, [], []
    for i, b in enumerate(kondisi, 1):
        f = nada(b) if nada else 0
        n = int(20 * sr)
        x = 0.01 * rng.standard_normal(n)
        if f:
            x += 0.3 * np.sin(2 * np.pi * f * np.arange(n) / sr)
        sinyal += [x, 0.01 * rng.standard_normal(int(2 * sr))]
        label.append({"no": i, "ulangan_blok": 1, "blok": 1, **b, "t_mulai_host": f"{t:.4f}",
                      "t_selesai_host": f"{t + 20:.4f}"})
        t += 22
    x = np.concatenate(sinyal).astype(np.float32)
    with (folder / "label.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(label[0]))
        w.writeheader(); w.writerows(label)
    with (folder / "audio_index.csv").open("w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["berkas", "t_mulai_host", "sample_rate", "jumlah_sampel"])
        per = int(potong_s * sr)
        for k, a in enumerate(range(0, len(x), per), 1):
            nama = f"audio-{k:04d}.wav"
            sf.write(folder / "audio" / nama, x[a:a + per], sr, subtype="PCM_16")
            w.writerow([nama, f"{t0 + a / sr:.4f}", sr, len(x[a:a + per])])
    return folder


@pytest.fixture
def sesi_tiruan(tmp_path):
    return lambda kondisi, **kw: tulis_sesi(tmp_path / "sesi-tiruan", kondisi, **kw)
