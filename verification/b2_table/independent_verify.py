#!/usr/bin/env python3
"""Clean-room replication of the B1 walk and equality-pattern null.

This script imports no code from ``audit.py``. It independently extracts the
pamphlet table, applies one representative admissible local model, rebuilds the
Monte Carlo distribution, and compares it with the saved result.
"""

from __future__ import annotations

import json
import random
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPECTED = Path(__file__).with_name("results.json")


def extract_printed_table() -> tuple[list[str], dict[int, str]]:
    raw = " ".join(
        (ROOT / "sources" / f"page_{page}.wikitext").read_text()
        for page in range(17, 21)
    )
    raw = raw[raw.index("{{dual|1|When,") : raw.index("The letter, or paper")]
    raw = re.sub(r"<noinclude>.*?</noinclude>", " ", raw, flags=re.S)
    raw = re.sub(
        r"\{\{dual\|(\d+)\|([^}|]+)(?:\|[^}]*)?\}\}",
        lambda match: f" {match.group(2)} ({match.group(1)}) ",
        raw,
    )
    raw = re.sub(r"\{\{[^{}]*\}\}", " ", raw)
    stream = re.findall(r"\((\d+)\)|([A-Za-z]+(?:['’][A-Za-z]+)?)", raw)
    words: list[str] = []
    pending: list[str] = []
    table: dict[int, str] = {}
    for anchor_text, word in stream:
        if word:
            words.append(word)
            pending.append(word)
            continue
        anchor = int(anchor_text)
        first = anchor - len(pending) + 1
        for offset, item in enumerate(pending):
            table[first + offset] = item
        pending = []
    if pending:
        first = max(table) + 1
        for offset, item in enumerate(pending):
            table[first + offset] = item
    return words, table


def representative_table(words: list[str], printed: dict[int, str]) -> dict[int, str]:
    # Ordinary word 246 ("a") is one of five equally admissible local deletions.
    retained = [word for position, word in enumerate(words, 1) if position != 246]
    local = {position: word for position, word in enumerate(retained, 1)}
    table = dict(printed)
    for label in range(240, 467):
        table[label] = local[label]
    return table


def walk_length(text: str) -> int:
    best = 0
    for direction in (1, -1):
        previous = None
        length = 0
        for char in text:
            if char == "?":
                previous = None
                length = 0
                continue
            value = ord(char) - 97
            if previous is not None and value - previous in (0, direction):
                length += 1
            else:
                length = 1
            best = max(best, length)
            previous = value
    return best


def main() -> None:
    expected = json.loads(EXPECTED.read_text())
    words, printed = extract_printed_table()
    table = representative_table(words, printed)
    cipher = [int(value) for value in re.findall(
        r"\d+", (ROOT / "data" / "beale1_1885.csv").read_text()
    )]
    decoded = "".join(table[number][0].lower() if number in table else "?"
                      for number in cipher)
    assert decoded[187:204] == "abcdefghiijklmmno"
    assert walk_length(decoded) == 17

    symbols = list(dict.fromkeys(cipher))
    lookup = {number: index for index, number in enumerate(symbols)}
    pattern = [lookup[number] for number in cipher]
    assignments = [table[number][0].lower() if number in table else "?"
                   for number in symbols]
    specification = expected["equality_pattern_null"]
    rng = random.Random(specification["seed"])
    work = list(assignments)
    histogram: Counter[int] = Counter()
    exceedances = 0
    for _ in range(specification["trials"]):
        rng.shuffle(work)
        statistic = walk_length("".join(work[index] for index in pattern))
        histogram[statistic] += 1
        exceedances += statistic >= 17

    observed_histogram = {str(key): histogram[key] for key in sorted(histogram)}
    assert exceedances == specification["exceedances"]
    assert observed_histogram == specification["histogram"]
    assert (exceedances + 1) / (specification["trials"] + 1) == specification["p_add_one"]
    print(json.dumps({
        "verified": True,
        "b1_positions_188_204": decoded[187:204],
        "observed": 17,
        "trials": specification["trials"],
        "exceedances": exceedances,
        "p_add_one": specification["p_add_one"],
        "histogram": observed_histogram,
    }, indent=2))


if __name__ == "__main__":
    main()
