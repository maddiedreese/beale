# B2 table constraint audit

This directory reconstructs observable B2 number-to-letter constraints from the
published B2 plaintext using a fully specified global alignment. It does not
claim an independent B2 decryption and does not force conflicting observations
to agree.

The principal result is negative: the local one-word displacement cannot be
identified with `pursuing`. B2 number 241 requires `invariably` twice. The data
support deletion of one unidentified ordinary Declaration word at positions
242–246; all five models produce the same B1 alphabet episode.

The candidate deletion is applied only through table label 466. It is not
projected through the later duplicated-480 and 630/670 discontinuities; outside
the local band, the complete-B1 comparison uses the separately parsed pamphlet
anchor table. Overlapping anchor intervals use an explicit last-assignment-wins
policy, and the output also reports the first-assignment alternative. The two
policies change only B1 positions 127 and 155 and leave the alphabet episode
unchanged.

Run the full audit from the workspace root:

```sh
python3 verification/b2_table/audit.py
```

Run the quick test suite:

```sh
python3 -m unittest discover -s verification/b2_table -p 'test_*.py' -v
```

Replicate the complete equality-pattern null with an implementation that imports
none of the analysis code:

```sh
python3 verification/b2_table/independent_verify.py
```

The generated `results.json` records input hashes, alignment rules, all inferred
constraints and conflicts, every local deletion candidate, complete-B1 results,
all 520 representative position rows, per-model deltas, collision-policy and
edition sensitivity, and the equality-pattern-preserving Monte Carlo control.
