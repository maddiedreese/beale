#!/usr/bin/env python3
"""Deterministic audit of the B2-derived table and its consequences for B1.

This is a known-plaintext reconstruction, not an independent decryption of B2.
Every alignment rule, tie-break, candidate deletion, and null model is explicit.
Ambiguous or conflicting observations are retained in the output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name("results.json")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_numbers(path: Path) -> list[int]:
    return [int(value) for value in re.findall(r"\d+", path.read_text())]


def declaration_words() -> list[str]:
    paths = [ROOT / "sources" / f"page_{page}.wikitext" for page in range(17, 21)]
    raw = " ".join(path.read_text() for path in paths)
    raw = raw[raw.index("{{dual|1|When,") : raw.index("The letter, or paper")]
    raw = re.sub(r"<noinclude>.*?</noinclude>", " ", raw, flags=re.S)
    raw = re.sub(
        r"\{\{dual\|\d+\|([^}|]+)(?:\|[^}]*)?\}\}",
        lambda match: " " + match.group(1) + " ",
        raw,
    )
    raw = re.sub(r"\{\{[^{}]*\}\}", " ", raw)
    return re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)?", raw)


def printed_anchor_mapping(collision_policy: str = "last") -> dict[int, str]:
    """Expand printed decade anchors with an explicit overlap policy.

    The pamphlet contains overlapping/duplicated anchor intervals.  ``last``
    preserves the historical parser's assignment order; ``first`` provides a
    frozen sensitivity check rather than silently resolving those collisions.
    """

    if collision_policy not in {"first", "last"}:
        raise ValueError("collision_policy must be 'first' or 'last'")
    paths = [ROOT / "sources" / f"page_{page}.wikitext" for page in range(17, 21)]
    raw = " ".join(path.read_text() for path in paths)
    raw = raw[raw.index("{{dual|1|When,") : raw.index("The letter, or paper")]
    raw = re.sub(r"<noinclude>.*?</noinclude>", " ", raw, flags=re.S)
    raw = re.sub(
        r"\{\{dual\|(\d+)\|([^}|]+)(?:\|[^}]*)?\}\}",
        lambda match: f" {match.group(2)} ({match.group(1)}) ",
        raw,
    )
    raw = re.sub(r"\{\{[^{}]*\}\}", " ", raw)
    tokens = re.findall(r"\((\d+)\)|([A-Za-z]+(?:['’][A-Za-z]+)?)", raw)

    mapping: dict[int, str] = {}
    pending: list[str] = []
    for number, word in tokens:
        if word:
            pending.append(word)
            continue
        anchor = int(number)
        first = anchor - len(pending) + 1
        for label, item in enumerate(pending, first):
            if collision_policy == "first" and label in mapping:
                continue
            mapping[label] = item
        pending.clear()
    if pending:
        first = max(mapping) + 1
        mapping.update({label: word for label, word in enumerate(pending, first)})
    return mapping


def decode(numbers: list[int], mapping: dict[int, str]) -> str:
    return "".join(mapping[number][0].lower() if number in mapping else "?"
                   for number in numbers)


def global_alignment(left: str, right: str) -> dict:
    """Globally align two strings with a frozen edit metric.

    Substitution costs 1 and either gap costs 2. Ties prefer diagonal,
    then a character present only in ``right``, then one present only in
    ``left``. This deliberately discourages using gaps to conceal table errors.
    """

    n, m = len(left), len(right)
    scores = [[0] * (m + 1) for _ in range(n + 1)]
    back = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        scores[i][0] = 2 * i
        back[i][0] = 2
    for j in range(1, m + 1):
        scores[0][j] = 2 * j
        back[0][j] = 1

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            candidates = (
                scores[i - 1][j - 1] + (left[i - 1] != right[j - 1]),
                scores[i][j - 1] + 2,
                scores[i - 1][j] + 2,
            )
            choice = min(range(3), key=lambda index: (candidates[index], index))
            scores[i][j] = candidates[choice]
            back[i][j] = choice

    pairs: list[tuple[int, int]] = []
    right_only: list[int] = []
    left_only: list[int] = []
    i, j = n, m
    while i or j:
        choice = back[i][j]
        if i and j and choice == 0:
            pairs.append((i - 1, j - 1))
            i -= 1
            j -= 1
        elif j and (not i or choice == 1):
            right_only.append(j - 1)
            j -= 1
        else:
            left_only.append(i - 1)
            i -= 1
    pairs.reverse()
    right_only.reverse()
    left_only.reverse()
    return {
        "score": scores[n][m],
        "pairs": pairs,
        "left_only": left_only,
        "right_only": right_only,
    }


def deleted_word_mapping(words: list[str], deleted_position: int | None) -> dict[int, str]:
    retained = [word for position, word in enumerate(words, 1)
                if position != deleted_position]
    return {position: word for position, word in enumerate(retained, 1)}


def piecewise_candidate_mapping(
    words: list[str], printed: dict[int, str], deleted_position: int
) -> dict[int, str]:
    """Insert one local deletion model without projecting it past label 466.

    The printed table has another discontinuity beginning at the duplicated 480
    marker.  A local 240--466 hypothesis therefore has no authority to shift the
    rest of the Declaration.  Outside that band, retain the independently parsed
    printed-anchor expansion.
    """

    mapping = dict(printed)
    local = deleted_word_mapping(words, deleted_position)
    for label in range(240, 467):
        mapping[label] = local[label]
    return mapping


def longest_walk(text: str) -> dict:
    best = {"length": 0, "start": None, "end": None, "text": "", "direction": None}
    for direction in (1, -1):
        start = 0
        previous = None
        for index, char in enumerate(text):
            if char == "?":
                previous = None
                start = index + 1
                continue
            value = ord(char) - 97
            if previous is None or value - previous not in (0, direction):
                start = index
            length = index - start + 1
            if length > best["length"]:
                best = {
                    "length": length,
                    "start": start + 1,
                    "end": index + 1,
                    "text": text[start:index + 1],
                    "direction": "forward" if direction == 1 else "reverse",
                }
            previous = value
    return best


def equality_pattern_null(
    cipher: list[int], mapping: dict[int, str], trials: int, seed: int, observed: int
) -> dict:
    symbols = list(dict.fromkeys(cipher))
    symbol_index = {number: index for index, number in enumerate(symbols)}
    pattern = [symbol_index[number] for number in cipher]
    assignments = [mapping[number][0].lower() if number in mapping else "?"
                   for number in symbols]
    rng = random.Random(seed)
    work = list(assignments)
    exceedances = 0
    histogram: Counter[int] = Counter()
    for _ in range(trials):
        rng.shuffle(work)
        text = "".join(work[index] for index in pattern)
        statistic = longest_walk(text)["length"]
        histogram[statistic] += 1
        exceedances += statistic >= observed
    return {
        "method": (
            "Permute decoded initials, including unresolved barriers, across B1's "
            "distinct number types; reconstruct the stream from the unchanged equality pattern."
        ),
        "distinct_number_types": len(symbols),
        "trials": trials,
        "seed": seed,
        "exceedances": exceedances,
        "p_add_one": (exceedances + 1) / (trials + 1),
        "histogram": {str(key): histogram[key] for key in sorted(histogram)},
    }


def best_walk_with_neighbor_corrections(
    cipher: list[int], mapping: dict[int, str], budget: int
) -> dict:
    """Maximize the walk while allowing at most ``budget`` ±1 number edits.

    This is a sensitivity analysis, not an authorized correction procedure.
    Dynamic-programming states retain direction, last letter, and edit cost;
    each state stores the longest contiguous run ending at the current position.
    """

    states: dict[tuple[int, int, int], tuple[int, int, str, tuple[int, ...]]] = {}
    best: tuple[int, int, int, str, tuple[int, ...]] = (0, 0, -1, "", ())
    for index, number in enumerate(cipher):
        options = []
        for delta in (-1, 0, 1):
            candidate = number + delta
            if candidate in mapping:
                options.append((ord(mapping[candidate][0].lower()) - 97, int(delta != 0), delta))
        next_states: dict[tuple[int, int, int], tuple[int, int, str, tuple[int, ...]]] = {}
        for direction in (1, -1):
            for value, cost, delta in options:
                if cost <= budget:
                    key = (direction, value, cost)
                    candidate_state = (1, index, chr(value + 97), (delta,))
                    if key not in next_states or candidate_state[0] > next_states[key][0]:
                        next_states[key] = candidate_state
                for (old_direction, previous, used), state in states.items():
                    if old_direction != direction or used + cost > budget:
                        continue
                    if value - previous not in (0, direction):
                        continue
                    length, start, text, changes = state
                    key = (direction, value, used + cost)
                    candidate_state = (
                        length + 1,
                        start,
                        text + chr(value + 97),
                        changes + (delta,),
                    )
                    if key not in next_states or candidate_state[0] > next_states[key][0]:
                        next_states[key] = candidate_state
        states = next_states
        for state in states.values():
            length, start, text, changes = state
            if length > best[0]:
                best = (length, start, index, text, changes)

    length, start, end, text, changes = best
    return {
        "budget": budget,
        "length": length,
        "positions_1_based": [start + 1, end + 1],
        "text": text,
        "edits": [
            {
                "b1_position": start + offset + 1,
                "printed_number": cipher[start + offset],
                "delta": delta,
                "replacement_number": cipher[start + offset] + delta,
            }
            for offset, delta in enumerate(changes) if delta
        ],
    }


def build_report(trials: int, seed: int) -> dict:
    b1_path = ROOT / "data" / "beale1_1885.csv"
    b2_path = ROOT / "data" / "beale2_1885.csv"
    plaintext_path = ROOT / "cipher_diagnostics" / "beale_cipher2_deciphered_fsu.txt"
    source_paths = [ROOT / "sources" / f"page_{page}.wikitext" for page in range(17, 21)]
    b1, b2 = read_numbers(b1_path), read_numbers(b2_path)
    words = declaration_words()
    printed = printed_anchor_mapping("last")
    printed_first = printed_anchor_mapping("first")
    b2_baseline = decode(b2, printed)
    plaintext = "".join(re.findall(r"[A-Za-z]", plaintext_path.read_text())).lower()
    alignment = global_alignment(b2_baseline, plaintext)

    observations: dict[int, Counter[str]] = defaultdict(Counter)
    for cipher_position, plaintext_position in alignment["pairs"]:
        observations[b2[cipher_position]][plaintext[plaintext_position]] += 1

    constraints = {
        str(number): {
            "observations": dict(sorted(counts.items())),
            "total": sum(counts.values()),
            "unanimous": len(counts) == 1,
            "majority": counts.most_common(1)[0][0],
        }
        for number, counts in sorted(observations.items())
    }
    conflicts = {number: row for number, row in constraints.items() if not row["unanimous"]}

    candidate_positions = list(range(240, 247))
    candidates = {}
    for deleted in candidate_positions:
        mapping = piecewise_candidate_mapping(words, printed, deleted)
        type_matches = type_mismatches = occurrence_matches = occurrence_mismatches = 0
        mismatches = []
        for number, counts in sorted(observations.items()):
            if number not in mapping or not 239 <= number <= 466:
                continue
            predicted = mapping[number][0].lower()
            majority = counts.most_common(1)[0][0]
            if predicted == majority:
                type_matches += 1
            else:
                type_mismatches += 1
                mismatches.append({
                    "number": number,
                    "predicted": predicted,
                    "observed": dict(sorted(counts.items())),
                })
            occurrence_matches += counts[predicted]
            occurrence_mismatches += sum(counts.values()) - counts[predicted]
        b1_text = decode(b1, mapping)
        candidates[str(deleted)] = {
            "deleted_ordinary_position": deleted,
            "deleted_word": words[deleted - 1],
            "local_239_466_constraint_type_matches": type_matches,
            "local_239_466_constraint_type_mismatches": type_mismatches,
            "local_239_466_constraint_occurrence_matches": occurrence_matches,
            "local_239_466_constraint_occurrence_mismatches": occurrence_mismatches,
            "mismatches": mismatches,
            "b1_decoded_count": len(b1_text) - b1_text.count("?"),
            "b1_unresolved_count": b1_text.count("?"),
            "b1_sha256": hashlib.sha256(b1_text.encode()).hexdigest(),
            "b1_longest_walk": longest_walk(b1_text),
            "b1_positions_188_207": b1_text[187:207],
        }

    admissible = [position for position in range(242, 247)]
    admissible_mappings = {
        position: piecewise_candidate_mapping(words, printed, position)
        for position in admissible
    }
    representative = admissible_mappings[admissible[-1]]
    representative_text = decode(b1, representative)
    representative_first = piecewise_candidate_mapping(words, printed_first, admissible[-1])
    representative_first_text = decode(b1, representative_first)
    observed_statistic = longest_walk(representative_text)["length"]
    admissible_texts = {
        position: decode(b1, mapping)
        for position, mapping in admissible_mappings.items()
    }
    differing_positions = [
        index + 1 for index in range(len(b1))
        if len({text[index] for text in admissible_texts.values()}) > 1
    ]
    representative_rows = [
        {
            "position": index,
            "cipher_number": number,
            "word": representative.get(number),
            "initial": representative_text[index - 1],
            "resolved": number in representative,
        }
        for index, number in enumerate(b1, 1)
    ]
    model_deltas = {}
    for position, mapping in admissible_mappings.items():
        text = admissible_texts[position]
        model_deltas[str(position)] = [
            {
                "position": index,
                "cipher_number": b1[index - 1],
                "word": mapping.get(b1[index - 1]),
                "initial": text[index - 1],
            }
            for index in range(1, len(b1) + 1)
            if text[index - 1] != representative_text[index - 1]
        ]

    raw_collision_labels = sorted(
        label for label in set(printed) | set(printed_first)
        if printed.get(label) != printed_first.get(label)
    )
    collision_b1_positions = [
        {
            "position": index,
            "cipher_number": number,
            "first_assignment_initial": representative_first_text[index - 1],
            "last_assignment_initial": representative_text[index - 1],
        }
        for index, number in enumerate(b1, 1)
        if representative_first_text[index - 1] != representative_text[index - 1]
    ]

    ordinary = deleted_word_mapping(words, None)
    fsu_words = re.findall(
        r"[A-Za-z]+(?:['’][A-Za-z]+)?",
        (ROOT / "cipher_diagnostics" / "declaration_fsu.txt").read_text(),
    )
    fsu_mapping = {position: word for position, word in enumerate(fsu_words, 1)}
    edition_sensitivity = {}
    for name, mapping in {
        "pamphlet_ordinary_sequential": ordinary,
        "pamphlet_printed_anchor_expansion": printed,
        "independent_modern_transcription_sequential": fsu_mapping,
    }.items():
        text = decode(b1, mapping)
        edition_sensitivity[name] = {
            "word_or_label_count": len(mapping),
            "decoded": len(text) - text.count("?"),
            "unresolved": text.count("?"),
            "longest_walk": longest_walk(text),
        }

    return {
        "schema": "beale-b2-table-constraint-audit-v1",
        "classification": "known_plaintext_table_reconstruction_not_b2_decryption",
        "inputs": {str(path.relative_to(ROOT)): sha256(path)
                   for path in [*source_paths, b1_path, b2_path, plaintext_path]},
        "alignment_specification": {
            "left": "B2 decoded under deterministic pamphlet printed-anchor expansion",
            "right": "published B2 plaintext, A-Z only and lowercase",
            "costs": {"substitution": 1, "gap": 2},
            "tie_break": "diagonal, then right-only, then left-only",
            "manual_phrase_deletions": 0,
            "score": alignment["score"],
            "paired_positions": len(alignment["pairs"]),
            "left_only_positions": [position + 1 for position in alignment["left_only"]],
            "right_only_positions": [position + 1 for position in alignment["right_only"]],
            "right_only_letters": "".join(plaintext[position]
                                           for position in alignment["right_only"]),
        },
        "inferred_constraints": {
            "observed_number_types": len(constraints),
            "unanimous_number_types": sum(row["unanimous"] for row in constraints.values()),
            "conflicting_number_types": conflicts,
            "number_241": constraints.get("241"),
            "number_246": constraints.get("246"),
            "all": constraints,
        },
        "single_deletion_candidates_240_246": candidates,
        "supported_local_interval": {
            "admissible_deleted_positions": admissible,
            "admissible_words": [words[position - 1] for position in admissible],
            "reason": (
                "Deleting 240 or 241 contradicts the two unanimous i observations for B2 "
                "number 241. Deleting any one of 242..246 retains 241=invariably and moves "
                "ordinary 247=design to table label 246; B2 does not use 242..245."
            ),
            "identifiable_word": False,
        },
        "complete_b1_application": {
            "admissible_models": [str(position) for position in admissible],
            "representative_model": "delete ordinary position 246",
            "representative_decoded_sha256": hashlib.sha256(
                representative_text.encode()).hexdigest(),
            "representative_decoded_count": len(representative_text) - representative_text.count("?"),
            "representative_unresolved_count": representative_text.count("?"),
            "representative_longest_walk": longest_walk(representative_text),
            "piecewise_rule": (
                "Use the candidate single-deletion enumeration only for labels "
                "240..466; use the parsed pamphlet-anchor table outside that band."
            ),
            "positions_that_differ_across_admissible_models": differing_positions,
            "invariant_positions_188_207": representative_text[187:207],
            "representative_rows": representative_rows,
            "model_deltas_from_representative": model_deltas,
        },
        "printed_anchor_collision_sensitivity": {
            "primary_policy": "last_assignment_wins",
            "alternative_policy": "first_assignment_wins",
            "classification": (
                "Frozen parser-policy sensitivity for overlapping printed-anchor intervals; "
                "the local 240..466 reconstruction is held fixed in both cases."
            ),
            "raw_labels_with_different_words": [
                {
                    "label": label,
                    "first_assignment_word": printed_first.get(label),
                    "last_assignment_word": printed.get(label),
                }
                for label in raw_collision_labels
            ],
            "complete_b1_positions_that_differ": collision_b1_positions,
            "first_assignment_longest_walk": longest_walk(representative_first_text),
            "last_assignment_longest_walk": longest_walk(representative_text),
        },
        "statistic": {
            "definition": (
                "Maximum contiguous run over the complete decoded B1 stream and both "
                "directions, where each adjacent alphabet-rank difference is zero or the "
                "chosen direction; unresolved symbols break runs."
            ),
            "status": "post_hoc_descriptive_calibration",
            "observed": observed_statistic,
        },
        "equality_pattern_null": equality_pattern_null(
            b1, representative, trials, seed, observed_statistic
        ),
        "edition_sensitivity": edition_sensitivity,
        "neighbor_number_error_sensitivity": {
            "classification": (
                "Optimization after observing B1; demonstrates researcher freedom and must "
                "not be presented as a corrected ciphertext or confirmatory test."
            ),
            "allowed_operation": (
                "At no more than k positions in one contiguous candidate run, replace the "
                "printed number n by n-1 or n+1; scan all starts and both directions."
            ),
            "ordinary_sequential_table": [
                best_walk_with_neighbor_corrections(b1, ordinary, budget)
                for budget in range(4)
            ],
            "piecewise_reconstructed_table": [
                best_walk_with_neighbor_corrections(b1, representative, budget)
                for budget in range(4)
            ],
        },
        "limitations": [
            "The known B2 plaintext is used to infer constraints; this is not an independent decryption.",
            "The global alignment is deterministic but four observed number types remain internally conflicted.",
            "The deletion interval is identifiable, but the deleted word is not.",
            "The alphabet statistic was formulated after the anomaly was known.",
            "The equality-pattern null is one explicit chance model, not a probability that the hoax hypothesis is true.",
            "Overlapping printed anchors require a parser collision policy; both frozen policies are reported.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=199_999)
    parser.add_argument("--seed", type=int, default=20260801)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    report = build_report(args.trials, args.seed)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "alignment": report["alignment_specification"],
        "constraints": {
            "observed": report["inferred_constraints"]["observed_number_types"],
            "unanimous": report["inferred_constraints"]["unanimous_number_types"],
            "conflicts": report["inferred_constraints"]["conflicting_number_types"],
            "241": report["inferred_constraints"]["number_241"],
            "246": report["inferred_constraints"]["number_246"],
        },
        "supported_interval": report["supported_local_interval"],
        "b1": {
            key: report["complete_b1_application"][key]
            for key in (
                "admissible_models",
                "representative_model",
                "representative_decoded_sha256",
                "representative_decoded_count",
                "representative_unresolved_count",
                "representative_longest_walk",
                "positions_that_differ_across_admissible_models",
                "invariant_positions_188_207",
            )
        },
        "null": report["equality_pattern_null"],
    }, indent=2))


if __name__ == "__main__":
    main()
