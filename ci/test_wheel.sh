#!/bin/bash
# Installs the built wheel fresh (no build toolchain present) and runs the
# test suite against it. Run on a PLAIN python:3.11 (or similar) container --
# deliberately NOT the manylinux build container -- to catch "only works
# inside the build container" bugs.
set -euxo pipefail

apt-get update -qq
apt-get install -y -qq default-jre-headless >/dev/null

python3 -m venv /tmp/venv
source /tmp/venv/bin/activate
pip install -q --upgrade pip
pip install -q dist/*.whl pytest

python -c "import mofid_wrapper; print('mofid_wrapper', mofid_wrapper.__version__)"
pytest -v tests/
