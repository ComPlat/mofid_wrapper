# mofid_wrapper

A pip-installable wrapper around [MOFid](https://github.com/snurr-group/mofid) for rapid identification and analysis of metal-organic frameworks.

Prebuilt release wheels for Linux x86_64 include the required native binaries (Open Babel and MOFid's CLI tools). Installing one of these wheels does **not** require a C/C++ compiler and does not build Open Babel from source.

## Installation

### Option 1: Install the prebuilt wheel directly from a GitHub release

This is the recommended installation method.

```bash
pip install https://github.com/ComPlat/mofid_wrapper/releases/download/<VERSION>/<WHEEL_FILE>.whl
```

For example:

```bash
pip install https://github.com/ComPlat/mofid_wrapper/releases/download/v0.1.0/mofid_wrapper-0.1.0-py3-none-manylinux_2_28_x86_64.whl
```

The wheel is built beforehand by GitHub Actions and already contains the required Open Babel and MOFid binaries. No local C/C++ compilation is performed during installation.

### Option 2: Download the wheel first and install it locally

Download the appropriate `.whl` file from the [GitHub Releases](https://github.com/ComPlat/mofid_wrapper/releases) page and then install it with:

```bash
pip install ./mofid_wrapper-0.1.0-py3-none-manylinux_2_28_x86_64.whl
```

This is equivalent to installing the wheel directly from its GitHub release URL. The native binaries are already included, so no local compiler is required.

### Option 3: Build from a local source checkout

If you clone the repository instead of installing a prebuilt wheel, the vendored native binaries are **not** present in the Git repository and must be built locally first.

```bash
git clone https://github.com/ComPlat/mofid_wrapper.git
cd mofid_wrapper

./ci/build_binaries.sh
pip install .
```

`ci/build_binaries.sh` builds Open Babel and the required MOFid CLI tools and places them into the package's `_vendor` directory. `pip install .` then builds and installs the Python package using these locally built binaries.

This installation method therefore requires the necessary C/C++ compiler and build dependencies.

Running only:

```bash
git clone https://github.com/ComPlat/mofid_wrapper.git
cd mofid_wrapper
pip install .
```

is **not sufficient**, because `pip install .` does not automatically run `ci/build_binaries.sh` and the native Open Babel/MOFid binaries are not stored in the Git repository.

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
