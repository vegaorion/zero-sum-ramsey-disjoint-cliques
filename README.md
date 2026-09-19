# Zero-sum Ramsey numbers of disjoint cliques modulo 3

Formulas, DRAT certificates and scripts supporting

> *Zero-sum Ramsey numbers of disjoint cliques modulo 3 and a counterexample to a
> conjecture of Caro and Provstgaard*, FIRSTNAME LASTNAME, arXiv:XXXX.XXXXX.
> Archived at [doi:10.5281/zenodo.XXXXXXX](https://doi.org/10.5281/zenodo.XXXXXXX).

`R(H, Z_3)` is the least `N` such that every colouring `c : E(K_N) -> Z_3`
admits a copy of `H` whose edge colours sum to zero. This repository supports
three values:

| value | upper bound from | reduction used |
|---|---|---|
| `R(2K_3, Z_3) = 8`  | `K8_2K3_none` UNSAT   | none |
| `R(2K_4, Z_3) = 10` | `K10_2K4_gauge` UNSAT | Lemma 2.2 |
| `R(3K_4, Z_3) = 13` | `K13_3K4_gauge` UNSAT | Lemma 2.2 |

The third refutes Conjecture 1 of Caro and Provstgaard, *J. Graph Theory* **32**
(1999) 207–216, which predicts `t(n+d) - d = 14`.

The matching lower bounds are proved by hand in the paper and depend on no
computation. `K13_3K4_none.cnf` is the unreduced form of the third instance, so
that value does not depend on Lemma 2.2 either.

## Contents

```
src/encode.py    builds Phi(N, sK_r)
src/counts.py    evaluates equation (5.1); does not import the encoder
src/check.py     independent decoder and checker
cnf/             the seven formulas
proofs/          DRAT certificates for the three UNSAT instances
logs/            solver and checker output
```

## Verify

```sh
make verify     # replay the three DRAT proofs with drat-trim   (~1 min)
make counts     # check every clause count against equation (5.1)
make encoder    # check the encoder admits known avoiding colourings
make check      # all three
make cnf        # regenerate every formula from scratch
make solve      # re-solve and re-emit the proofs
```

`make verify` needs only `drat-trim` and is sufficient to confirm the three
values. `sha256sum -c SHA256SUMS` checks file integrity.

## What the certificates cover, and what they do not

The DRAT proofs remove any need to trust the **solver**. They do not cover the
**encoder**. Three checks address that, in increasing strength:

1. `make counts` evaluates the closed forms of equation (5.1) and compares them
   against the `p cnf` header of every shipped file. `src/counts.py` does not
   import `src/encode.py`, so an under-constrained encoding — a missing family
   of copies, say — appears here as a mismatch.
2. `make encoder` checks that the magic `K_4` of Construction 1.14, proved
   avoiding by hand in Lemma 3.1, really is avoiding on `K_7`, `K_9` and
   `K_12`. `src/check.py` enumerates copies by a different method from the
   encoder (ordered tuples deduplicated by canonical form, rather than
   increasing minima) and compares the count it reaches against the closed
   form, so a silently incomplete enumeration cannot pass.
3. The same colouring must therefore satisfy `cnf/K7_2K3.cnf`,
   `cnf/K9_2K4.cnf` and `cnf/K12_3K4.cnf`, which are satisfiable; decoding
   their models with `src/check.py --model` closes the loop.

Only the variable numbering is shared between `check.py` and the encoder, which
is unavoidable — something has to read the model. It is re-derived in
`check.py` from the layout below rather than imported.

## The encoding

Section 5.1 of the paper gives this in full. For `H = sK_r` and `m = C(r,2)`:

- **Edges.** `x[e,a]` meaning `c(e) = a`, occupying the first `3*C(N,2)`
  variables: edge `i` in lexicographic order owns `3i+1, 3i+2, 3i+3`. One
  at-least-one clause and three pairwise exclusions, so 3 variables and 4
  clauses per edge.
- **Weights.** Per `r`-set `S`, a running-sum chain over its `m` edges in
  lexicographic order, with states `y[S,i,a]` for `2 <= i <= m` and
  `y[S,1,a] := x[e_1,a]`. Per state one at-least-one clause and the nine
  implications `(-y[S,i-1,a] | -x[e_i,b] | y[S,i,a+b])`, so 3 variables and 10
  clauses. The weight of `S` is `y[S,m,.]`, built once and shared across every
  copy containing `S`.
- **Copies.** Per copy `{S_1,...,S_s}`, the `3^(s-1)` clauses of width `s`
  forbidding `sum_j w(S_j) = 0`.
- **Gauge fixing** (`gauge` suffix; valid only for `r = 1 mod 3`): the `N-1`
  unit clauses `x[0v,0]`, by Lemma 2.2.

No exclusion clauses are placed on the chain states. They are unnecessary for
the direction used in the paper: to conclude `R(H) <= N` from UNSAT it suffices
that every avoiding colouring extends to a model, and setting `y[S,i,a]` true
exactly when the partial sum is `a` does so.

## Environment

CaDiCaL VERSION, drat-trim COMMIT, Python VERSION, on CPU / RAM / OS.
Solver and checker output is in `logs/`.

## License

MIT for `src/`, CC-BY-4.0 for `cnf/`, `proofs/` and `logs/`. See `LICENSE`.
