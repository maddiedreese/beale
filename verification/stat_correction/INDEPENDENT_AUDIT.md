# Independent audit: B1 walk calibration and correction sensitivity

## Verdict

**PASS**, within the explicitly specified representative table and null model.

A standalone implementation that imports no project analysis module reproduces
the complete representative B1 decode hash, the observed alphabet-walk
statistic, the exact seeded Monte Carlo histogram, and the optimized ±1-edit
lengths.

The verified descriptive result is a forward run of length 17 at one-based B1
positions 188–204:

`ABCDEFGHIIJKLMMNO`

The result is necessarily **post hoc**: the alphabet passage was already known
before the statistic and null were specified. The Monte Carlo result calibrates
this statistic under this null. It is not the probability that the Beale Papers
are fraudulent and is not evidence that the longer edit-optimized strings are
authentic corrections.

## Clean-room method

`verify.py` independently:

1. parses the frozen pamphlet transcription on pages 17–20;
2. expands its sparse printed number anchors;
3. builds the representative admissible local table by deleting ordinary word
   246 only inside labels 240–466;
4. applies that table position by position to the frozen 520-number B1 stream;
5. scans the whole decoded stream in both alphabet directions, allowing an
   adjacent letter to repeat or advance one rank and treating `?` as a barrier;
6. assigns the table initials to B1's 298 distinct number types, randomly
   permutes those assignments while preserving B1's complete equality pattern,
   and repeats the scan for 199,999 seeded trials; and
7. independently scans every start position and both directions with an
   exhaustive reachable-state search allowing at most zero, one, or two ±1
   number substitutions.

The edit search is structurally different from the primary implementation: it
starts a search at every B1 position and retains every reachable
`(last letter, edits spent)` state until the run cannot continue. It therefore
checks the claimed global maxima rather than merely evaluating the previously
reported witnesses.

## Reproduced outputs

| Quantity | Independent result |
|---|---:|
| Observed maximum | 17 |
| Position interval | 188–204 |
| Text | `abcdefghiijklmmno` |
| Distinct B1 number types | 298 |
| Monte Carlo trials | 199,999 |
| Runs at least 17 | 0 |
| Add-one estimate | 0.000005 |
| Largest simulated run | 10 |

The independent histogram is exactly:

| Length | Count |
|---:|---:|
| 2 | 26 |
| 3 | 55,871 |
| 4 | 109,304 |
| 5 | 28,938 |
| 6 | 4,867 |
| 7 | 828 |
| 8 | 136 |
| 9 | 25 |
| 10 | 4 |

This histogram, the zero exceedances, and the add-one estimate exactly match
`verification/b2_table/results.json` under seed 20260801.

The correction-freedom scan independently gives:

| Maximum edit budget | Optimized length | Witness interval | Witness |
|---:|---:|---:|---|
| 0 | 17 | 188–204 | `abcdefghiijklmmno` |
| 1 | 20 | 188–207 | `abcdefghiijklmmnoopp` |
| 2 | 21 | 188–208 | `abcdefghiijklmmnooppp` |

The one-edit witness changes B1 position 205 from number 301 to 302. The
two-edit witness additionally changes position 208 from 680 to 681. These are
optimized after inspecting the anomaly. The 20- and 21-character forms therefore
measure researcher freedom; they are not stronger statistical evidence than the
unaltered 17-character run.

## Equality and provenance checks

The independently decoded 520-character representative stream has SHA-256:

`68c570b80007149c241af2f9a149fe15bf9f4b5c28dcf220aa4bd52b35547dd0`

This exactly equals the primary report's representative decoded hash. Frozen
inputs used by the independent implementation are:

| Input | SHA-256 |
|---|---|
| `data/beale1_1885.csv` | `0e63242041b03717a96340fde86af10f895355b936b4120da1769e9f2f7e3d27` |
| `sources/page_17.wikitext` | `b3b41de785cae4fb1f25f849c6a61f2fb17da0cb8cec7784a094ac150a23588f` |
| `sources/page_18.wikitext` | `439683edf0a52ce398eaca05e15f3cbac3e03f6dfb3ec291ba72746a33372cf0` |
| `sources/page_19.wikitext` | `1f88c40b384200ed63714171216fe681da7bc570f7e5bf5a936bb6078d3c5004` |
| `sources/page_20.wikitext` | `50133deddbf80fd81a9664742c8526f5381f803416db80e207719434d4c2bee8` |

## Scope and limitations

The null preserves:

- the 520-position B1 equality pattern;
- each number type's multiplicity and positions;
- the multiset of assigned table initials across the 298 distinct number
  types; and
- unresolved assignments as barriers.

It does not preserve number magnitude, neighboring Declaration words, or any
historical generative process. Other defensible nulls answer different
questions. Exact agreement here means exact reproduction of the frozen seeded
experiment, not independent prospective discovery.

The calibration uses the representative deletion-at-246 model. The separate
B2-table audit establishes that the central 188–204 passage is invariant under
all five locally admissible models; this audit did not re-prove the B2
known-plaintext admissibility argument.

One packaging issue was observed: the existing `test_audit.py` imports `audit`
as a top-level module, so `python3 -m unittest verification.b2_table.test_audit`
from the workspace root fails. Running the documented test from
`verification/b2_table` passes all six tests. This does not alter the numerical
findings but should be corrected or documented in the publication repository.

## Reproduction

From the workspace root:

```sh
python3 verification/stat_correction/verify.py
```

The script writes `verification/stat_correction/independent_results.json` and
exits nonzero unless every headline claim and the exact comparison with the
primary result pass.

At audit completion:

- `verify.py` SHA-256:
  `d7c1a3dad2ec1c4e250e44a43bdcf2832171355702948a80118286c060f14428`
- `independent_results.json` SHA-256:
  `768acbc44e6b95b2226cc4104a806c053c3990b54ce905caaf46e40bafe32501`

