# Systre / Gavrog

`mofid_wrapper` bundles `Systre-experimental-20.8.0.jar` in its wheel
(`src/mofid_wrapper/_vendor/share/resources/`), taken as-is from the upstream
[`mofid`](https://github.com/snurr-group/mofid) repository's `Resources/`
directory. It is used, unmodified, to determine MOF topology via the Systre
command-line tool from the [Gavrog](https://github.com/odf/gavrog) project
(Olaf Delgado-Friedrichs).

## License

Gavrog (Systre and 3dt, and associated libraries) is licensed under the
**Apache License, Version 2.0**. It has carried this license since the
project's initial public commit (2011), so the bundled `20.8.0` build is
covered by it. The full license text is in
[`gavrog_LICENSE`](./gavrog_LICENSE) in this directory.

Apache-2.0 permits redistribution of the unmodified binary `.jar`. The
conditions relevant here (Section 4):

- a copy of the license travels with the redistribution -- satisfied by
  `gavrog_LICENSE`;
- this NOTICE file is retained;
- the jar itself is unmodified and carries no `NOTICE` file of its own that
  would need to be reproduced (none is present in the upstream Gavrog
  repository).

## Source

The corresponding source for this jar is the Gavrog project:
<https://github.com/odf/gavrog>. The RCSR net archive it is invoked with
(`RCSRnets.arc`) is covered separately -- see [`rcsr_NOTICE.md`](./rcsr_NOTICE.md).
