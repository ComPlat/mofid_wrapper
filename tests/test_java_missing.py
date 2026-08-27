"""
Regression test: importing mofid_wrapper must NOT require Java on PATH.

Upstream mofid checked for `java` at module import time, so `import mofid`
failed even for code paths that never touch Systre. mofid_wrapper moves that
check into extract_topology() -- this test locks that behavior in.
"""

import sys

import pytest


def test_import_does_not_require_java(monkeypatch):
    monkeypatch.setenv("PATH", "/nonexistent")
    for mod in list(sys.modules):
        if mod == "mofid_wrapper" or mod.startswith("mofid_wrapper."):
            del sys.modules[mod]
    import mofid_wrapper  # noqa: F401 -- must not raise, even re-imported fresh


def test_topology_raises_actionable_error_without_java(monkeypatch, tmp_path):
    monkeypatch.setenv("PATH", "/nonexistent")
    from mofid_wrapper.id_constructor import extract_topology

    with pytest.raises(RuntimeError, match="Java runtime"):
        extract_topology(str(tmp_path / "topology.cgd"))
