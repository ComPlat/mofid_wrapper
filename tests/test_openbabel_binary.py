"""
Pin the bundled Open Babel engine itself, independent of the MOF pipeline.

The wrapper builds Open Babel from source with non-default flags
(WITH_JSON=OFF, an old GCC, a CMake-policy override) and then relocates the
result via patchelf + BABEL_LIBDIR. These tests check that what ended up in
the wheel is still a working chemistry engine with the plugins the pipeline
depends on -- a cheap tripwire for a mis-scoped flag or a broken/missing
plugin .so that the two end-to-end tests would only catch indirectly.
"""

import subprocess

from mofid_wrapper._paths import bin_path
from mofid_wrapper.cpp_cheminformatics import (
    ob_normalize,
    openbabel_GetSpacedFormula,
    openbabel_formula,
)

# Formats the CIF -> MOFid path relies on: CIF/mmCIF in, canonical SMILES out.
REQUIRED_FORMATS = ("cif", "mmcif", "smi", "can", "inchi")


def _obabel(*args):
    return subprocess.run(
        [str(bin_path / "obabel"), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def test_obabel_runs():
    # Exercises the relocated RPATH / core-lib load path with no input.
    out = _obabel("-V")
    assert "Open Babel" in (out.stdout + out.stderr)


def test_required_format_plugins_present():
    blob = _obabel("-L", "formats").stdout
    listed = {line.split(None, 1)[0] for line in blob.splitlines() if line.strip()}
    missing = [f for f in REQUIRED_FORMATS if f not in listed]
    assert not missing, f"bundled Open Babel is missing format plugins: {missing}"


def test_canonical_smiles_roundtrip():
    # Non-canonical input -> canonical output; proves the SMILES read/write
    # plugins and the perception code actually run, not just load.
    assert ob_normalize("OCC") == "CCO"
    assert ob_normalize("C1=CC=CC=C1") == "c1ccccc1"


def test_formula_extraction():
    assert openbabel_formula("OCC") == "C2H6O"
    assert openbabel_GetSpacedFormula("OCC") == "C 2 H 6 O"
