# Independent verification: B3 Declaration-episode replication

Date: 2026-08-01

## Conclusion

**PASS.** A clean-room, read-only verifier reproduced the B3 extraction, the
pamphlet's printed Declaration mapping, the observed scan result, and both
99,999-trial null distributions exactly. The preregistered B3 replication is
negative: primary `p = 0.08728`, above the registered `0.01` threshold. The
full-stream descriptive statistic is also null-like (`p = 0.53406`).

## Cipher extraction

The verifier independently selected all decimal integers inside the sole
`smaller block` on physical pamphlet page 22 and obtained byte-for-byte the
stored B3 CSV:

- Page-source SHA-256: `35498941ad7efe25db7092c1e2cf1664f76cdc21b510df3d6bb340e2d960c9f9`
- B3 CSV SHA-256: `4cfc1bc51ba326de3c917762e857a35b7e7f2a3debc3daa70e67ba6b6128da46`
- 618 integers, 263 distinct labels, minimum 1, maximum 975
- Zero occurrences of printed label 501

The frozen result file SHA-256 is
`a0e385f875274e34dc81622ac4ea4b5833889cadf22cb72ca249f606b22a7509`.

## Declaration mapping and eligibility

The verifier rebuilt the mapping directly from pamphlet pages 17–20, including
their printed numeric anchors and numbering errors. Its complete mapping
metadata equals `results.json`. Within B3's 1–975 range, exactly 974 printed
indices are defined: every integer except 501. Consequently all 618 B3 symbols
are eligible for the registered decode.

## Observed statistic

Each B3 label was replaced by the lowercase initial of its printed-index
Declaration word. Across every contiguous 17-symbol window, the verifier
counted its 16 adjacent rank differences equal to 0 or +1.

- Maximum: 8 qualifying transitions
- Earliest maximizing window: B3 positions 151–167 (1-based)
- Window initials: `ccstttebawasttaaa`
- Qualifying transitions over all 617 stream transitions: 76

## Exact null reproduction

For each trial, Python `random.Random(20260801)` injected the 263 distinct B3
labels without replacement into the 974 eligible printed Declaration indices,
preserved the equality pattern, and recomputed the scan maximum and full-stream
total.

| Statistic | Exceedances | Plus-one p-value | Null-vector SHA-256 |
|---|---:|---:|---|
| 17-symbol scan maximum | 8,727 | 0.08728 | `e9ca7dad560b35f334440e49eadcc2d1449c1999eef2d9eb2427d067a711a528` |
| Full-stream total | 53,405 | 0.53406 | `b46b538e34f248d0f86f1fec06a7d6dc8e8e17ccf0256912e04a272c14562ce5` |

Both use 99,999 trials and the registered plus-one estimator.

## Reproduction

```sh
python3 analysis/b3_control/verify.py
```

The verifier imports neither the first-exposure runner nor the mapping
implementation. It does not write any frozen artifact and exits nonzero on a
mismatch.
