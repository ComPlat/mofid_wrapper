#!/bin/bash
# Builds the wheel from the already-assembled src/mofid_wrapper/_vendor/ tree.
# Run inside manylinux_2_28_x86_64, from the repo root, after build_binaries.sh.
set -euxo pipefail

# setup.cfg's [bdist_wheel] python_tag/plat_name force the correct
# py3-none-manylinux_2_28_x86_64 tag directly -- no need to use `auditwheel
# repair`'s automatic dependency-closure walk (which follows link-time
# DT_NEEDED and would miss openbabel's dlopen()-loaded plugins) or a manual
# filename-only relabel. (The wheel still reports Root-Is-Purelib: true since
# there is no ext module / custom Distribution class; harmless here -- pip
# installs the platform-tagged wheel into the environment either way.)
/opt/python/cp311-cp311/bin/pip install -q --upgrade pip build wheel
/opt/python/cp311-cp311/bin/python -m build --wheel --outdir dist
ls -la dist
