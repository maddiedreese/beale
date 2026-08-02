# Methods

## Frozen inputs

B1 is the 520-number stream printed under "The Locality of the Vault" in the
[1885 pamphlet](https://commons.wikimedia.org/wiki/File:The_Beale_Papers.djvu).
B2 contains 762 numbers. The included Wikisource transcriptions
are checked against the included public-domain scan; all evidentiary inputs are
bound by SHA-256 in `SOURCES.yml` and `provenance/checksums.sha256`. The
[source verifier](../provenance/verify_sources.py) extracts the exact labeled
blocks and checks all 1,282 integers.

## Three tables that must not be conflated

1. **Ordinary sequential table:** number every printed Declaration word in
   sequence.
2. **Printed-anchor expansion:** interpolate backward from the pamphlet's
   sparse printed decade labels. Overlaps are retained as an auditable
   collision before a policy is applied.
3. **Locally reconstructed working table:** infer number-to-initial constraints
   from the advertised B2 plaintext. This is known-plaintext reconstruction,
   not an independent decryption.

The pamphlet visibly contains `pursuing (240)`. The eleven-word group ending at
the next printed label produces a duplicate 240 under backward interpolation,
which initially suggested suppressing `pursuing`. That dictionary behavior is
not evidence that a historical worksheet omitted the word.

## Conflict-preserving B2 alignment

The [constraint audit](../verification/b2_table/audit.py) globally aligns:

- the B2 stream decoded by deterministic printed-anchor expansion; and
- the advertised B2 plaintext, normalized to lowercase A-Z.

Substitution cost is 1, gap cost is 2, and ties prefer diagonal, then
right-only, then left-only. No phrase is manually deleted. All 762 B2 symbols
are paired; ten plaintext letters are right-only. Repeated numbers that imply
different plaintext letters remain conflicts in `results.json` rather than
being silently forced to a majority value.

Number 241 has two unanimous `i` observations. Number 246 has three unanimous
`d` observations. B2 contains none of 242-245. Therefore a single deletion at
ordinary positions 242, 243, 244, 245, or 246 is locally admissible, while
deleting 240 (`pursuing`) or 241 (`invariably`) is not.

The candidate deletion is applied only through table label 466. Later printed
discontinuities, including the duplicated 480 region and irregular intervals
near 630 and 670, are parsed from their own anchors rather than pretending the
local shift continues indefinitely, consistent with distinct irregularities
documented by [Mateer (2013)](https://doi.org/10.1080/01611194.2013.798517).

Overlapping anchor intervals use a frozen last-assignment-wins policy. A
first-assignment sensitivity changes only B1 positions 127 and 155; both retain
the same 17-character walk. The exact differing labels, words, and B1 rows are
recorded in [results.json](../verification/b2_table/results.json).

## B1 application

Every admissible local table is applied to all 520 B1 positions. The five
models agree at positions 188-207 on `abcdefghiijklmmnohpp`, share the same
17-character walk at 188-204, and disagree only at B1 position 347 outside the
passage. Twelve B1 positions are unresolved by the parsed table and break a
run. The representative model's 520 position rows and every per-model delta are
included in [results.json](../verification/b2_table/results.json).

## Descriptive statistic

For each direction `d` in `{+1, -1}`, scan the complete decoded B1 stream. A
run continues when the next alphabet rank differs from the previous rank by
either 0 or `d`. The reported family statistic is the maximum over every start
position and both directions. The observed value is 17.

This definition was fixed for the present audit but was formulated after the
historical anomaly was known. It is descriptive and post hoc.

## Equality-pattern-preserving null

B1 contains 298 distinct number types. Each trial permutes the representative
table's decoded initials, including unresolved barriers, across those 298
types. The original 520-position type pattern is then reconstructed. This
preserves every equality relation caused by repeated numbers while randomizing
which decoded initial belongs to each number type.

With seed 20260801, 0 of 199,999 trials reached 17. The add-one estimate is
`(0+1)/(199999+1) = 0.000005`; the largest null value is 10. A separate script
that imports none of the audit code reproduces every histogram count; see the
[independent verifier](../verification/b2_table/independent_verify.py) and its
[second independent audit](../verification/stat_correction/INDEPENDENT_AUDIT.md).

## Correction sensitivity

After observing B1, the sensitivity analysis allows at most `k` positions in a
candidate run to replace printed number `n` with `n-1` or `n+1`, scanning every
start and both directions. Under the piecewise table the optimized maxima are
17, 20, and 21 for budgets 0, 1, and 2. This quantifies the benefit of
post-exposure editing and is not a corrected ciphertext proposal.
