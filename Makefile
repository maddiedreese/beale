PYTHON ?= python3

.PHONY: test verify-sources verify-core verify-b3 verify-all checksums hygiene

test:
	$(PYTHON) -m unittest discover -v
	$(PYTHON) -m unittest discover -s verification/b2_table -p 'test_*.py' -v

verify-sources:
	$(PYTHON) provenance/verify_sources.py

verify-core:
	mkdir -p build
	$(PYTHON) verification/b2_table/audit.py --output build/results.json
	cmp build/results.json verification/b2_table/results.json
	$(PYTHON) verification/b2_table/independent_verify.py
	$(PYTHON) verification/stat_correction/verify.py

verify-b3:
	$(PYTHON) analysis/b3_control/verify.py

checksums:
	shasum -a 256 -c provenance/checksums.sha256

hygiene:
	test -z "$$(find . -type f -size +95M -not -path './.git/*' -print -quit)"
	! git grep -nE '(/Users/|/home/[^/]+/|[A-Za-z]:\\Users\\)' -- ':!Makefile'
	! git ls-files | grep -Ei '(^|/)(x[_-]?article|twitter[_-]?article|tweet[_-]?thread|social[_-]?draft)'

verify-all: checksums verify-sources test verify-core verify-b3 hygiene
