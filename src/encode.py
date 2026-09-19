#!/usr/bin/env python3
"""
Build the CNF formula Phi(N, sK_r) described in Section 5.1 of

    Zero-sum Ramsey numbers of disjoint cliques modulo 3 and a counterexample
    to a conjecture of Caro and Provstgaard.

Phi(N, sK_r) is satisfiable iff some colouring c : E(K_N) -> Z_3 admits no
zero-sum copy of sK_r.  Hence UNSAT is equivalent to R(sK_r, Z_3) <= N.

Variables
    x[e,a]        c(e) = a,                     for each edge e of K_N
    y[S,i,a]      c(e_1)+...+c(e_i) = a,        for each r-subset S, 2 <= i <= m

where m = C(r,2) and e_1,...,e_m is the lexicographic ordering of the edges
inside S.  We set y[S,1,a] := x[e_1,a], so the chain introduces m-1 new states.
The weight of S is carried by y[S,m,.], built once per r-set and shared by every
copy containing it.

Clauses
    per edge          1 at-least-one + 3 pairwise exclusions          =  4
    per chain state   1 at-least-one + 9 implications                 = 10
    per copy          3^(s-1) clauses of width s forbidding sum = 0
    gauge fixing      N-1 units (only when r = 1 mod 3)

No exclusion clauses are placed on the chain states.  They are unnecessary for
the direction used in the paper: to conclude R(H) <= N from UNSAT it suffices
that every avoiding colouring extends to a model, and setting y[S,i,a] true
exactly when the partial sum equals a does so.

Usage
    python3 src/encode.py --N 13 --r 4 --s 3 --reduction gauge -o out.cnf
"""

import argparse
import sys
from itertools import combinations
from math import comb


# --------------------------------------------------------------------------
# indexing
# --------------------------------------------------------------------------

def edge_index(N):
    """Lexicographic index of each edge of K_N."""
    return {e: i for i, e in enumerate(combinations(range(N), 2))}


def rset_index(N, r):
    """Lexicographic index of each r-subset of V(K_N)."""
    return {S: i for i, S in enumerate(combinations(range(N), r))}


class Vars:
    def __init__(self, N, r):
        self.N, self.r = N, r
        self.m = comb(r, 2)
        self.eidx = edge_index(N)
        self.sidx = rset_index(N, r)
        self.n_edge_vars = 3 * comb(N, 2)

    def x(self, e, a):
        """Variable for c(e) = a.  e is a sorted 2-tuple."""
        return 3 * self.eidx[e] + a % 3 + 1

    def y(self, S, i, a):
        """Variable for the i-th partial sum of S being a.  1 <= i <= m."""
        if i == 1:
            edges = list(combinations(S, 2))
            return self.x(edges[0], a)
        t = self.sidx[S]
        off = (self.m - 1) * t + (i - 2)
        return self.n_edge_vars + 3 * off + a % 3 + 1

    def total(self):
        return self.n_edge_vars + 3 * (self.m - 1) * comb(self.N, self.r)


# --------------------------------------------------------------------------
# copies of sK_r
# --------------------------------------------------------------------------

def copies(N, r, s):
    """
    Yield every copy of sK_r in K_N exactly once, as a tuple of s sorted
    r-tuples.  Canonical form: the minima of the parts strictly increase, which
    picks one representative per unordered family.
    """
    verts = list(range(N))

    def rec(avail, k, last_min):
        if k == 0:
            yield ()
            return
        # need k*r vertices left
        if len(avail) < k * r:
            return
        for S in combinations(avail, r):
            if S[0] <= last_min:
                continue
            rest = [v for v in avail if v not in S]
            for tail in rec(rest, k - 1, S[0]):
                yield (S,) + tail

    yield from rec(verts, s, -1)


def n_copies(N, r, s):
    """Closed form for the number of copies of sK_r in K_N."""
    total = 1
    for j in range(s):
        total *= comb(N - j * r, r)
    for j in range(2, s + 1):
        total //= j
    return total


# --------------------------------------------------------------------------
# encoding
# --------------------------------------------------------------------------

def build(N, r, s, reduction="none"):
    """Return (clauses, n_vars).  clauses is a list of lists of ints."""
    if r < 3:
        sys.exit("r must be at least 3")
    if s < 1:
        sys.exit("s must be at least 1")
    if s * r > N:
        sys.exit("need N >= s*r")

    V = Vars(N, r)
    m = V.m
    cls = []

    # --- edges: exactly one colour ------------------------------------------
    for e in combinations(range(N), 2):
        cls.append([V.x(e, 0), V.x(e, 1), V.x(e, 2)])
        for a, b in ((0, 1), (0, 2), (1, 2)):
            cls.append([-V.x(e, a), -V.x(e, b)])

    # --- weight chains -------------------------------------------------------
    for S in combinations(range(N), r):
        edges = list(combinations(S, 2))
        for i in range(2, m + 1):
            cls.append([V.y(S, i, 0), V.y(S, i, 1), V.y(S, i, 2)])
            ei = edges[i - 1]
            for a in range(3):
                for b in range(3):
                    cls.append([-V.y(S, i - 1, a), -V.x(ei, b),
                                V.y(S, i, (a + b) % 3)])

    # --- copies: forbid zero sum --------------------------------------------
    def assignments(k):
        if k == 0:
            yield ()
            return
        for head in range(3):
            for tail in assignments(k - 1):
                yield (head,) + tail

    for copy in copies(N, r, s):
        for pre in assignments(s - 1):
            last = (-sum(pre)) % 3
            vals = pre + (last,)
            cls.append([-V.y(S, m, a) for S, a in zip(copy, vals)])

    # --- gauge fixing --------------------------------------------------------
    if reduction == "gauge":
        if r % 3 != 1:
            sys.exit("gauge fixing requires r = 1 (mod 3); see Lemma 2.2")
        for v in range(1, N):
            cls.append([V.x((0, v), 0)])
    elif reduction != "none":
        sys.exit("unknown reduction: %s" % reduction)

    return cls, V.total()


def write_dimacs(path, cls, n_vars, header=None):
    with open(path, "w") as f:
        if header:
            for line in header:
                f.write("c %s\n" % line)
        f.write("p cnf %d %d\n" % (n_vars, len(cls)))
        for c in cls:
            f.write(" ".join(map(str, c)) + " 0\n")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--N", type=int, required=True)
    p.add_argument("--r", type=int, required=True)
    p.add_argument("--s", type=int, required=True)
    p.add_argument("--reduction", default="none", choices=["none", "gauge"])
    p.add_argument("-o", "--out", required=True)
    a = p.parse_args()

    cls, nv = build(a.N, a.r, a.s, a.reduction)
    hdr = ["Phi(K_%d, %dK_%d), reduction=%s" % (a.N, a.s, a.r, a.reduction),
           "copies: %d" % n_copies(a.N, a.r, a.s),
           "UNSAT is equivalent to R(%dK_%d, Z_3) <= %d" % (a.s, a.r, a.N)]
    write_dimacs(a.out, cls, nv, hdr)
    print("%s: %d variables, %d clauses" % (a.out, nv, len(cls)))


if __name__ == "__main__":
    main()
