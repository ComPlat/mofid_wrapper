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

The resulting binaries + Open Babel's data/plugins + the InChI shared library
+ the Systre jar + the RCSR net archive are bundled as package data and
shipped as a `manylinux_2_28_x86_64`-tagged wheel.

## License

`mofid_wrapper`'s own code is **GPL-2.0-or-later**. See `LICENSE`.

The wheel redistributes precompiled binaries and data files that are the work
of others. `NOTICE` (repo root, also installed with the package) lists every
bundled component with its license and a pointer to its corresponding source;
full license texts are in `THIRD_PARTY_LICENSES/`:

| Component | Bundled as | License |
|---|---|---|
| [MOFid](https://github.com/snurr-group/mofid) | `sbu`, `sobgrep`, `searchdb`, `tsfm_smiles`, `compare` | GPL-2.0-or-later |
| [Open Babel](https://github.com/openbabel/openbabel) | `obabel`, `libopenbabel.so*`, format plugins, data | GPL-2.0-or-later |
| [InChI](https://github.com/IUPAC-InChI/InChI) library (v1.04) | `libinchi.so*` (via Open Babel's inchiformat plugin) | IUPAC/InChI-Trust InChI Licence No. 1.0 |
| [Systre / Gavrog](https://github.com/odf/gavrog) | `Systre-experimental-20.8.0.jar` | Apache-2.0 |
| [RCSR](http://rcsr.net/) net archive | `RCSRnets.arc` | factual database, free for research w/ citation |

The copyleft components (MOFid, Open Babel, InChI) require their corresponding
source to be available. It is not shipped in the wheel but is fully specified
by `ci/build_binaries.sh`, which pins every upstream revision and records the
toolchain; see `NOTICE` for details.
