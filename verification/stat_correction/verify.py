#!/usr/bin/env python3
"""Independent replication of the B1 walk calibration and edit sensitivity.

This implementation imports no project analysis code.  It derives the table
from the frozen pamphlet transcription, reconstructs the representative local
model, and uses a start-by-start exhaustive state search for the edit analysis.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TRIALS = 199_999
SEED = 20_260_801


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs() -> tuple[list[int], list[str], dict[int, str], list[Path]]:
    pages = [ROOT / "sources" / f"page_{number}.wikitext" for number in range(17, 21)]
    raw = " ".join(path.read_text() for path in pages)
    raw = raw[raw.index("{{dual|1|When,") : raw.index("The letter, or paper")]
    raw = re.sub(r"<noinclude>.*?</noinclude>", " ", raw, flags=re.S)
    raw = re.sub(
        r"\{\{dual\|(\d+)\|([^}|]+)(?:\|[^}]*)?\}\}",
        lambda match: f" {match.group(2)} ZZZANCHOR{match.group(1)}ZZZ ",
        raw,
    )
    raw = re.sub(r"\{\{[^{}]*\}\}", " ", raw)
    # Most decade labels are literal parenthetical numbers in the transcription;
    # early labels are embedded in the dual templates handled above.
    raw = re.sub(r"\((\d+)\)", lambda match: f" ZZZANCHOR{match.group(1)}ZZZ ", raw)
    tokens = re.findall(
        r"ZZZANCHOR(\d+)ZZZ|([A-Za-z]+(?:['’][A-Za-z]+)?)", raw
    )

    words: list[str] = []
    pending: list[str] = []
    printed: dict[int, str] = {}
    for label_text, word in tokens:
        if word:
            words.append(word)
            pending.append(word)
        else:
            label = int(label_text)
            for number, pending_word in enumerate(pending, label - len(pending) + 1):
                printed[number] = pending_word
            pending.clear()
    if pending:
        for number, pending_word in enumerate(pending, max(printed) + 1):
            printed[number] = pending_word

    b1_path = ROOT / "data" / "beale1_1885.csv"
    cipher = [int(item) for item in re.findall(r"\d+", b1_path.read_text())]
    return cipher, words, printed, [b1_path, *pages]


def representative_table(words: list[str], printed: dict[int, str]) -> dict[int, str]:
    # Ordinary position 246 is only a representative of the five admissible
    # deletions (242..246); all five yield the same reported central run.
    retained = [word for position, word in enumerate(words, 1) if position != 246]
    local = dict(enumerate(retained, 1))
    result = dict(printed)
    result.update({label: local[label] for label in range(240, 467)})
    return result


def decode(cipher: list[int], table: dict[int, str]) -> str:
    return "".join(table[number][0].lower() if number in table else "?" for number in cipher)


def walk_maximum(text: str) -> dict[str, int | str]:
    best: dict[str, int | str] = {"length": 0, "start": 0, "end": 0, "text": ""}
    for direction in (1, -1):
        start = 0
        previous: int | None = None
        for index, character in enumerate(text):
            if character == "?":
                previous = None
                start = index + 1
                continue
            value = ord(character) - ord("a")
            if previous is None or value - previous not in (0, direction):
                start = index
            length = index - start + 1
            if length > int(best["length"]):
                best = {
                    "length": length,
                    "start": start + 1,
                    "end": index + 1,
                    "text": text[start:index + 1],
                    "direction": "forward" if direction == 1 else "reverse",
                }
            previous = value
    return best


def monte_carlo(cipher: list[int], table: dict[int, str], observed: int) -> dict:
    types = list(dict.fromkeys(cipher))
    index = {number: offset for offset, number in enumerate(types)}
    equality_pattern = [index[number] for number in cipher]
    assignments = [table[number][0].lower() if number in table else "?" for number in types]
    rng = random.Random(SEED)
    work = assignments[:]
    histogram: Counter[int] = Counter()
    exceedances = 0
    for _ in range(TRIALS):
        rng.shuffle(work)
        sample = "".join(work[offset] for offset in equality_pattern)
        statistic = int(walk_maximum(sample)["length"])
        histogram[statistic] += 1
        exceedances += statistic >= observed
    return {
        "trials": TRIALS,
        "seed": SEED,
        "distinct_number_types": len(types),
        "exceedances": exceedances,
        "p_add_one": (exceedances + 1) / (TRIALS + 1),
        "maximum_simulated_run": max(histogram),
        "histogram": {str(length): count for length, count in sorted(histogram.items())},
    }


def exhaustive_edit_scan(cipher: list[int], table: dict[int, str], budget: int) -> dict:
    """Scan every start/direction; retain all reachable (last-letter,cost) states."""
    best = {"budget": budget, "length": 0, "start": 0, "end": 0, "text": "", "edits": []}
    for start in range(len(cipher)):
        for direction in (1, -1):
            # Values are witnesses: (text, tuple of deltas).
            states: dict[tuple[int, int], tuple[str, tuple[int, ...]]] = {}
            for end in range(start, len(cipher)):
                options: list[tuple[int, int, int]] = []
                for delta in (-1, 0, 1):
                    replacement = cipher[end] + delta
                    if replacement in table:
                        options.append((ord(table[replacement][0].lower()) - ord("a"), abs(delta), delta))
                next_states: dict[tuple[int, int], tuple[str, tuple[int, ...]]] = {}
                for letter, cost, delta in options:
                    if end == start:
                        if cost <= budget:
                            next_states.setdefault((letter, cost), (chr(letter + 97), (delta,)))
                        continue
                    for (previous, spent), (text, deltas) in states.items():
                        if spent + cost <= budget and letter - previous in (0, direction):
                            next_states.setdefault(
                                (letter, spent + cost),
                                (text + chr(letter + 97), deltas + (delta,)),
                            )
                states = next_states
                if not states:
                    break
                length = end - start + 1
                if length > best["length"]:
                    _, (text, deltas) = next(iter(states.items()))
                    best = {
                        "budget": budget,
                        "length": length,
                        "start": start + 1,
                        "end": end + 1,
                        "text": text,
                        "edits": [
                            {
                                "b1_position": start + offset + 1,
                                "printed_number": cipher[start + offset],
                                "delta": delta,
                                "replacement_number": cipher[start + offset] + delta,
                            }
                            for offset, delta in enumerate(deltas) if delta
                        ],
                    }
    return best


def main() -> None:
    cipher, words, printed, source_paths = inputs()
    table = representative_table(words, printed)
    decoded = decode(cipher, table)
    observed = walk_maximum(decoded)
    calibration = monte_carlo(cipher, table, int(observed["length"]))
    sensitivity = [exhaustive_edit_scan(cipher, table, budget) for budget in range(3)]
    result = {
        "schema": "beale-stat-correction-independent-audit-v1",
        "implementation": "standalone; imports no project analysis module",
        "input_sha256": {str(path.relative_to(ROOT)): digest(path) for path in source_paths},
        "decoded_sha256": hashlib.sha256(decoded.encode()).hexdigest(),
        "observed": observed,
        "positions_188_204": decoded[187:204],
        "monte_carlo": calibration,
        "correction_sensitivity": sensitivity,
        "claims_verified": {
            "observed_length_17_at_188_204": observed["length"] == 17 and observed["start"] == 188 and observed["end"] == 204,
            "observed_text": observed["text"] == "abcdefghiijklmmno",
            "zero_of_199999": calibration["exceedances"] == 0 and calibration["trials"] == 199_999,
            "add_one_p_000005": calibration["p_add_one"] == 0.000005,
            "maximum_simulated_10": calibration["maximum_simulated_run"] == 10,
            "edit_lengths_17_20_21": [row["length"] for row in sensitivity] == [17, 20, 21],
        },
    }
    expected = json.loads((ROOT / "verification" / "b2_table" / "results.json").read_text())
    expected_null = expected["equality_pattern_null"]
    result["exact_comparison_to_primary"] = {
        "histogram": calibration["histogram"] == expected_null["histogram"],
        "exceedances": calibration["exceedances"] == expected_null["exceedances"],
        "p_add_one": calibration["p_add_one"] == expected_null["p_add_one"],
        "correction_rows": [row["length"] for row in sensitivity]
        == [row["length"] for row in expected["neighbor_number_error_sensitivity"]["piecewise_reconstructed_table"][:3]],
    }
    if not all(result["claims_verified"].values()) or not all(result["exact_comparison_to_primary"].values()):
        raise SystemExit("verification failed")
    output = HERE / "independent_results.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"verified": True, **result["claims_verified"]}, indent=2))


if __name__ == "__main__":
    main()
