# Method and prior-art audit

## Defensible result

The 1885 pamphlet's Declaration labels and the known B2 plaintext support a
one-word displacement in the working enumeration after ordinary word 241 and
no later than word 246. They do not identify the missing word. In particular,
they contradict deleting `pursuing` (ordinary word 240): both B2 occurrences of
number 241 require `invariably`, initial `i`.

All five locally admissible deletion models—ordinary positions 242 through
246—produce the same B1 passage at positions 188–207:

`ABCDEFGHIIJKLMMNOHPP`

The central 17-character walk is `ABCDEFGHIIJKLMMNO`. This is prior art, not a
new decipherment and not readable B1 plaintext.

## Frozen descriptive statistic

The reported statistic is the maximum contiguous run over the entire decoded
B1 stream and both alphabet directions, where every adjacent letter either
repeats or advances one rank in the selected direction. An unresolved table
entry breaks a run. The observed maximum is 17 at B1 positions 188–204.

The statistic is necessarily post hoc because Gillogly published the passage in
1980. Monte Carlo results therefore calibrate one specified anomaly under one
specified null; they are not a prospective discovery probability and are not a
posterior probability that the papers are fraudulent.

## Researcher degrees of freedom

Any publication must disclose at least these choices:

1. The Declaration is selected because B2's published solution already names it.
2. The 1885 pamphlet transcription, a modern normalized text, or another
   historical edition can be used.
3. Hyphenation, apostrophes, headings, signatures, and the extra `a` before
   `new government` affect enumeration.
4. Sparse decade labels require an interpolation rule.
5. Overlapping labels require a collision policy.
6. Known B2 prose must be aligned to 762 cipher symbols; the local audit freezes
   edit costs and tie-breaking and retains conflicts.
7. The word deleted in the 242–246 interval is unidentifiable from observed B2
   symbols.
8. Later discontinuities at the duplicated 480 marker and near 630/670 prevent
   projecting a local shift through the complete table.
9. The walk definition chooses contiguity, both directions, repeated letters,
   one-rank steps, and a scan over every B1 start position.
10. The 17-character central run and alternative 20-character presentation are
    different reporting choices.
11. Twelve B1 positions remain unresolved under the parsed printed-label table.
12. The null may shuffle positions, number-type assignments, blocks, or generated
    ciphertexts; these test different chance mechanisms.
13. Allowing post hoc ±1 corrections to printed B1 numbers increases the
    reconstructed run from 17 to 20 with one edit and 21 with two edits. Those
    optimized forms are sensitivity demonstrations, not evidence.
14. The parser resolves overlapping printed-anchor intervals by last assignment.
    A frozen first-assignment sensitivity changes only B1 positions 127 and 155;
    both policies retain the same 17-character maximum at positions 188–204.

## Complete application artifact

`results.json` contains one row for each of B1's 520 positions under the
representative delete-246 model. Each row records the ciphertext number,
resolved Declaration word (or null), initial, and resolution status. Per-model
delta arrays encode every difference for the other four admissible models.
Only delete-242 differs from the representative, at B1 position 347.

## Prior-art reconciliation

- Carl Hammer analyzed B2's construction errors before the alphabet anomaly was
  published.
- James J. Gillogly published the raw B1 alphabet anomaly in 1980 and favored a
  fabrication explanation while retaining alternatives.
- Dorothy E. Denning printed and regularized Gillogly's sequence in 1982 while
  discussing possible errors.
- The Remington/Hill material available as a 1989 web reproduction published a
  piecewise B2 table and corrected B1 sequence.
- John C. King reconstructed the B2 key and reported stronger B1 anomalies in
  1993.
- Stephen M. Matyas Jr. located an omitted word after 241 and before 246, while
  stating that the exact omitted word was not knowable from the reconstruction.
- Todd D. Mateer independently reverse-engineered B2's table errors and argued
  that shared errors support common construction; he did not identify
  `pursuing`.
- Nick Pelling published the corrected 20-character B1 sequence and exact
  mappings in 2018, and separately summarized Matyas's interval.
- Joe Nickell's work supplies independent historical, linguistic, provenance,
  and authorship evidence for fabrication; it is not priority for the corrected
  B1 sequence or table reconstruction.

## Publication boundary

Safe description:

> We independently reproduce the B2-table displacement and corrected B1 alphabet
> anomaly, expose the unresolved five-word deletion interval, reject a specific
> `pursuing`-omission interpretation, and provide complete code, ambiguity
> records, sensitivity analyses, and modern chance calibrations.

Avoid claims that this work decrypts B1, discovers the corrected sequence,
identifies an omitted word, proves a unique author, or converts a post-hoc Monte
Carlo result into a probability that the Beale Papers are a hoax.

## Sources

- James J. Gillogly, “The Beale Cipher: A Dissenting Opinion,” *Cryptologia*
  4.2 (1980), 116–119: https://doi.org/10.1080/0161-118091854979
- Remington/Hill reconstructed table reproduction:
  https://thomasbeale.tripod.com/52EERemington.htm
- John C. King, “A Reconstruction of the Key to Beale Cipher Number Two,”
  *Cryptologia* 17.3 (1993), 305–317:
  https://doi.org/10.1080/0161-119391867971
- Nick Pelling, “Refining Beale Cipher B1's cipher table” (2018):
  https://ciphermysteries.com/2018/11/15/refining-beale-cipher-b1s-cipher-table
- Nick Pelling, “More notes on the Beale Ciphers” (2018):
  https://ciphermysteries.com/2018/12/16/more-notes-on-the-beale-ciphers
- Todd D. Mateer, “Cryptanalysis of Beale Cipher Number Two,” *Cryptologia*
  37.3 (2013), 215–232: https://doi.org/10.1080/01611194.2013.798517
- Joe Nickell, “Discovered: The Secret of Beale's Treasure,” *Virginia Magazine
  of History and Biography* 90.3 (1982), 310–324:
  https://www.jstor.org/stable/4248566
