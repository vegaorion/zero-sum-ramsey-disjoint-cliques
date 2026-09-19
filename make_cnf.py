#!/usr/bin/env python3
"""
make_cnf.py  --  press Run.  No arguments needed.

Regenerates all seven CNF formulas into cnf/.

WARNING.  If the DRAT proofs in proofs/ were produced from CNF files written by
a different encoder, running this will overwrite those CNF files and the proofs
will no longer verify against them.  Check first with:

    python3 src/encode.py --N 8 --r 3 --s 2 --reduction none -o test.cnf
    diff test.cnf cnf/K8_2K3_none.cnf

If they differ, do not run this script; keep your own CNF files.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))

import encode  # noqa: E402

# (filename stem, N, r, s, reduction)
INSTANCES = [
    ("K8_2K3_none",    8, 3, 2, "none"),
    ("K10_2K4_gauge", 10, 4, 2, "gauge"),
    ("K13_3K4_gauge", 13, 4, 3, "gauge"),
    ("K13_3K4_none",  13, 4, 3, "none"),
    ("K7_2K3",         7, 3, 2, "none"),
    ("K9_2K4",         9, 4, 2, "gauge"),
    ("K12_3K4",       12, 4, 3, "gauge"),
]


def main():
    out = os.path.join(HERE, "cnf")
    os.makedirs(out, exist_ok=True)

    if os.path.isdir(os.path.join(HERE, "proofs")):
        existing = [f for f in os.listdir(os.path.join(HERE, "proofs"))
                    if f.endswith(".drat")]
        if existing:
            print("NOTE: proofs/ already contains %d DRAT file(s)." % len(existing))
            print("      Overwriting cnf/ may invalidate them.  See the docstring.")
            print()

    print("Generating seven formulas.  The two K_13 files take a minute each.")
    print()
    for stem, N, r, s, red in INSTANCES:
        path = os.path.join(out, stem + ".cnf")
        cls, nv = encode.build(N, r, s, red)
        hdr = ["Phi(K_%d, %dK_%d), reduction=%s" % (N, s, r, red),
               "copies: %d" % encode.n_copies(N, r, s),
               "UNSAT is equivalent to R(%dK_%d, Z_3) <= %d" % (s, r, N)]
        encode.write_dimacs(path, cls, nv, hdr)
        print("  %-18s %8d variables %10d clauses"
              % (stem + ".cnf", nv, len(cls)))

    print()
    print("Done.  Now run run_all.py.")


if __name__ == "__main__":
    main()
