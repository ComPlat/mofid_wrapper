# InChI library

`mofid_wrapper`'s wheel bundles the shared library `libinchi.so.0.4.1`
(`src/mofid_wrapper/_vendor/lib/`, with the `libinchi.so` and `libinchi.so.0`
symlinks). It is produced from the InChI sources vendored inside Open Babel
(`src/formats/libinchi/` in the upstream Open Babel tree) and is loaded by
Open Babel's `inchiformat` plugin. `mofid_wrapper` builds it unmodified from
that source.

## Version and license

The vendored sources identify themselves as **InChI Software version 1.04
(September 2011)**. That release is licensed under the **IUPAC/InChI-Trust
Licence for the International Chemical Identifier (InChI) Software version 1.0**
("IUPAC/InChI-Trust InChI Licence No. 1.0"), an LGPL-style copyleft licence.
Copyright (C) IUPAC and InChI Trust Limited. Full text:
[`inchi_LICENSE`](./inchi_LICENSE).

Note: newer InChI releases (>= 1.07.1, 2024) are distributed by the InChI
Project under the MIT licence, but that does **not** apply retroactively to
the 1.04 code shipped here.

## Compliance notes for redistributors

- A copy of the licence travels with this distribution (`inchi_LICENSE`).
- This NOTICE is retained.
- The library is used via a shared-library mechanism (Section 6b of the
  licence): Open Babel `dlopen()`s it at run time; it is not statically
  linked into any executable.
- The InChI sources are not modified, so the Section 15 naming restriction
  (modified builds may not call their output "InChI") is not triggered.

## Source

Corresponding source for the bundled `libinchi.so`:

- as vendored and built here -- Open Babel at the pinned commit, `src/formats/libinchi/`
  (see the top-level `NOTICE` for how to obtain the exact tree);
- upstream InChI project -- <https://www.inchi-trust.org/> and
  <https://github.com/IUPAC-InChI/InChI>. The 1.04 licence PDF:
  <https://www.inchi-trust.org/download/104/LICENCE.pdf>.
