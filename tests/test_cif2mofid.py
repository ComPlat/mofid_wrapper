"""
End-to-end test of the full pipeline: sbu -> OpenBabel plugins -> Java/Systre.

Mirrors upstream mofid's tests/check_run_mofid.py, run against the actual
installed wheel (never against the source tree), which is the point --
this exercises exactly the paths/env-vars/relocation that are fragile.
"""

import os

from mofid_wrapper import cif2mofid

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def test_irmof1(tmp_path):
    cif_path = os.path.join(DATA_DIR, "P1-IRMOF-1.cif")
    result = cif2mofid(cif_path, output_path=str(tmp_path))
    assert result["mofkey"].startswith("Zn.KKEYFWRCBNTPAC.MOFkey-v1")
    assert "MOFid-v1" in result["mofid"]


def test_cu_btc(tmp_path):
    cif_path = os.path.join(DATA_DIR, "P1-Cu-BTC.cif")
    result = cif2mofid(cif_path, output_path=str(tmp_path))
    assert result["mofkey"].startswith("Cu.QMKYBPDZANOJGF.MOFkey-v1")
    assert "[O-]C(=O)c1cc(cc(c1)C(=O)[O-])C(=O)[O-]" in result["smiles_linkers"]
