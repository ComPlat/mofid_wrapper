# RCSR net archive (`RCSRnets.arc`)

`mofid_wrapper`'s wheel bundles the data file `RCSRnets.arc`
(`src/mofid_wrapper/_vendor/share/resources/`), taken unmodified from the
upstream [`mofid`](https://github.com/snurr-group/mofid) repository's
`Resources/` directory. It is the Systre-format archive of known nets from
the **Reticular Chemistry Structure Resource (RCSR)**, <http://rcsr.net/>,
and is passed to Systre as its reference archive so that computed MOF
topologies can be matched to named RCSR nets.

## Provenance and terms

`RCSRnets.arc` is a factual database of net topologies compiled by the RCSR
project (M. O'Keeffe, M. A. Peskov, S. J. Ramsden, O. M. Yaghi). The same
data is offered for public download from <http://rcsr.net/systre> as "Systre
input data (.cgd)". RCSR makes its data freely available for research use;
publications that use it are asked to cite:

  M. O'Keeffe, M. A. Peskov, S. J. Ramsden and O. M. Yaghi,
  "The Reticular Chemistry Structure Resource (RCSR) Database of, and Symbols
  for, Crystal Nets", Acc. Chem. Res. 2008, 41, 1782-1789.

`mofid_wrapper` redistributes the copy as it appears in upstream mofid, which
is itself distributed under GPL-2.0. No separate machine-readable licence
file accompanies this archive upstream; it is included here for provenance
and citation, not as a claim of additional licensing terms by this package.
