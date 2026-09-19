#!/usr/bin/env python3
"""
run_all.py  --  press Run.  No arguments needed.

Runs every check in the repository and prints a summary.

  1. clause counts       every CNF file against equation (5.1) of the paper
  2. encoder validation  the magic K_4 really avoids zero-sum copies
  3. proof replay        drat-trim on the three DRAT certificates, if installed
  4. checksums           regenerates SHA256SUMS

Steps that cannot run (missing files, drat-trim not installed) are reported as
SKIPPED rather than failing, so the script is safe to run at any stage of
setting the repository up.
"""

import hashlib
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))

import check as chk      # noqa: E402
import counts as cnt     # noqa: E402

CERTIFIED = ["K8_2K3_none", "K10_2K4_gauge", "K13_3K4_gauge", "K13_3K4_none"]
COMPANIONS = [("K7_2K3", 7, 3, 2), ("K9_2K4", 9, 4, 2), ("K12_3K4", 12, 4, 3)]

results = []


def banner(n, title):
    print()
    print("=" * 70)
    print("  %d. %s" % (n, title))
    print("=" * 70)


def record(name, ok, note=""):
    results.append((name, ok, note))


# ---------------------------------------------------------------- 1. counts
def step_counts():
    banner(1, "Clause counts against equation (5.1)")
    cnfdir = os.path.join(HERE, "cnf")
    print("%-16s %6s %6s %4s %10s %12s %12s"
          % ("instance", "N", "r", "s", "copies", "variables", "clauses"))
    for label, N, r, s, g in cnt.INSTANCES:
        nv, nc = cnt.counts(N, r, s, g)
        print("%-16s %6d %6d %4d %10d %12d %12d"
              % (label, N, r, s, cnt.kappa(N, r, s), nv, nc))
    print()

    if not os.path.isdir(cnfdir) or not os.listdir(cnfdir):
        print("cnf/ is empty -- run make_cnf.py, or add your own files.")
        record("clause counts", None, "no CNF files present")
        return

    bad = missing = 0
    for label, N, r, s, g in cnt.INSTANCES:
        path = os.path.join(cnfdir, label + ".cnf")
        nv, nc = cnt.counts(N, r, s, g)
        if not os.path.exists(path):
            print("  MISSING   %s.cnf" % label)
            missing += 1
            continue
        fnv, fnc = cnt.read_header(path)
        if (fnv, fnc) == (nv, nc):
            print("  OK        %-16s %d vars, %d clauses" % (label, fnv, fnc))
        else:
            print("  MISMATCH  %-16s file %d/%d, formula says %d/%d"
                  % (label, fnv, fnc, nv, nc))
            bad += 1
    record("clause counts", bad == 0,
           "%d missing" % missing if missing else "")


# ------------------------------------------------------- 2. encoder validation
def step_encoder():
    banner(2, "Encoder validation: the magic K_4 avoids zero-sum copies")
    print("Construction 1.14 is proved avoiding by hand in Lemma 3.1.  Here it")
    print("is re-checked by exhaustive enumeration, independently of the")
    print("encoder.  These are the lower bounds of Theorem 3.3(ii),(iii).")
    print()
    ok = True
    for label, N, r, s in COMPANIONS:
        colour = chk.magic_k4(N, [0, 1, 2, 3])
        rc = chk.check(N, r, s, colour)
        print()
        ok = ok and rc == 0

    print("Negative control: the same colouring on K_8, where R(2K_3) = 8")
    print("means a zero-sum copy MUST exist.")
    rc = chk.check(8, 3, 2, chk.magic_k4(8, [0, 1, 2, 3]))
    control = (rc == 1)
    print("  control %s" % ("passed (failure found, as expected)" if control
                            else "FAILED -- the checker never reports failure"))
    record("encoder validation", ok and control)


# ------------------------------------------------------------ 3. proof replay
def step_proofs():
    banner(3, "Replaying the DRAT certificates")
    drat = shutil.which("drat-trim")
    if drat is None:
        print("drat-trim is not on the PATH -- skipping.")
        print("Install it from https://github.com/marijnheule/drat-trim")
        record("proof replay", None, "drat-trim not installed")
        return
    logs = os.path.join(HERE, "logs")
    os.makedirs(logs, exist_ok=True)
    ok, ran = True, 0
    for stem in CERTIFIED:
        c = os.path.join(HERE, "cnf", stem + ".cnf")
        p = os.path.join(HERE, "proofs", stem + ".drat")
        if not (os.path.exists(c) and os.path.exists(p)):
            print("  SKIP      %s (cnf or proof missing)" % stem)
            continue
        ran += 1
        print("  checking  %s ..." % stem, end="", flush=True)
        out = subprocess.run([drat, c, p], capture_output=True, text=True)
        with open(os.path.join(logs, "verify-%s.log" % stem), "w") as f:
            f.write(out.stdout + out.stderr)
        good = "s VERIFIED" in out.stdout
        print(" VERIFIED" if good else " FAILED")
        ok = ok and good
    if ran == 0:
        record("proof replay", None, "no proof files present")
    else:
        record("proof replay", ok)


# --------------------------------------------------------------- 4. checksums
def step_sums():
    banner(4, "Checksums")
    lines = []
    for sub in ("cnf", "proofs"):
        d = os.path.join(HERE, sub)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith((".cnf", ".drat")):
                continue
            h = hashlib.sha256()
            with open(os.path.join(d, name), "rb") as f:
                for blk in iter(lambda: f.read(1 << 20), b""):
                    h.update(blk)
            lines.append("%s  %s/%s" % (h.hexdigest(), sub, name))
    if not lines:
        print("nothing to hash yet -- skipping.")
        record("checksums", None, "no files")
        return
    with open(os.path.join(HERE, "SHA256SUMS"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote SHA256SUMS covering %d file(s)" % len(lines))
    record("checksums", True)


# --------------------------------------------------------------------- main
def main():
    step_counts()
    step_encoder()
    step_proofs()
    step_sums()

    banner(5, "Summary")
    failed = 0
    for name, ok, note in results:
        if ok is None:
            tag = "SKIPPED"
        elif ok:
            tag = "PASS"
        else:
            tag = "FAIL"
            failed += 1
        print("  %-8s %-22s %s" % (tag, name, note))
    print()
    if failed:
        print("%d step(s) failed." % failed)
    else:
        print("No failures.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
