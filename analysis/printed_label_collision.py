#!/usr/bin/env python3
"""Reconstruct the pamphlet's duplicate-label collision near printed 240.

This reproduces the attractive but ultimately incorrect ``pursuing omission``
hypothesis.  It records the collision instead of silently treating a dictionary
overwrite as historical evidence.  The independent B2 constraint audit rejects
deleting pursuing; see ``verification/b2_table``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATHS = [ROOT / "sources" / "wikisource" / f"page_{page}.wikitext"
                for page in range(17, 21)]
B1_PATH = ROOT / "data" / "beale1_1885.csv"

EXPECTED_HASHES = {
    "data/beale1_1885.csv": "0e63242041b03717a96340fde86af10f895355b936b4120da1769e9f2f7e3d27",
    "sources/wikisource/page_17.wikitext": "b3b41de785cae4fb1f25f849c6a61f2fb17da0cb8cec7784a094ac150a23588f",
    "sources/wikisource/page_18.wikitext": "439683edf0a52ce398eaca05e15f3cbac3e03f6dfb3ec291ba72746a33372cf0",
    "sources/wikisource/page_19.wikitext": "1f88c40b384200ed63714171216fe681da7bc570f7e5bf5a936bb6078d3c5004",
    "sources/wikisource/page_20.wikitext": "50133deddbf80fd81a9664742c8526f5381f803416db80e207719434d4c2bee8",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_inputs() -> dict[str, str]:
    observed = {}
    for relative, expected in EXPECTED_HASHES.items():
        actual = sha256(ROOT / relative)
        if actual != expected:
            raise RuntimeError(f"hash mismatch for {relative}: {actual} != {expected}")
        observed[relative] = actual
    return observed


def source_tokens() -> list[tuple[str, str | int]]:
    raw = " ".join(path.read_text() for path in SOURCE_PATHS)
    raw = re.sub(r"<noinclude>.*?</noinclude>", " ", raw, flags=re.S)
    raw = raw[raw.index("{{dual|1|When,") : raw.index("The letter, or paper")]
    raw = re.sub(
        r"\{\{dual\|(\d+)\|([^}|]+)(?:\|[^}]*)?\}\}",
        lambda match: f" {match.group(2)} ({match.group(1)}) ",
        raw,
    )
    raw = re.sub(r"\{\{[^{}]*\}\}", " ", raw)
    tokens = []
    for number, word in re.findall(r"\((\d+)\)|([A-Za-z]+(?:['’][A-Za-z]+)?)", raw):
        tokens.append(("anchor", int(number)) if number else ("word", word))
    return tokens


def reconstruct() -> dict:
    words: list[str] = []
    pending: list[str] = []
    mapping: dict[int, str] = {}
    assignments: dict[int, list[dict]] = {}
    groups = []

    for kind, value in source_tokens():
        if kind == "word":
            word = str(value)
            words.append(word)
            pending.append(word)
            continue

        anchor = int(value)
        first = anchor - len(pending) + 1
        group = {
            "anchor": anchor,
            "word_count": len(pending),
            "first_assigned": first,
            "words": list(pending),
        }
        groups.append(group)
        for label, word in enumerate(pending, first):
            event = {"word": word, "anchor": anchor, "first_assigned": first}
            assignments.setdefault(label, []).append(event)
            mapping[label] = word  # explicit latest-anchor working-table policy
        pending.clear()

    # The final unanchored tail follows the convention used by prior B2-table
    # reconstructions.  It is irrelevant to the B1 alphabet passage.
    if pending:
        for label, word in enumerate(pending, max(mapping) + 1):
            assignments.setdefault(label, []).append({
                "word": word, "anchor": None, "first_assigned": max(mapping) + 1,
            })
            mapping[label] = word

    ordinary = {index: word for index, word in enumerate(words, 1)}
    collisions = {
        str(label): events for label, events in assignments.items() if len(events) > 1
    }
    return {
        "words": words,
        "ordinary": ordinary,
        "working": mapping,
        "groups": groups,
        "collisions": collisions,
    }


def decode(numbers: list[int], mapping: dict[int, str]) -> str:
    return "".join(mapping[number][0].lower() if number in mapping else "?"
                   for number in numbers)


def longest_forward_walk(text: str) -> dict:
    best_start = 0
    best_length = 0
    run_start = 0
    for index, char in enumerate(text):
        if index and char != "?" and text[index - 1] != "?" and (
                ord(char) - ord(text[index - 1]) in (0, 1)):
            pass
        else:
            run_start = index
        length = index - run_start + 1
        if length > best_length:
            best_start, best_length = run_start, length
    return {
        "length": best_length,
        "positions_1_based": [best_start + 1, best_start + best_length],
        "text": text[best_start:best_start + best_length],
    }


def build_report() -> dict:
    hashes = verify_inputs()
    model = reconstruct()
    cipher = [int(value) for value in re.findall(r"\d+", B1_PATH.read_text())]
    working_text = decode(cipher, model["working"])
    ordinary_text = decode(cipher, model["ordinary"])
    start, end = 187, 207  # B1 positions 188--207, Python half-open indices
    comparison = []
    for index in range(start, end):
        number = cipher[index]
        comparison.append({
            "b1_position": index + 1,
            "number": number,
            "ordinary_word": model["ordinary"].get(number),
            "ordinary_letter": ordinary_text[index],
            "working_word": model["working"].get(number),
            "working_letter": working_text[index],
            "changed": ordinary_text[index] != working_text[index],
        })

    pursuing_groups = [group for group in model["groups"]
                       if "pursuing" in [word.lower() for word in group["words"]]
                       or group["anchor"] == 250]
    report = {
        "schema": "beale-printed-label-collision-v1",
        "input_sha256": hashes,
        "cipher_count": len(cipher),
        "declaration_word_count": len(model["words"]),
        "enumeration_policy": (
            "For each printed anchor n, assign the words since the prior anchor "
            "backward so the last word receives n; retain the later assignment "
            "when ranges overlap, while reporting every overlap."
        ),
        "pursuing_interval": pursuing_groups,
        "label_240_assignments": model["collisions"].get("240", []),
        "all_assignment_collisions": model["collisions"],
        "b1_positions_188_207": comparison,
        "ordinary_letters_188_207": ordinary_text[start:end],
        "working_letters_188_207": working_text[start:end],
        "changed_positions": [row for row in comparison if row["changed"]],
        "working_forward_walk": longest_forward_walk(working_text),
        "hypothesis_status": "refuted as a historical omission model",
        "interpretation_limit": (
            "This reconstructs a collision created by one deterministic expansion "
            "of sparse printed labels. It does not show that a historical working "
            "table omitted pursuing. B2 number 241 requires invariably -> i twice, "
            "which contradicts deleting pursuing."
        ),
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build_report()
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
