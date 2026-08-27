#!/bin/bash
# Builds the precompiled mofid/openbabel binaries and assembles them into
# src/mofid_wrapper/_vendor/, ready for `python -m build --wheel`.
#
# MUST run inside a manylinux_2_28_x86_64 container (see .github/workflows/
# build-and-test.yml) -- it installs packages via yum and assumes that
# environment. Run from the mofid_wrapper repo root.
#
# Every flag/step below was learned the hard way during the relocatability
# spike; see the plan doc / commit history for why each one is here:
#   - CMAKE_POLICY_VERSION_MINIMUM=3.5: manylinux's cmake (4.x) hard-errors on
#     openbabel's `cmake_policy(SET CMP0042 OLD)` (removed in modern cmake).
#     We additionally install an older cmake from PyPI since that policy
#     rejection isn't fully worked around by this flag alone on some cmake
#     versions.
#   - WITH_JSON=OFF: openbabel's bundled RapidJSON 1.1.0 doesn't compile
#     under GCC 14 (unrelated to CIF/MOF parsing -- only chemdoodle/pubchem
#     JSON format plugins need it).
#   - gcc-toolset-11: matches mofid upstream's own historical/documented
#     compiler pin (see upstream commit 1b8038e2) for its own src/.
#   - lib/ split into lib/ (core: libopenbabel.so*, libinchi.so*) and
#     lib/plugins/ (format/charge/descriptor/... plugins) with BABEL_LIBDIR
#     pointed only at lib/plugins/: openbabel's core libs are versioned
#     symlink chains (libopenbabel.so -> libopenbabel.so.7 ->
#     libopenbabel.so.7.0.0), and OpenBabel's plugin loader dlopen()s every
#     .so* file it finds in BABEL_LIBDIR. If the core libs sit in that same
#     directory, `cp -a` preserving the symlinks in-place is not enough:
#     wheel packaging (a zip file) does not preserve symlinks either, so on
#     install the 3 names become 3 full-content copies again, and dlopen()ing
#     "3 copies" of libopenbabel as if independent plugins duplicates its
#     static-initializer/registry state and corrupts the heap
#     (`free(): invalid pointer` / `double free or corruption` /
#     `munmap_chunk(): invalid pointer`, all seen in testing). Keeping the
#     core libs out of the BABEL_LIBDIR-scanned directory entirely sidesteps
#     the issue regardless of how the archive/wheel format handles symlinks.
set -euxo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MOFID_COMMIT="36873683083c7bc62c1da2062df2833adc35b48a"
BUILD_DIR="/tmp/mofid_build"
VENDOR_DIR="$REPO_ROOT/src/mofid_wrapper/_vendor"

# --- toolchain ---
yum install -y java-11-openjdk-headless patchelf gcc-toolset-11 git >/dev/null
source /opt/rh/gcc-toolset-11/enable
gcc --version | head -1
/opt/python/cp311-cp311/bin/pip install -q "cmake<4"
export PATH="/opt/python/cp311-cp311/bin:$PATH"
cmake --version | head -1

# --- fetch pinned upstream mofid + apply the setenv-overwrite patch ---
rm -rf "$BUILD_DIR"
git clone https://github.com/snurr-group/mofid.git "$BUILD_DIR"
cd "$BUILD_DIR"
git checkout "$MOFID_COMMIT"
git apply --check "$REPO_ROOT/ci/patches/0001-babel-env-no-overwrite.patch"
git apply "$REPO_ROOT/ci/patches/0001-babel-env-no-overwrite.patch"

# --- build openbabel (mirrors mofid's Makefile `init` target) ---
mkdir -p openbabel/build openbabel/installed
( cd openbabel/build && cmake \
    -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ \
    -DCMAKE_INSTALL_PREFIX=../installed -DENABLE_TESTS=OFF -DBUILD_GUI=OFF \
    -DEIGEN3_INCLUDE_DIR=../eigen -DWITH_JSON=OFF \
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5 .. )
( cd openbabel/build && make -j"$(nproc)" && make install )

# --- build mofid's own CLI tools ---
mkdir -p bin
( cd bin && cmake \
    -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ \
    -DOpenBabel3_DIR=../openbabel/build -DBUILD_TESTING=OFF \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_POLICY_VERSION_MINIMUM=3.5 ../src/ )
( cd bin && make -j"$(nproc)" )

# --- assemble the relocatable _vendor/ tree ---
rm -rf "$VENDOR_DIR"
mkdir -p "$VENDOR_DIR"/bin "$VENDOR_DIR"/lib "$VENDOR_DIR"/lib/plugins \
         "$VENDOR_DIR"/share/openbabel_data "$VENDOR_DIR"/share/resources

for exe in sbu sobgrep searchdb tsfm_smiles compare; do
  cp "bin/$exe" "$VENDOR_DIR/bin/"
done
cp openbabel/build/bin/obabel "$VENDOR_DIR/bin/"

# core libs (linked via DT_NEEDED, resolved at process-start via RPATH) vs.
# plugins (dlopen()'d individually by OpenBabel's own plugin loader, driven
# by BABEL_LIBDIR) -- see the note above on why these must NOT share a
# directory.
for f in openbabel/build/lib/*; do
  base="$(basename "$f")"
  if [[ "$base" == lib*.so* ]]; then
    cp -a "$f" "$VENDOR_DIR/lib/$base"
  else
    cp "$f" "$VENDOR_DIR/lib/plugins/$base"
  fi
done

cp -r openbabel/data/. "$VENDOR_DIR/share/openbabel_data/"
cp Resources/Systre-experimental-20.8.0.jar "$VENDOR_DIR/share/resources/"
cp Resources/RCSRnets.arc "$VENDOR_DIR/share/resources/"

# --- make it relocatable: patch RPATH to $ORIGIN-relative paths ---
for exe in "$VENDOR_DIR"/bin/*; do
  patchelf --set-rpath '$ORIGIN/../lib' "$exe"
done
for so in "$VENDOR_DIR"/lib/*.so*; do
  if [ -f "$so" ] && [ ! -L "$so" ]; then
    patchelf --set-rpath '$ORIGIN' "$so"
  fi
done
for so in "$VENDOR_DIR"/lib/plugins/*.so*; do
  patchelf --set-rpath '$ORIGIN/..' "$so"
done

# --- bake the upstream commit into _build_info.py for provenance ---
cat > "$REPO_ROOT/src/mofid_wrapper/_build_info.py" <<EOF
"""Provenance of the upstream mofid commit these binaries were built from.

Written by ci/build_binaries.sh at wheel-build time.
"""

MOFID_SOURCE_COMMIT = "$MOFID_COMMIT"
EOF

echo "=== _vendor/ assembled ==="
find "$VENDOR_DIR" -maxdepth 3 | sort
echo "=== BUILD_BINARIES DONE ==="
