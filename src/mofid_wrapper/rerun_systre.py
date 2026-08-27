"""
Rerun Systre with verbose output.

Calls the Systre command, writing its full, raw stdout and stderr instead of
parsing out the RCSR topology or other error states. Useful as a diagnostic
after cif2mofid(). Ported from upstream mofid's Python/rerun_systre.py.
"""

import subprocess
import sys

from mofid_wrapper.id_constructor import DEFAULT_SYSTRE_CGD, SYSTRE_CMD_LIST, _require_java

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 1:
        raise SyntaxError("Usage: python -m mofid_wrapper.rerun_systre optional_path.cgd")
    cgd_path = args[0] if len(args) == 1 else DEFAULT_SYSTRE_CGD

    _require_java()
    cmd_list = SYSTRE_CMD_LIST + [cgd_path]
    subprocess.run(cmd_list, universal_newlines=True)
