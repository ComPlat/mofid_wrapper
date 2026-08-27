"""Runtime paths to the bundled binaries/data, computed relative to this package.

Replaces upstream mofid's set_paths.py + generated Python/paths.py, which baked
absolute build-machine paths into a file on disk -- incompatible with a
relocatable pip package. Also sets BABEL_DATADIR/BABEL_LIBDIR once here, since
every ported module transitively imports this one.
"""

import os
import stat
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parent
_VENDOR = _PKG_ROOT / "_vendor"

bin_path = _VENDOR / "bin"
lib_path = _VENDOR / "lib"  # core libopenbabel.so*/libinchi.so*, resolved via RPATH
plugin_path = _VENDOR / "lib" / "plugins"  # dlopen()'d by OpenBabel via BABEL_LIBDIR
openbabel_data_path = _VENDOR / "share" / "openbabel_data"
resources_path = _VENDOR / "share" / "resources"

_REQUIRED_DIRS = (bin_path, lib_path, plugin_path, openbabel_data_path, resources_path)
_EXECUTABLES = ("sbu", "sobgrep", "searchdb", "tsfm_smiles", "compare", "obabel")


def _check_installed():
    missing = [str(p) for p in _REQUIRED_DIRS if not p.is_dir()]
    if missing:
        raise RuntimeError(
            "mofid_wrapper appears to be installed incorrectly -- missing "
            f"bundled runtime directories: {missing}. mofid_wrapper only "
            "ships prebuilt binaries for Linux x86_64 via its PyPI wheel; "
            "installing from an sdist or on an unsupported platform will "
            "not work."
        )


def _ensure_executable(path):
    if not path.exists():
        return
    mode = path.stat().st_mode
    if not mode & stat.S_IXUSR:
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


_check_installed()
for _name in _EXECUTABLES:
    _ensure_executable(bin_path / _name)

os.environ["BABEL_DATADIR"] = str(openbabel_data_path)
os.environ["BABEL_LIBDIR"] = str(plugin_path)
