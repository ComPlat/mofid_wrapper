# mofid_wrapper — remaining work

Status as of 2026-08-27. Phase 1 is done (commit `0835a9d`). This file tracks
what's left so a later session can pick up without re-deriving context.

## What this project is

A pip-installable wrapper around upstream [MOFid](https://github.com/snurr-group/mofid).
The wheel bundles precompiled Linux x86_64 binaries (Open Babel + mofid's C++
CLI tools) + the Systre jar as package data, so `pip install` needs no C/C++
compiler. Only a JRE is required at runtime (topology step), checked lazily.

Key files:
- `ci/build_binaries.sh` — builds + relocates the binaries into `src/mofid_wrapper/_vendor/` (must run in a `manylinux_2_28_x86_64` container)
- `ci/build_wheel.sh` — `python -m build --wheel` over the assembled tree
- `ci/patches/0001-babel-env-no-overwrite.patch` — flips `setenv(..., 1)` → `0` in mofid's C tools so they don't clobber the env vars `_paths.py` sets
- `src/mofid_wrapper/_paths.py` — runtime-relative paths + sets `BABEL_DATADIR`/`BABEL_LIBDIR` + `chmod +x` the binaries
- `.github/workflows/` — `build-and-test.yml` (every push/PR), `release.yml` (on `v*` tag → PyPI)

`_vendor/`, `build/`, `dist/` are gitignored (CI artifacts). A prebuilt wheel
exists locally at `dist/mofid_wrapper-0.1.0-py3-none-manylinux_2_28_x86_64.whl`
(built 2026-08-25) and passes all 15 tests in a clean venv (Py 3.13, JRE 21).

## Phase 1 — DONE (commit 0835a9d)

- [x] Initial git commit
- [x] Fixed stale `setup.py (BinaryDistribution)` comment in `ci/build_wheel.sh`
- [x] Tests 4 → 15: added `tests/test_openbabel_binary.py` (engine + plugin
      checks) and `tests/test_id_constructor.py` (pure-Python assemble/parse units)

## Phase 1.5 — third-party licensing — DONE (2026-09-01)

Every bundled binary/data file now has its license + corresponding-source
pointer recorded.

- [x] `THIRD_PARTY_LICENSES/gavrog_LICENSE` — Systre/Gavrog is **Apache-2.0**
      (has been since Gavrog's 2011 initial commit), not GPL. `systre_NOTICE.md`
      rewritten from placeholder to a real Apache-2.0 §4 compliance note.
- [x] `THIRD_PARTY_LICENSES/inchi_LICENSE` + `inchi_NOTICE.md` — the bundled
      `libinchi.so.0.4.1` is InChI **1.04**, under the IUPAC/InChI-Trust InChI
      Licence No. 1.0 (LGPL-style). Verified version from the source headers in
      OpenBabel's `src/formats/libinchi/`. Newer InChI (>=1.07.1) is MIT but
      that does not apply to the 1.04 code we ship.
- [x] `THIRD_PARTY_LICENSES/rcsr_NOTICE.md` — provenance + citation note for
      `RCSRnets.arc`.
- [x] Top-level `NOTICE` — one list of all 5 components (MOFid, Open Babel,
      InChI, Systre/Gavrog, RCSR) with license + source pointer + a
      GPL-§3 / InChI-§6 corresponding-source statement pointing at
      `ci/build_binaries.sh`. Added to `pyproject.toml` `license-files` so it
      installs into `*.dist-info/licenses/`.
- [x] `README.md` "License" section replaced with a component table.

## Phase 2 — Into ComPlat, CI green

This is **work for ComPlat**, not a personal repo. Blocked on the boss
creating the org repo.

- [ ] **Decide the name** (repo + PyPI distribution should match). `mofid_wrapper`
      is free on PyPI; plain `mofid` likely isn't. Candidates: `mofid-complat`,
      `mofid-wheel`.
- [ ] **Ask boss to create `ComPlat/<name>`** on GitHub.
- [ ] Rewrite account references once the repo exists:
    - [ ] `pyproject.toml` — `[project.urls]` homepage/repository (currently
          `github.com/Konrad1991/mofid_wrapper`)
    - [ ] `LICENSE` copyright holder → institution, if that's ComPlat's norm
    - [ ] `README.md` — install line, any badge URLs
    - [ ] `pyproject.toml` `[project].name` / `authors` if the dist name changes
- [ ] Push; watch the first `build-and-test.yml` run. This is the real
      validation not possible locally: full container build + install on a
      clean runner + tests.
- [ ] Add a Python version matrix to `build-and-test.yml` (3.9–3.13); currently
      only 3.11 is exercised.

## Phase 3 — Publish to PyPI

- [ ] Create the `pypi` environment in repo Settings → Environments (add
      required reviewers if a manual release gate is wanted). `release.yml`
      already references `environment: pypi`.
- [ ] Configure PyPI **Trusted Publishing** (OIDC, no stored token): register
      `ComPlat/<repo>` + workflow `release.yml` + environment `pypi` as a
      pending publisher on PyPI. Done by whoever owns the PyPI project/account.
- [ ] Tag `v0.1.0` → triggers `release.yml` (build → test → publish).
- [ ] Verify `pip install <name>` works from a clean machine with a JRE.

## Later / optional

- [ ] **aarch64 wheel** (ARM Linux). Same `build_binaries.sh` in a second
      container; everything else is arch-agnostic.
- [ ] Broaden MOF coverage: port a handful of cases from upstream
      `tests/check_mof_composition.py` (recipe DB + `Resources/TestCIFs`).
- [ ] `CHANGELOG.md` + a short "how to bump the pinned upstream mofid commit"
      note in `ci/` — that's the one recurring maintenance task
      (`MOFID_COMMIT` in `ci/build_binaries.sh`, currently
      `36873683083c7bc62c1da2062df2833adc35b48a`).
- [ ] Confirm scope with the colleague who requested this: Linux only, JRE
      required, and the 3 `pybel`-dependent upstream modules
      (`old_cheminformatics`, `extract_metals`, `remove_metals`) are **not**
      included. Make sure `cif2mofid` covers their use case.

## Known rough edges (deliberately left as-is for upstream parity)

- `id_constructor.parse_mofid`: upstream typo `mofid_data.lstrip != mofid_data`
  (compares a method to a string, always true). Cosmetic only — wrong error
  message on single-token input. Documented in
  `tests/test_id_constructor.py::test_parse_mofid_rejects_bare_token`.
- `run_mofid.cif2mofid` on a malformed/non-MOF `.cif` raises `IndexError` at
  the final `openbabel_GetSpacedFormula` call instead of returning a
  "no MOF found" result (upstream behaves the same). `extract_fragments`'s
  own `["*"]` fallback works; only the formula step is unguarded. Fixing it
  means a deliberate divergence from upstream — decide before doing it.
