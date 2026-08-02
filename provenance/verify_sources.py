#!/usr/bin/env python3
"""Verify frozen B1/B2 transcriptions against scan-derived Wikisource pages.

The repository preserves the 1885 scan as the primary visual witness and the
corresponding Wikisource page markup as a machine-readable transcription.  This
script deliberately extracts only the numbered blocks identified by their
surrounding pamphlet headings; it does not search the page for a convenient
matching subsequence.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def numbers(text: str) -> list[int]:
    return [int(value) for value in re.findall(r"\d+", text)]


def frozen(name: str) -> list[int]:
    return numbers((ROOT / "data" / name).read_text())


def delimited_block(text: str, start_marker: str) -> str:
    start = text.index(start_marker) + len(start_marker)
    block_start = text.index("{{smaller block/s}}", start) + len("{{smaller block/s}}")
    block_end = text.index("{{smaller block/e}}", block_start)
    return text[block_start:block_end]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    page20 = (ROOT / "sources" / "wikisource" / "page_20.wikitext").read_text()
    page21 = (ROOT / "sources" / "wikisource" / "page_21.wikitext").read_text()

    extracted_b2 = numbers(delimited_block(page20, "marked “2,”"))
    extracted_b1 = numbers(delimited_block(page21, "THE LOCALITY OF THE VAULT"))
    frozen_b1 = frozen("beale1_1885.csv")
    frozen_b2 = frozen("beale2_1885.csv")

    assert len(extracted_b1) == 520, len(extracted_b1)
    assert len(extracted_b2) == 762, len(extracted_b2)
    assert extracted_b1 == frozen_b1
    assert extracted_b2 == frozen_b2

    scan = ROOT / "sources" / "beale_papers_1885.djvu"
    print(f"B1: exact match ({len(extracted_b1)} integers)")
    print(f"B2: exact match ({len(extracted_b2)} integers)")
    print(f"1885 scan sha256: {digest(scan)}")
    print("PASS")


if __name__ == "__main__":
    main()
