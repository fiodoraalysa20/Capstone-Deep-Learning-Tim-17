"""Tes protokol tim 17: persen duty, metrik per taraf, pemisahan per ulangan, uji target acak (data meja bila ada)."""
import numpy as np
import pytest

from src.protokol import data


def test_persen_duty():
    assert data.persen(255) == pytest.approx(100.0) and data.persen(0) == 0.0


def test_metrik_per_taraf():
    y = data.persen([0, 0, 255, 255]); p = y + np.array([10, 0, -20, 0])
    m = data.metrik_tim(y, p)
    assert m["val_mae"] == pytest.approx(7.5) and m["val_mae_rinci"]["0"] == 5.0 and m["val_mae_rinci"]["255"] == 10.0


nyata = pytest.mark.skipif(not data.FOLDER.exists(), reason="data belum ada")


@nyata
def test_ulangan_terpisah_dan_seimbang():
    Xtr, ytr, Xva, yva, Xte, yte = data.muat()
    b = data.bagian(); c = b["c"]
    assert not set(c["ulangan"][b["latih"]]) & set(c["ulangan"][b["val"]].tolist() + c["ulangan"][b["uji"]].tolist())
    assert Xtr.shape[1:] == (3 * data.N_BINGKAI, data.UKURAN, data.UKURAN)
    for m in (b["latih"], b["val"], b["uji"]):         # tiap ulangan memuat 18 kondisi → semua taraf duty seimbang
        kondisi = {(int(k), int(d)) for k, d in zip(c["kondisi"][m], c["duty"][m])}
        n = np.unique([d for _, d in kondisi], return_counts=True)[1]
        assert len(n) == len(data.DUTY) and n.min() == n.max()
    assert np.bincount(np.unique(c["kondisi"], return_counts=True)[1]).nonzero()[0].min() >= 2   # ≥ 2 klip per kondisi
    # klip sisa putar hanya duty 0
    assert (c["duty"][c["sisa_putar"]] == 0).all()


@nyata
def test_target_acak_tidak_lebih_baik_dari_rata_rata():
    from sklearn.ensemble import RandomForestRegressor

    b = data.bagian(); c = b["c"]
    F = c["X"][:, :, ::8, ::8].reshape(len(c["X"]), -1)
    ytr = c["y"][b["latih"]][np.random.default_rng(0).permutation(int(b["latih"].sum()))]
    m = RandomForestRegressor(100, random_state=0, n_jobs=1).fit(F[b["latih"]], ytr)
    yva = c["y"][b["val"]]
    acak = np.abs(m.predict(F[b["val"]]) - yva).mean()
    rata = np.abs(c["y"][b["latih"]].mean() - yva).mean()
    assert acak > 0.8 * rata, f"MAE target acak {acak:.1f} terlalu rendah dibanding rata-rata {rata:.1f}"
