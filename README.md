# Zero-sum Ramsey numbers of disjoint cliques modulo 3

Formulas, DRAT certificates and scripts supporting

> *Zero-sum Ramsey numbers of disjoint cliques modulo 3 and a counterexample to a
> conjecture of Caro and Provstgaard*, Utkarsh Singh, arXiv:XXXX.XXXXX.
> Archived at [doi:10.5281/zenodo.22847270](https://doi.org/10.5281/zenodo.22847270).

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

The certified proofs for R(2K_4) and R(3K_4) use gauge fixing (Lemma 2.2 of the paper, a one-line argument). The unreduced formula K13_3K4_none.cnf is included so that anyone can confirm R(3K₄) = 13 without that lemma.
## Contents

```
run_all.py       runs every check and prints a summary
make_cnf.py      regenerates all seven formulas
src/encode.py    builds Phi(N, sK_r)
src/counts.py    evaluates equation (5.1); does not import the encoder
src/check.py     independent decoder and checker
cnf/             the seven formulas
proofs/          DRAT certificates for the three UNSAT instances
logs/            solver and checker output
Makefile         the same targets, for anyone who prefers make
proofs/ holds the DRAT certificates for the three UNSAT instances in the paper. cnf/K13_3K4_none.cnf is the unreduced form of the K₁₃ instance; it was also solved and its proof checked (see Remark 5.2(e) of the paper), but that proof is not shipped because of its size (414 MB). It can be regenerated in about 40 minutes with make_cnf.py and CaDiCaL.
```

## Verify

Only Python 3 is needed for steps 1, 2 and 4; step 3 also needs
[drat-trim](https://github.com/marijnheule/drat-trim).

```sh
python3 run_all.py
```

That runs, in order:

1. **Clause counts** — every CNF file against equation (5.1) of the paper.
2. **Encoder validation** — the magic `K_4` really does avoid zero-sum copies.
3. **Proof replay** — `drat-trim` on the three certificates.
4. **Checksums** — regenerates `SHA256SUMS`.

Steps that cannot run are reported as SKIPPED rather than failing, so the script
is safe to run at any stage. `python3 make_cnf.py` regenerates the formulas from
scratch; the two `K_13` files take about a minute each.

Equivalent `make` targets are `make counts`, `make encoder`, `make verify`,
`make sums`, `make cnf`.

## What the certificates cover, and what they do not

The DRAT proofs remove any need to trust the **solver**. They do not cover the
**encoder**. Three checks address that, in increasing strength.

1. `src/counts.py` evaluates the closed forms of equation (5.1) and compares
   them against the `p cnf` header of every shipped file. It does not import
   `src/encode.py`, so an under-constrained encoding — a missing family of
   copies, say — appears here as a mismatch.
2. `src/check.py` verifies that the magic `K_4` of Construction 1.10, proved
   avoiding by hand in Lemma 3.1, really is avoiding on `K_7`, `K_9` and
   `K_12`. It enumerates copies by a different method from the encoder (ordered
   tuples deduplicated by canonical form, rather than increasing minima) and
   compares the count it reaches against the closed form, so a silently
   incomplete enumeration cannot pass. It is also run on `K_8` as a negative
   control, where `R(2K_3) = 8` means a zero-sum copy must exist: a checker that
   never reports failure proves nothing.
3. The same colouring must therefore satisfy `cnf/K7_2K3.cnf`,
   `cnf/K9_2K4.cnf` and `cnf/K12_3K4.cnf`, which are satisfiable; decoding their
   models with `python3 src/check.py --model` closes the loop.

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

CaDiCaL 3.0.1, drat-trim 2e3b2dc, Python 3.13.15, on Google Colab (x86-64 Linux).
Solver and checker output is in `logs/`.

## License

MIT for `src/`, `run_all.py` and `make_cnf.py`; CC-BY-4.0 for `cnf/`, `proofs/`
and `logs/`. See `LICENSE`.
