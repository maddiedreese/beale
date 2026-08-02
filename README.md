# The Beale Alphabet Is Real. Our Explanation Was Wrong.

We began this project intending to solve Beale Cipher No. 1 (B1). We did not
solve it. What we found instead is a reproducible investigation of a real
construction artifact, an attractive explanation that failed, and a narrower
result that survived independent checking.

[The 1885 pamphlet](https://commons.wikimedia.org/wiki/File:The_Beale_Papers.djvu)
claims that B1 locates buried treasure. Its second cipher
(B2) comes with an advertised plaintext and uses the Declaration of
Independence as a word-number key. When Declaration initials are applied to B1,
positions 188-204 contain the alphabet-like passage:

```text
ABCDEFGHIIJKLMMNO
```

The longer reconstructed presentation at positions 188-207 is:

```text
ABCDEFGHIIJKLMMNOHPP
```

Neither passage is a plaintext solution. Both are prior art.

## The investigation

1. We froze the 520 printed B1 numbers before testing keys.
2. We tested historically plausible political, legal, literary, and Masonic
   texts from early Virginia. None produced a qualifying B1 plaintext.
3. The Declaration reproduced [James Gillogly's 1980 alphabet anomaly](https://doi.org/10.1080/0161-118091854979).
4. Expanding the pamphlet's irregular decade labels strengthened the passage.
5. A duplicate assignment at printed label 240 made `pursuing` appear to be a
   newly identifiable omitted word.
6. The literature search showed that the anomaly, corrected run, B2-table
   reconstruction, and one-word displacement were all established earlier.
7. We then tested the `pursuing` interpretation with a deterministic B2
   known-plaintext alignment that preserves conflicting observations.
8. It failed.

[The conflict-preserving audit](verification/b2_table/results.json) shows that
B2 uses number 241 twice where the advertised plaintext requires `i`.
Retaining ordinary word 240, `pursuing`, leaves word 241 as
`invariably -> i`. Deleting `pursuing` moves `the -> t` into position 241 and
contradicts both observations.

The evidence supports one unidentified deletion among ordinary Declaration
positions 242-246:

```text
the / same / object / evinces / a
```

All five admissible models produce the identical 20-character B1 passage above
and the identical central 17-character walk. Across the complete 520-position
application they differ at only B1 position 347; the complete rows and deltas
are preserved in the [machine-readable result](verification/b2_table/results.json).

## What this project contributes

- a reproducible rejection of the `pursuing`-omission hypothesis;
- reduction to five locally admissible deletion models;
- proof that the alphabet passage is invariant across all five;
- deterministic conflict-preserving B2 known-plaintext alignment;
- complete position-by-position B1 application;
- an equality-pattern-preserving Monte Carlo calibration;
- correction-sensitivity analysis measuring researcher freedom; and
- a source-graded comparison with the previous literature.

We do **not** claim discovery of the alphabet passage, corrected B2 table,
one-word displacement, or hoax hypothesis.

## Statistical result and its limit

The fixed descriptive statistic is the longest contiguous run anywhere in the
decoded B1 stream, scanning both alphabet directions, where adjacent letters
may repeat or advance one rank.

| Quantity | Result |
|---|---:|
| Observed length | 17 |
| B1 positions | 188-204 |
| Equality-pattern null trials | 199,999 |
| Simulated runs reaching 17 | 0 |
| Add-one estimate | 0.000005 |
| Maximum simulated run | 10 |

The null permutes decoded initials across B1's 298 distinct number types and
reconstructs the stream from the unchanged equality pattern. A
[clean-room implementation](verification/b2_table/independent_verify.py)
reproduces the complete histogram exactly, and a separately written
[statistical and correction audit](verification/stat_correction/INDEPENDENT_AUDIT.md)
reproduces both analyses.

This statistic is **post hoc**: the alphabet passage has been known since
Gillogly published it in 1980. The estimate calibrates one specified anomaly
under one specified null. It is not the probability that the pamphlet is a
hoax.

Allowing optimized `+/-1` changes to printed B1 numbers lengthens the walk from
17 with no edits, to 20 with one edit, and 21 with two. Those longer fitted
forms demonstrate researcher freedom; they are not stronger evidence.

## Held-out B3 check

A preregistered attempt to reproduce a Declaration-conditioned alphabet
episode in B3 was negative: the 17-symbol scan gave `p = 0.08728`, and the
full-stream statistic gave `p = 0.53406`. A clean-room verifier reproduced the
extraction and both 99,999-trial distributions exactly. This does not weaken
the observed B1 artifact, but it supplies no evidence that B3 shares the same
episodic mechanism. See the [independent B3 report](analysis/b3_control/INDEPENDENT_VERIFICATION.md).

## Reproduce

Requires Python 3.11 or newer; the core analysis uses only the standard
library.

```sh
make verify-core
make verify-b3
make test
```

`make verify-core` regenerates the complete result, compares it byte-for-byte
with the frozen JSON, and runs the separately implemented 199,999-trial
verification. See [methods](docs/methods.md), [prior art](docs/prior_art.md),
and [limitations](docs/limitations.md).

## Conclusion

We did not solve B1, and this analysis alone does not prove fabrication. But
the known-plaintext dependence, shared B1/B2 construction artifacts,
conspicuous alphabet episode, irregular enumeration, absence of a recoverable
B1 message, and historical/provenance problems documented by
[Gillogly, Mateer, Nickell, Kruh, and others](docs/prior_art.md) collectively
make deliberate fabrication substantially more likely
than an authentic treasure-location cipher.

Falsifying our most attractive new explanation is part of the evidence for the
reliability of that narrower conclusion.

Research by **Maddie D. Reese**, with **significant assistance from OpenAI’s
Codex — GPT-5.6 Sol**. See [acknowledgments](ACKNOWLEDGMENTS.md).
