"""
Parent module for obtaining MOFid data for a single .cif

Ported from upstream mofid's Python/run_mofid.py.

Upstream reads `.git/ORIG_HEAD` for a `commit_ref` embedded in the MOFid
string, which is meaningless for a pip-installed package (no .git dir in
site-packages) and always fell back to 'NO_REF'. Here it's replaced with the
wrapper's own version plus the pinned upstream mofid commit that produced the
bundled binaries, preserving the original provenance intent.
"""

import json
import os

from mofid_wrapper._build_info import MOFID_SOURCE_COMMIT
from mofid_wrapper._version import __version__
from mofid_wrapper.cpp_cheminformatics import openbabel_GetSpacedFormula
from mofid_wrapper.id_constructor import (
    assemble_mofid,
    assemble_mofkey,
    extract_fragments,
    extract_topology,
    parse_mofid,
)

DEFAULT_OUTPUT_PATH = "Output"


def _commit_ref():
    return f"mofidwrapper{__version__}-mofid{MOFID_SOURCE_COMMIT[:8]}"


def cif2mofid(cif_path, output_path=DEFAULT_OUTPUT_PATH):
    # Assemble the MOFid string from all of its pieces.
    # Also export the MOFkey in an output dict for convenience.
    cif_path = os.path.abspath(cif_path)
    output_path = os.path.abspath(output_path)

    node_fragments, linker_fragments, cat, base_mofkey = extract_fragments(
        cif_path, output_path
    )
    if cat is not None:
        sn_topology = extract_topology(
            os.path.join(output_path, "SingleNode", "topology.cgd")
        )
        an_topology = extract_topology(
            os.path.join(output_path, "AllNode", "topology.cgd")
        )
        if sn_topology == an_topology or an_topology == "ERROR":
            topology = sn_topology
        else:
            topology = sn_topology + "," + an_topology
    else:
        topology = "NA"

    mof_name = os.path.splitext(os.path.basename(cif_path))[0]
    mofkey = base_mofkey
    commit_ref = _commit_ref()

    if topology != "NA":
        base_topology = topology.split(",")[0]
        mofkey = assemble_mofkey(mofkey, base_topology, commit_ref=commit_ref)

    all_fragments = []
    all_fragments.extend(node_fragments)
    all_fragments.extend(linker_fragments)
    all_fragments.sort()
    mofid = assemble_mofid(
        all_fragments, topology, cat=cat, mof_name=mof_name, commit_ref=commit_ref
    )
    parsed = parse_mofid(mofid)

    identifiers = {
        "mofid": mofid,
        "mofkey": mofkey,
        "smiles_nodes": node_fragments,
        "smiles_linkers": linker_fragments,
        "smiles": parsed["smiles"],
        "topology": parsed["topology"],
        "cat": parsed["cat"],
        "cifname": parsed["name"],
    }

    with open(os.path.join(output_path, "python_mofid.txt"), "w") as f:
        f.write(identifiers["mofid"] + "\n")
    with open(os.path.join(output_path, "python_mofkey.txt"), "w") as f:
        f.write(identifiers["mofkey"] + "\n")
    with open(os.path.join(output_path, "python_smiles_parts.txt"), "w") as f:
        for smiles in node_fragments:
            f.write("node" + "\t" + smiles + "\n")
        for smiles in linker_fragments:
            f.write("linker" + "\t" + smiles + "\n")
    with open(os.path.join(output_path, "python_molec_formula.txt"), "w") as f:
        f.write(
            openbabel_GetSpacedFormula(
                os.path.join(output_path, "orig_mol.cif"), " ", False
            )
            + "\n"
        )

    return identifiers


if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    if len(args) not in [1, 2, 3]:
        raise SyntaxError(
            "Usage: python -m mofid_wrapper.run_mofid path_to_cif.cif "
            "OutputPathIfNonstandard OutputMofidOrJson"
        )
    cif_file = args[0]
    output_path = DEFAULT_OUTPUT_PATH
    output_json = False
    if len(args) >= 2:
        output_path = args[1]
    if len(args) == 3:
        if args[2] == "json":
            output_json = True
        elif args[2] != "mofid":
            raise SyntaxError("Third argument must be json, mofid, or not provided")

    identifiers = cif2mofid(cif_file, output_path)
    if output_json:
        print(json.dumps(identifiers))
    else:
        print(identifiers["mofid"])
