# Zero-sum Ramsey numbers of disjoint cliques modulo 3
#
#   make verify    replay the three DRAT proofs               (needs drat-trim)
#   make counts    check every clause count against eq. (5.1)
#   make encoder   check the encoder admits known colourings
#   make check     all three of the above
#   make cnf       regenerate every CNF from scratch
#   make solve     re-solve everything and re-emit proofs      (needs cadical)
#   make sums      regenerate SHA256SUMS
#   make clean     remove generated files

PY       ?= python3
SAT      ?= cadical
DRAT     ?= drat-trim

CERTIFIED = K8_2K3_none K10_2K4_gauge K13_3K4_gauge
ALLCNF    = $(CERTIFIED) K13_3K4_none K7_2K3 K9_2K4 K12_3K4

.PHONY: check verify counts encoder cnf solve sums clean

check: counts verify encoder

# -- verification ----------------------------------------------------------

verify:
	@for f in $(CERTIFIED); do \
	  printf '%-18s ' "$$f"; \
	  $(DRAT) cnf/$$f.cnf proofs/$$f.drat > logs/verify-$$f.log 2>&1 \
	    && grep -q 's VERIFIED' logs/verify-$$f.log \
	    && echo VERIFIED || { echo FAILED; exit 1; }; \
	done

counts:
	@$(PY) src/counts.py --check cnf

# The magic K_4 of Construction 1.14 is proved avoiding by hand in Lemma 3.1.
# It must therefore satisfy the formula on K_{N-1}; src/check.py re-derives that
# independently of the encoder.  See Remark 5.2(a),(b).
encoder:
	@$(PY) src/check.py --N 7  --r 3 --s 2 --magic 0,1,2,3
	@$(PY) src/check.py --N 9  --r 4 --s 2 --magic 0,1,2,3
	@$(PY) src/check.py --N 12 --r 4 --s 3 --magic 0,1,2,3

# -- regeneration ----------------------------------------------------------

cnf:
	@mkdir -p cnf
	$(PY) src/encode.py --N 8  --r 3 --s 2 --reduction none  -o cnf/K8_2K3_none.cnf
	$(PY) src/encode.py --N 10 --r 4 --s 2 --reduction gauge -o cnf/K10_2K4_gauge.cnf
	$(PY) src/encode.py --N 13 --r 4 --s 3 --reduction gauge -o cnf/K13_3K4_gauge.cnf
	$(PY) src/encode.py --N 13 --r 4 --s 3 --reduction none  -o cnf/K13_3K4_none.cnf
	$(PY) src/encode.py --N 7  --r 3 --s 2 --reduction none  -o cnf/K7_2K3.cnf
	$(PY) src/encode.py --N 9  --r 4 --s 2 --reduction gauge -o cnf/K9_2K4.cnf
	$(PY) src/encode.py --N 12 --r 4 --s 3 --reduction gauge -o cnf/K12_3K4.cnf

solve: cnf
	@mkdir -p proofs logs
	@for f in $(CERTIFIED); do \
	  echo "solving $$f"; \
	  $(SAT) cnf/$$f.cnf proofs/$$f.drat > logs/solve-$$f.log 2>&1 || true; \
	  grep -E '^s ' logs/solve-$$f.log; \
	done
	@for f in K7_2K3 K9_2K4 K12_3K4; do \
	  $(SAT) cnf/$$f.cnf > logs/solve-$$f.log 2>&1 || true; \
	  grep -E '^s ' logs/solve-$$f.log; \
	done

sums:
	@sha256sum cnf/*.cnf proofs/*.drat > SHA256SUMS
	@echo "wrote SHA256SUMS"

clean:
	rm -f cnf/*.cnf proofs/*.drat logs/*.log
