#!/usr/bin/env python3
"""
Evaluate the closed forms of equation (5.1) of the paper, and optionally compare
them against the headers of the shipped CNF files.

    V = 3*C(N,2) + 3*(C(r,2)-1)*C(N,r)
    C = 4*C(N,2) + 10*(C(r,2)-1)*C(N,r) + 3^(s-1)*kappa + eps*(N-1)

where kappa is the number of copies of sK_r in K_N and eps records gauge fixing.

This script deliberately does NOT import src/encode.py.  Its purpose is to let a
reader confirm the size of every formula without trusting the encoder: an
under-constrained encoding -- a missing family of copies, say -- would show up
here as a mismatch against the shipped file.

Usage
    python3 src/counts.py                # print the table
    python3 src/counts.py --check cnf    # compare against cnf/*.cnf headers
"""

import argparse
import glob
import os
import sys
from math import comb

# (label, N, r, s, gauge)
INSTANCES = [
    ("K8_2K3_none",    8, 3, 2, False),
    ("K10_2K4_gauge", 10, 4, 2, True),
    ("K13_3K4_gauge", 13, 4, 3, True),
    ("K13_3K4_none",  13, 4, 3, False),
    ("K7_2K3",         7, 3, 2, False),
    ("K9_2K4",         9, 4, 2, True),
    ("K12_3K4",       12, 4, 3, True),
]


def kappa(N, r, s):
    """Number of copies of sK_r in K_N."""
    total = 1
    for j in range(s):
        total *= comb(N - j * r, r)
    for j in range(2, s + 1):
        total //= j
    return total


def counts(N, r, s, gauge):
    m = comb(r, 2)
    nv = 3 * comb(N, 2) + 3 * (m - 1) * comb(N, r)
    nc = (4 * comb(N, 2)
          + 10 * (m - 1) * comb(N, r)
          + 3 ** (s - 1) * kappa(N, r, s)
          + (N - 1 if gauge else 0))
    return nv, nc


def read_header(path):
    """Return (n_vars, n_clauses) from the DIMACS 'p cnf' line."""
    with open(path) as f:
        for line in f:
            if line.startswith("p cnf"):
                _, _, nv, nc = line.split()
                return int(nv), int(nc)
    raise ValueError("no 'p cnf' line in %s" % path)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", metavar="DIR",
                   help="compare against DIR/*.cnf")
    a = p.parse_args()

    print("%-16s %6s %6s %4s %10s %12s %12s"
          % ("instance", "N", "r", "s", "copies", "variables", "clauses"))
    rows = []
    for label, N, r, s, g in INSTANCES:
        nv, nc = counts(N, r, s, g)
        rows.append((label, nv, nc))
        print("%-16s %6d %6d %4d %10d %12d %12d"
              % (label, N, r, s, kappa(N, r, s), nv, nc))

    # the unresolved K_14 instance, reported in Section 6
    nv, nc = counts(14, 6, 2, False)
    print("%-16s %6d %6d %4d %10d %12d %12d"
          % ("K14_2K6_none", 14, 6, 2, kappa(14, 6, 2), nv, nc))
    print("c  (the instance actually run adds 1 scaling unit + 36 star-sorting"
          " clauses, for %d)" % (nc + 37))

    if not a.check:
        return 0

    print()
    bad = 0
    for label, nv, nc in rows:
        path = os.path.join(a.check, label + ".cnf")
        if not os.path.exists(path):
            print("MISSING  %s" % path)
            bad += 1
            continue
        fnv, fnc = read_header(path)
        ok = (fnv, fnc) == (nv, nc)
        print("%-8s %-16s file %d/%d  formula %d/%d"
              % ("OK" if ok else "MISMATCH", label, fnv, fnc, nv, nc))
        bad += 0 if ok else 1
    if bad:
        print("\n%d mismatch(es)" % bad)
    else:
        print("\nall %d files agree with equation (5.1)" % len(rows))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
