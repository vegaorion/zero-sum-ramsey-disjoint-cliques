#!/usr/bin/env python3
"""
Independent re-check of a satisfying assignment, for Remark 5.2(b).

Given a model of Phi(N, sK_r), decode the edge colouring and verify directly
that no copy of sK_r is zero-sum.  This script shares no logic with
src/encode.py: it enumerates copies by a different method (ordered tuples of
disjoint r-sets, deduplicated through a set of canonical forms) and recomputes
every weight from scratch.  It also compares the number of copies it enumerated
against the closed form, so a silently incomplete enumeration cannot pass.

It can also check the explicit colouring of Construction 1.14 -- the magic K_4,
proved avoiding by hand in Lemma 3.1 -- which is what validates the encoder in
Remark 5.2(a).

Only the variable numbering is shared with the encoder, which is unavoidable:
something has to read the model.  It is re-derived here from the layout
documented in the README rather than imported.

Usage
    python3 src/check.py --N 7 --r 3 --s 2 --model logs/K7_2K3.sol
    python3 src/check.py --N 7 --r 3 --s 2 --magic 0,1,2,3
"""

import argparse
import sys
from itertools import combinations
from math import comb


# --------------------------------------------------------------------------
# reading a model
# --------------------------------------------------------------------------

def read_model(path):
    """Read DIMACS 'v' lines (or a bare list of literals) into a set of true vars."""
    lits = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line[0] in "cs":
                continue
            if line[0] == "v":
                line = line[1:]
            lits.extend(int(t) for t in line.split() if t.lstrip("-").isdigit())
    return {v for v in lits if v > 0}


def decode_colouring(N, true_vars):
    """
    Edge variables occupy the first 3*C(N,2) slots: edge i in lexicographic
    order owns 3i+1, 3i+2, 3i+3 for colours 0, 1, 2.
    """
    colour = {}
    for i, e in enumerate(combinations(range(N), 2)):
        got = [a for a in range(3) if 3 * i + a + 1 in true_vars]
        if len(got) != 1:
            sys.exit("edge %s has %d colours in the model; expected exactly 1"
                     % (str(e), len(got)))
        colour[e] = got[0]
    return colour


def magic_k4(N, D):
    """Construction 1.14: the 4-cycle d1 d2 d4 d3 gets colour 1, the matching
    {d1 d4, d2 d3} gets colour 2, everything else 0."""
    if len(D) != 4 or len(set(D)) != 4:
        sys.exit("--magic needs four distinct vertices")
    d1, d2, d3, d4 = D
    special = {tuple(sorted((d1, d2))): 1,
               tuple(sorted((d1, d3))): 1,
               tuple(sorted((d1, d4))): 2,
               tuple(sorted((d2, d3))): 2,
               tuple(sorted((d2, d4))): 1,
               tuple(sorted((d3, d4))): 1}
    return {e: special.get(e, 0) for e in combinations(range(N), 2)}


# --------------------------------------------------------------------------
# independent enumeration
# --------------------------------------------------------------------------

def weight(S, colour):
    return sum(colour[e] for e in combinations(sorted(S), 2)) % 3


def kappa(N, r, s):
    total = 1
    for j in range(s):
        total *= comb(N - j * r, r)
    for j in range(2, s + 1):
        total //= j
    return total


def all_copies(N, r, s):
    """
    Enumerate every copy of sK_r in K_N.  Method deliberately differs from the
    encoder's: build ordered tuples of pairwise-disjoint r-sets and deduplicate
    by canonical form.  Slower, but structurally independent.
    """
    seen = set()

    def rec(used, parts):
        if len(parts) == s:
            key = tuple(sorted(parts))
            if key not in seen:
                seen.add(key)
                yield key
            return
        for S in combinations([v for v in range(N) if v not in used], r):
            yield from rec(used | set(S), parts + [S])

    yield from rec(frozenset(), [])


def check(N, r, s, colour, verbose=False):
    expected = kappa(N, r, s)
    seen = 0
    zero = []
    for copy in all_copies(N, r, s):
        seen += 1
        w = sum(weight(S, colour) for S in copy) % 3
        if w == 0:
            zero.append(copy)
            if len(zero) > 3:
                break
    if seen != expected and not zero:
        print("FAIL: enumerated %d copies, closed form says %d"
              % (seen, expected))
        return 1
    print("copies enumerated: %d (closed form %d)%s"
          % (seen, expected, "" if seen == expected else "  [stopped early]"))
    if zero:
        print("FAIL: found a zero-sum copy, e.g. %s" % (zero[0],))
        return 1
    print("OK: no copy of %dK_%d in K_%d is zero-sum under this colouring"
          % (s, r, N))
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--N", type=int, required=True)
    p.add_argument("--r", type=int, required=True)
    p.add_argument("--s", type=int, required=True)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--model", help="file containing a DIMACS model")
    g.add_argument("--magic", help="comma-separated 4-set, e.g. 0,1,2,3")
    a = p.parse_args()

    if a.model:
        colour = decode_colouring(a.N, read_model(a.model))
        print("decoded a colouring of K_%d from %s" % (a.N, a.model))
    else:
        D = [int(t) for t in a.magic.split(",")]
        colour = magic_k4(a.N, D)
        print("magic K_4 of Construction 1.14 on D = %s inside K_%d"
              % (D, a.N))

    return check(a.N, a.r, a.s, colour)


if __name__ == "__main__":
    sys.exit(main())
