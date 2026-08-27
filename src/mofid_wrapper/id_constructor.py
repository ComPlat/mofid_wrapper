"""
Calculate a MOFid string.

Extracts the node and linker identities from the bundled `sbu` binary, plus
topological classification from Systre. Ported from upstream mofid's
Python/id_constructor.py.

Upstream checked for Java at *module import time*, meaning `import mofid`
failed even for code paths that never touch Systre. Here the check is lazy
(inside extract_topology) with an actionable error message.
"""

import os
import subprocess
import sys

from mofid_wrapper._paths import bin_path, resources_path

GAVROG_LOC = str(resources_path / "Systre-experimental-20.8.0.jar")
JAVA_LOC = "java"
RCSR_PATH = str(resources_path / "RCSRnets.arc")
DEFAULT_SYSTRE_CGD = os.path.join("Output", "SingleNode", "topology.cgd")
SYSTRE_TIMEOUT = 30  # max time to allow Systre to run (seconds)
SBU_BIN = str(bin_path / "sbu")

SYSTRE_CMD_LIST = [
    JAVA_LOC,
    "-Xmx1024m",
    "-cp",
    GAVROG_LOC,
    "org.gavrog.apps.systre.SystreCmdline",
    RCSR_PATH,
]


def _require_java():
    try:
        subprocess.run(
            ["java", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except FileNotFoundError:
        raise RuntimeError(
            "mofid_wrapper requires a Java runtime (`java`) on your PATH to "
            "compute MOF topology via Systre. Install a JRE, e.g. "
            "`apt install default-jre-headless` on Debian/Ubuntu, and try again."
        )


def runcmd(cmd_list, timeout=None):
    return subprocess.run(
        cmd_list,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )


def extract_fragments(mof_path, output_path):
    # Extract MOF decomposition information using the bundled sbu binary
    cpp_run = runcmd([SBU_BIN, mof_path, output_path])
    cpp_output = cpp_run.stdout
    sys.stderr.write(cpp_run.stderr)  # Re-forward sbu.cpp errors
    if cpp_run.returncode:
        all_fragments = ["*"]  # Null-behaving atom, so the .smi file is still useful
    else:
        all_fragments = cpp_output.strip().split("\n")
        all_fragments = [x.strip() for x in all_fragments]

    cat = None
    if "simplified net(s)" in all_fragments[-1]:
        cat = all_fragments.pop()[8]  # '# Found x simplified net(s)'
        cat = str(int(cat) - 1)
        if cat == "-1":
            cat = None

    if all_fragments[0] != "# Nodes:":
        return (["*"], [], cat, "")
    all_fragments.pop(0)
    linker_flag_loc = all_fragments.index("# Linkers:")
    node_fragments = all_fragments[:linker_flag_loc]
    linker_fragments = all_fragments[linker_flag_loc + 1 :]

    base_mofkey = None
    if not cpp_run.returncode:
        mofkey_loc = os.path.join(output_path, "MetalOxo", "mofkey_no_topology.txt")
        with open(mofkey_loc) as f:
            base_mofkey = f.read().rstrip()

    return (sorted(node_fragments), sorted(linker_fragments), cat, base_mofkey)


def extract_topology(mof_path):
    # Extract underlying MOF topology using Systre and sbu's output data
    _require_java()
    try:
        java_run = runcmd(SYSTRE_CMD_LIST + [mof_path], timeout=SYSTRE_TIMEOUT)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    java_output = java_run.stdout

    topologies = []
    current_component = 0
    topology_line = False
    repeat_line = False
    for raw_line in java_output.split("\n"):
        line = raw_line.strip()
        if topology_line:
            topology_line = False
            rcsr = line.split()
            assert rcsr[0] == "Name:"
            topologies.append(rcsr[1])
        elif repeat_line:
            repeat_line = False
            assert line.split()[0] == "Name:"
            components = line.split("_")
            assert components[-2] == "component"
            topologies.append(topologies[int(components[-1]) - 1])
        elif "ERROR" in line:
            return "ERROR"
        elif "Structure was found in archive" in line:
            topology_line = True
        elif line == "Structure is new for this run.":
            topologies.append("UNKNOWN")
        elif line == "Structure already seen in this run.":
            repeat_line = True
        elif "Processing component " in line:
            assert len(topologies) == current_component
            current_component += 1
            line_num = line.split("component")[-1].split(":")[0].strip()
            assert line_num == str(current_component)

    if len(topologies) == 0:
        return "ERROR"
    first_net = topologies[0]
    for net in topologies:
        if net != first_net:
            return "MISMATCH"
    return first_net


def assemble_mofid(fragments, topology, cat=None, mof_name="NAME_GOES_HERE", commit_ref="NO_REF"):
    # Assemble the MOFid string from its components
    mofid = ".".join(fragments) + " "
    mofid = mofid + "MOFid-v1" + "."
    mofid = mofid + topology + "."
    if cat == "no_mof":
        mofid = mofid + cat
    elif cat is not None:
        mofid = mofid + "cat" + cat
    else:
        mofid = mofid + "NA"
    if mofid.startswith(" "):  # Null linkers. Make .smi compatible
        mofid = "*" + mofid + "no_mof"
    mofid = mofid + "." + commit_ref
    mofid = mofid + ";" + mof_name
    return mofid


def assemble_mofkey(base_mofkey, base_topology, commit_ref="NO_REF"):
    # Add a topology to an existing MOFkey
    return base_mofkey.replace(
        "MOFkey-v1", "MOFkey-v1." + base_topology + "." + commit_ref
    )


def parse_mofid(mofid):
    # Deconstruct a MOFid string into its pieces
    mofid_parts = mofid.rstrip().split(";")
    mofid_data = mofid_parts[0]
    if len(mofid_parts) > 1:
        mofid_name = ";".join(mofid_parts[1:])
    else:
        mofid_name = None

    components = mofid_data.split()
    if len(components) == 1:
        if mofid_data.lstrip != mofid_data:  # Empty SMILES: no MOF found
            components.append(components[0])
            components[0] = ""
        else:
            raise ValueError("MOF metadata required")
    smiles = components[0]
    if len(components) > 2:
        raise ValueError(
            "Bad MOFid containing extra spaces before the semicolon:" + mofid
        )
    metadata = components[1]
    metadata = metadata.split(".")

    cat = None
    topology = None
    for loc, tag in enumerate(metadata):
        if loc == 0 and not tag.startswith("MOFid"):
            raise ValueError("MOFid-v1 must start with the correct tag")
        if loc == 0 and tag[5:] != "-v1":
            raise ValueError("Unsupported version of MOFid")
        elif loc == 1:
            topology = tag
        elif tag.lower().startswith("cat"):
            cat = tag[3:]
        else:
            pass

    return dict(smiles=smiles, topology=topology, cat=cat, name=mofid_name)
