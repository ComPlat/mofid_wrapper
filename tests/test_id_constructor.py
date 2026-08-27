"""
Unit tests for the pure-Python string machinery in id_constructor.

No binaries, no Java -- these are fast and exist mainly so a regression in
the MOFid/MOFkey assembly or parsing shows up on its own rather than only as
a confusing failure of the end-to-end tests.
"""

import pytest

from mofid_wrapper.id_constructor import (
    assemble_mofid,
    assemble_mofkey,
    extract_fragments,
    parse_mofid,
)


def test_assemble_and_parse_roundtrip_with_cat():
    mofid = assemble_mofid(
        ["[Zn]", "c1ccccc1"], "pcu", cat="0", mof_name="FOO", commit_ref="ref1"
    )
    assert mofid == "[Zn].c1ccccc1 MOFid-v1.pcu.cat0.ref1;FOO"

    parsed = parse_mofid(mofid)
    assert parsed == {
        "smiles": "[Zn].c1ccccc1",
        "topology": "pcu",
        "cat": "0",
        "name": "FOO",
    }


def test_assemble_and_parse_roundtrip_no_cat():
    mofid = assemble_mofid(["[Cu]"], "NA", cat=None, mof_name="BAR", commit_ref="r2")
    assert mofid == "[Cu] MOFid-v1.NA.NA.r2;BAR"

    parsed = parse_mofid(mofid)
    assert parsed["smiles"] == "[Cu]"
    assert parsed["topology"] == "NA"
    assert parsed["cat"] is None
    assert parsed["name"] == "BAR"


def test_assemble_mofid_empty_fragments_is_smi_compatible():
    # Null linkers: the string must still start with a real SMILES atom so
    # downstream .smi consumers don't choke.
    mofid = assemble_mofid([], "NA", cat=None, mof_name="EMPTY", commit_ref="r3")
    assert mofid.startswith("* ")
    assert parse_mofid(mofid)["smiles"] == "*"


def test_assemble_mofkey_inserts_topology_and_ref():
    out = assemble_mofkey("Zn.KKEYFWRCBNTPAC.MOFkey-v1;NAME", "pcu", commit_ref="cr")
    assert out == "Zn.KKEYFWRCBNTPAC.MOFkey-v1.pcu.cr;NAME"


def test_parse_mofid_rejects_wrong_tag():
    with pytest.raises(ValueError):
        parse_mofid("CCO MOFXX-v1.pcu.NA;n")


def test_parse_mofid_rejects_bare_token():
    # NOTE: ported straight from upstream, where `parse_mofid` has a latent
    # bug -- `mofid_data.lstrip != mofid_data` compares a method object to a
    # string, so it is always true and a single-token input takes the
    # "empty SMILES" branch instead of raising "MOF metadata required".
    # Net effect is still a ValueError, which is all this locks in; if the
    # upstream typo is ever fixed the message changes and this test should be
    # tightened.
    with pytest.raises(ValueError):
        parse_mofid("justonetoken")


def test_extract_fragments_falls_back_on_non_mof_input(tmp_path):
    junk = tmp_path / "junk.cif"
    junk.write_text("this is not a valid cif file\n")

    node, linker, cat, base_mofkey = extract_fragments(str(junk), str(tmp_path))
    assert node == ["*"]
    assert linker == []
    assert cat is None
    assert base_mofkey == ""
