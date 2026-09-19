# Certificates

Four instances were solved and certified. Three proofs are here:

| proof | certifies |
|---|---|
| `K8_2K3_none.drat`    | `R(2K_3, Z_3) <= 8`, no symmetry reduction |
| `K10_2K4_gauge.drat`  | `R(2K_4, Z_3) <= 10`, gauge fixing (Lemma 2.2) |
| `K13_3K4_gauge.drat`  | `R(3K_4, Z_3) <= 13`, gauge fixing (Lemma 2.2) |

A fourth, `K13_3K4_none.drat`, certifies `R(3K_4, Z_3) <= 13` from the
*unreduced* formula `cnf/K13_3K4_none.cnf`, so that the counterexample to
Caro–Provstgaard depends on no auxiliary result at all. CaDiCaL solved it in
1905 s and drat-trim verified it in 439 s. The proof is too large for GitHub
even compressed and is available only in the Zenodo archive linked from the
top-level README.

Anyone with CaDiCaL can regenerate it:

    python3 make_cnf.py
    cadical --no-binary cnf/K13_3K4_none.cnf proofs/K13_3K4_none.drat
    drat-trim cnf/K13_3K4_none.cnf proofs/K13_3K4_none.drat
