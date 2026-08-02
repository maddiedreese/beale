#!/usr/bin/env python3
"""Independent, read-only verification of the frozen B3 replication."""
from __future__ import annotations

import hashlib
import json
import random
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXPECTED_RESULT_FILE_SHA256 = (
    "a0e385f875274e34dc81622ac4ea4b5833889cadf22cb72ca249f606b22a7509"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_printed_doi() -> tuple[dict[int, str], dict]:
    """Recover the pamphlet's printed word labels directly from its pages."""
    pages = [ROOT / "sources" / "wikisource" / f"page_{number}.wikitext"
             for number in range(17, 21)]
    material = " ".join(page.read_text(encoding="utf-8") for page in pages)
    material = re.sub(r"<noinclude>.*?</noinclude>", " ", material, flags=re.DOTALL)
    begin = material.index("{{dual|1|When,")
    end = material.index("The letter, or paper", begin)
    declaration = material[begin:end]

    # Convert each printed {{dual|label|word...}} anchor to ordinary word text
    # followed by a sentinel. Remove all other simple Wikisource templates.
    def expose_anchor(match: re.Match[str]) -> str:
        label, printed_word = match.group(1), match.group(2)
        return f" {printed_word} ANCHOR{label}END "

    declaration = re.sub(
        r"\{\{dual\|(\d+)\|([^}|]+)(?:\|[^}]*)?\}\}", expose_anchor, declaration
    )
    declaration = re.sub(r"\{\{[^{}]*\}\}", " ", declaration)
    declaration = re.sub(r"\((\d+)\)", r" ANCHOR\1END ", declaration)
    units = re.findall(r"ANCHOR(\d+)END|([A-Za-z]+(?:['’][A-Za-z]+)?)", declaration)

    all_words: list[str] = []
    assigned_through = 0
    printed: dict[int, str] = {}
    anchor_history: list[tuple[int, int, int]] = []
    for anchor_text, word in units:
        if word:
            all_words.append(word)
            continue
        anchor = int(anchor_text)
        unassigned = all_words[assigned_through:]
        first_label = anchor - len(unassigned) + 1
        for label, token in zip(range(first_label, anchor + 1), unassigned):
            printed[label] = token
        anchor_history.append((anchor, len(unassigned), first_label))
        assigned_through = len(all_words)

    # The last visible anchor is 800. The pamphlet's next word is printed 817
    # because sixteen words intervene; carry that printed sequence to the end.
    for label, token in enumerate(all_words[assigned_through:], start=817):
        printed[label] = token

    metadata = {
        "source_paths": [str(page.relative_to(ROOT)) for page in pages],
        "source_sha256": {str(page.relative_to(ROOT)): digest(page) for page in pages},
        "true_word_count": len(all_words),
        "printed_numbering_max": max(printed),
        "distinct_printed_numbers": len(printed),
        "non_ten_word_anchor_groups": [
            {"anchor": anchor, "words_since_prior_anchor": size, "first_assigned": first}
            for anchor, size, first in anchor_history
            if 10 < anchor <= 800 and size != 10
        ],
        "non_increasing_anchors": [
            {"previous_anchor": left[0], "anchor": right[0]}
            for left, right in zip(anchor_history, anchor_history[1:])
            if right[0] <= left[0]
        ],
    }
    return printed, metadata


def transition_statistics(ranks: list[int]) -> tuple[int, int, int]:
    indicators = [int(b - a == 0 or b - a == 1) for a, b in zip(ranks, ranks[1:])]
    sums = [sum(indicators[start:start + 16])
            for start in range(len(ranks) - 16)]
    maximum = max(sums)
    return maximum, sums.index(maximum), sum(indicators)


def main() -> None:
    registration_path = HERE / "registration.json"
    result_path = HERE / "results.json"
    manifest_path = HERE / "extraction_manifest.json"
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert registration["status"] == "frozen"
    assert registration["exposure_authorized"] is True
    # The frozen registration records the original private-workspace path and
    # implementation hash.  This public verifier instead rebuilds the mapping
    # independently below, while preserving the registration byte-for-byte.

    source_path = ROOT / "sources" / "wikisource" / "page_22.wikitext"
    assert digest(source_path) == manifest["source_sha256"]
    source = source_path.read_text(encoding="utf-8")
    blocks = re.findall(
        r"\{\{smaller block/s\}\}(.*?)\{\{smaller block/e\}\}", source,
        flags=re.DOTALL,
    )
    assert len(blocks) == 1
    extracted = [int(token) for token in re.findall(r"\d+", blocks[0])]
    cipher_path = ROOT / "data" / "beale3_1885.csv"
    stored = [int(token) for token in re.findall(r"\d+", cipher_path.read_text())]
    assert extracted == stored
    assert (len(stored), len(set(stored)), min(stored), max(stored), stored.count(501)) == (
        618, 263, 1, 975, 0
    )
    assert digest(cipher_path) == manifest["output_sha256"]
    assert digest(cipher_path) == registration["cipher"]["sha256"]
    assert digest(cipher_path) == result["cipher_sha256"]
    assert digest(registration_path) == result["registration_sha256"]
    assert digest(result_path) == EXPECTED_RESULT_FILE_SHA256

    declaration, metadata = build_printed_doi()
    # Normalize the curated public source subdirectory to the path labels
    # preserved in the frozen 2026-08-01 result.
    metadata["source_paths"] = [path.replace("sources/wikisource/", "sources/")
                                for path in metadata["source_paths"]]
    metadata["source_sha256"] = {
        path.replace("sources/wikisource/", "sources/"): value
        for path, value in metadata["source_sha256"].items()
    }
    assert metadata == result["mapping_metadata"]
    eligible = sorted(label for label in declaration if 1 <= label <= 975)
    assert eligible == [label for label in range(1, 976) if label != 501]
    assert all(stored_label in declaration for stored_label in stored)
    letter_rank = {label: ord(declaration[label][0].lower()) - ord("a")
                   for label in eligible}

    observed_ranks = [letter_rank[label] for label in stored]
    observed_max, observed_start, observed_total = transition_statistics(observed_ranks)
    observed_window = "".join(
        chr(rank + ord("a")) for rank in observed_ranks[observed_start:observed_start + 17]
    )
    observed = {
        "maximum_positive_transitions_in_17_symbols": observed_max,
        "best_window_start_1_based": observed_start + 1,
        "best_window_end_1_based": observed_start + 17,
        "best_window_initials": observed_window,
        "full_stream_positive_transitions": observed_total,
    }
    assert observed == result["observed"]

    labels = sorted(set(stored))
    generator = random.Random(registration["null"]["seed"])
    maxima: list[int] = []
    totals: list[int] = []
    for _ in range(registration["null"]["trials"]):
        destinations = generator.sample(eligible, len(labels))
        assignment = dict(zip(labels, destinations))
        randomized_ranks = [letter_rank[assignment[label]] for label in stored]
        maximum, _, total = transition_statistics(randomized_ranks)
        maxima.append(maximum)
        totals.append(total)

    maxima_hash = hashlib.sha256(
        json.dumps(maxima, separators=(",", ":")).encode()
    ).hexdigest()
    totals_hash = hashlib.sha256(
        json.dumps(totals, separators=(",", ":")).encode()
    ).hexdigest()
    primary_exceedances = sum(value >= observed_max for value in maxima)
    secondary_exceedances = sum(value >= observed_total for value in totals)
    primary_p = (primary_exceedances + 1) / (len(maxima) + 1)
    secondary_p = (secondary_exceedances + 1) / (len(totals) + 1)
    assert maxima_hash == result["null_maxima_sha256"]
    assert totals_hash == result["null_totals_sha256"]
    assert primary_exceedances == result["primary"]["exceedances"] == 8727
    assert primary_p == result["primary"]["monte_carlo_p"] == 0.08728
    assert result["primary"]["statistical_hit"] is False
    assert secondary_exceedances == result["secondary_descriptive"]["exceedances"] == 53405
    assert secondary_p == result["secondary_descriptive"]["monte_carlo_p"] == 0.53406

    print(json.dumps({
        "verification": "PASS",
        "result_file_sha256": digest(result_path),
        "cipher": {
            "source_sha256": digest(source_path),
            "csv_sha256": digest(cipher_path),
            "count": len(stored),
            "distinct": len(labels),
            "range": [min(stored), max(stored)],
        },
        "eligible_printed_doi_indices": len(eligible),
        "undefined_within_1_to_975": [501],
        "observed": observed,
        "null": {
            "seed": registration["null"]["seed"],
            "trials": len(maxima),
            "primary_exceedances": primary_exceedances,
            "primary_p": primary_p,
            "secondary_exceedances": secondary_exceedances,
            "secondary_p": secondary_p,
            "maxima_sha256": maxima_hash,
            "totals_sha256": totals_hash,
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
