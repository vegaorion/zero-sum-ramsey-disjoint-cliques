# DRAT certificates

This folder holds the DRAT proofs of unsatisfiability for the three formulas
that give the upper bounds in the paper:

| file                  | formula                     | proves              | reduction |
| --------------------- | --------------------------- | ------------------- | --------- |
| `K8_2K3_none.drat`    | `cnf/K8_2K3_none.cnf`       | `R(2K_3, Z_3) <= 8`  | none      |
| `K10_2K4_gauge.drat`  | `cnf/K10_2K4_gauge.cnf`     | `R(2K_4, Z_3) <= 10` | Lemma 2.2 |
| `K13_3K4_gauge.drat`  | `cnf/K13_3K4_gauge.cnf`     | `R(3K_4, Z_3) <= 13` | Lemma 2.2 |

The matching lower bounds are proved by hand in the paper (Theorem 1.11), so
together with these certificates they give `R(2K_3, Z_3) = 8`,
`R(2K_4, Z_3) = 10` and `R(3K_4, Z_3) = 13`. "Lemma 2.2" is the gauge-fixing
lemma of the paper, a one-line argument valid because `r = 4` is `1 mod 3`.

The proofs were produced by CaDiCaL 3.0.1 and verified with drat-trim
(commit `2e3b2dc`). None uses RAT lemmas. Checksums are in `../SHA256SUMS`.

## Checking a proof

With [drat-trim](https://github.com/marijnheule/drat-trim) built:

    drat-trim ../cnf/K13_3K4_gauge.cnf K13_3K4_gauge.drat

A successful check ends with `s VERIFIED`. `python3 ../run_all.py` replays all
three and reports the results. drat-trim reads both text and binary DRAT.

A certificate removes the need to trust the solver, but not the encoder that
produced the formula; see "What the certificates cover, and what they do not"
in the main README.

## The unreduced K13 instance

`cnf/K13_3K4_none.cnf` is the same `K_13` question with no symmetry
reduction, so it does not rely on Lemma 2.2. It was also solved (about 32
minutes) and its DRAT proof verified (about 7 minutes); the log is in `../logs/`.
That proof is about 414 MB and is **not** included here. To regenerate and
check it:

    cadical ../cnf/K13_3K4_none.cnf K13_3K4_none.drat
    drat-trim ../cnf/K13_3K4_none.cnf K13_3K4_none.drat

CaDiCaL should report `s UNSATISFIABLE` and drat-trim `s VERIFIED`. Timings
will vary with hardware.
