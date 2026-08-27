# mofid_wrapper

A pip-installable wrapper around [MOFid](https://github.com/snurr-group/mofid)
(rapid identification and analysis of metal-organic frameworks). The wheel
ships precompiled Linux x86_64 binaries (Open Babel + mofid's own CLI tools),
so installing does **not** require a C/C++ compiler or building Open Babel
from source.

```bash
pip install mofid_wrapper
```

## Usage

```python
from mofid_wrapper import cif2mofid

result = cif2mofid("my_mof.cif", output_path="Output")
print(result["mofid"])
print(result["mofkey"])
```

## Requirements

- Linux, x86_64.
- A Java runtime (`java` on PATH), used for the topology step (Systre). E.g.
  `apt install default-jre-headless` on Debian/Ubuntu. This is checked lazily
  -- only raised when you actually compute topology, not on `import`.

## Scope

This wraps the parts of upstream mofid that only shell out to compiled
executables and `java`. Three upstream modules that depend on Open Babel's
SWIG Python bindings (`pybel`) -- a separate, heavier build path not produced
by this package's build -- are not included: `old_cheminformatics.py`,
`extract_metals.py`, `remove_metals.py`.

## How the binaries are built

See `ci/build_binaries.sh`. In short: a pinned upstream mofid commit is
built inside a `manylinux_2_28_x86_64` container, with a small patch
(`ci/patches/0001-babel-env-no-overwrite.patch`) applied first -- upstream's
`sbu`/`sobgrep`/`tsfm_smiles`/`compare`/`searchdb` binaries call
`setenv("BABEL_DATADIR"/"BABEL_LIBDIR", ..., 1)` with overwrite=1, which
unconditionally clobbers the environment variables this package needs to set
for the binaries to find their bundled data/plugins on someone else's
machine.

The resulting binaries + Open Babel's data/plugins + the Systre jar are
bundled as package data and shipped as a `manylinux_2_28_x86_64`-tagged
wheel.

## License

GPL-2.0-or-later, matching upstream mofid and Open Babel (both GPLv2), whose
binaries this package redistributes. See `LICENSE` and
`THIRD_PARTY_LICENSES/`.
