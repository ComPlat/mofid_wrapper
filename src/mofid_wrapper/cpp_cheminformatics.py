"""
Cheminformatics helpers that shell out to the bundled Open Babel binaries.

Ported from upstream mofid's Python/cpp_cheminformatics.py.
"""

import re
import subprocess
import sys

from mofid_wrapper._paths import bin_path

OBABEL_BIN = str(bin_path / "obabel")
TSFM_BIN = str(bin_path / "tsfm_smiles")


def runcmd(cmd_list, timeout=None):
    return subprocess.run(
        cmd_list,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )


def quote(smiles_str):
    # Prepares SMILES strings for Open Babel command line calls.
    return smiles_str


def in_smiles(smiles_str):
    # Adds necessary quotes and Open Babel input notation for SMILES strings
    return "-:" + quote(smiles_str)


def ob_normalize(smiles):
    # Normalizes an arbitrary SMILES string with the same format and parameters as sbu.cpp
    cpp_run = runcmd([OBABEL_BIN, in_smiles(smiles), "-xi", "-ocan"])
    cpp_output = cpp_run.stdout
    if cpp_run.stderr != "1 molecule converted\n":
        sys.stderr.write(cpp_run.stderr + "\n")
    return cpp_output.rstrip()


def openbabel_replace(mol_smiles, query, replacement):
    # Perform Open Babel transforms, deletions, and/or replacements on a SMILES molecule.
    cpp_run = runcmd([TSFM_BIN, quote(mol_smiles), quote(query), quote(replacement)])
    cpp_output = cpp_run.stdout
    sys.stderr.write(cpp_run.stderr)
    return ob_normalize(cpp_output.rstrip())


def openbabel_contains(mol_smiles, query):
    # Checks if a molecule (including multi-fragment) contains a SMARTS match
    cpp_run = runcmd(
        [OBABEL_BIN, in_smiles(mol_smiles), "-s", quote(query), "-xi", "-ocan"]
    )
    if cpp_run.stderr == "1 molecule converted\n":
        return True
    elif cpp_run.stderr == "0 molecules converted\n":
        return False
    else:
        sys.stderr.write(cpp_run.stderr + "\n")
        return False


def openbabel_formula(mol_smiles, smiles=True):
    # Extracts a molecular formula without relying on the pybel module
    input_str = in_smiles(mol_smiles) if smiles else mol_smiles
    cpp_run = runcmd(
        [
            OBABEL_BIN,
            input_str,
            "-ab",
            "--title",
            "FAKE",
            "--append",
            "FORMULA",
            "-otxt",
        ]
    )
    cpp_output = cpp_run.stdout
    if cpp_run.stderr != "1 molecule converted\n":
        sys.stderr.write(cpp_run.stderr + "\n")
    return cpp_output.rstrip().split()[1]  # removes the overwritten title


def openbabel_GetSpacedFormula(mol_smiles, delim=" ", smiles=True):
    # Re-implements part of OpenBabel's GetSpacedFormula method
    consolidated_formula = openbabel_formula(mol_smiles, smiles)
    split_formula = re.findall(r"[A-Z][a-z]?|\d+", consolidated_formula)
    if split_formula[-1] == "":
        split_formula.pop()
    return delim.join(split_formula)
