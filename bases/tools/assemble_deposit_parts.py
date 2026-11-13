#!/usr/bin/env python3
"""Assemble GitHub-browser-sized pieces of a MEMSDOC1 documentary pack.

The original encrypted bytes are reconstructed unchanged, and the existing
AES-GCM/SQLite publisher validates them before anything may be released.
A lone part is *not* a completed upload and never becomes a candidate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

PACK_PATTERN = re.compile(
    r"^(MEMS-DOC-(FR|EN|PT|ES|IT|DE)-[A-Za-z0-9._-]+\.encrypted)(?:\.part([12]))?$"
)
MAX_BROWSER_PART = 24 * 1024 * 1024
MAX_ENCRYPTED_PACK = 256 * 1024 * 1024
COPY_BLOCK = 1024 * 1024


def collect_deposits(depot: Path, changed: list[str], target: Path) -> dict[str, dict]:
    """Return only complete new/updated packs, keyed by language."""
    selections: dict[str, str] = {}
    for name in changed:
        relative = Path(name)
        if relative.parts[:2] != ("bases", "depot") or len(relative.parts) != 3:
            continue
        match = PACK_PATTERN.fullmatch(relative.name)
        if match is None:
            continue
        basename, language = match.group(1), match.group(2).lower()
        if language in selections and selections[language] != basename:
            raise ValueError("MORE_THAN_ONE_NEW_PACK_FOR_LANGUAGE_" + language.upper())
        selections[language] = basename

    result: dict[str, dict] = {}
    for language, basename in sorted(selections.items()):
        whole = depot / basename
        first = depot / (basename + ".part1")
        second = depot / (basename + ".part2")
        parts_found = [p.exists() for p in (first, second)]
        if whole.exists() and any(parts_found):
            raise ValueError("AMBIGUOUS_WHOLE_AND_SPLIT_PACK_" + basename)

        sources: list[Path]
        if any(parts_found):
            if not all(parts_found):
                print("WAITING_FOR_SECOND_PART", basename)
                continue
            sources = [first, second]
            for part in sources:
                if part.is_symlink() or not part.is_file() or not 0 < part.stat().st_size <= MAX_BROWSER_PART:
                    raise ValueError("SPLIT_PART_TOO_LARGE_OR_INVALID_" + part.name)
        elif whole.is_file() and not whole.is_symlink():
            sources = [whole]
        else:
            raise ValueError("ENCRYPTED_PACK_NOT_FOUND_" + basename)

        target.mkdir(parents=True, exist_ok=True)
        destination = target / basename
        digest = hashlib.sha256()
        size = 0
        try:
            with destination.open("wb") as output:
                for path in sources:
                    with path.open("rb") as stream:
                        while True:
                            block = stream.read(COPY_BLOCK)
                            if not block:
                                break
                            size += len(block)
                            if size > MAX_ENCRYPTED_PACK:
                                raise ValueError("ENCRYPTED_PACK_TOO_LARGE")
                            output.write(block)
                            digest.update(block)
            with destination.open("rb") as stream:
                if size < 62 or stream.read(8) != b"MEMSDOC1":
                    raise ValueError("PACK_FORMAT_INVALID_OR_INCOMPLETE")
        except Exception:
            destination.unlink(missing_ok=True)
            raise

        result[language] = {
            "name": basename, "size": size, "sha256": digest.hexdigest(),
            "source_parts": len(sources),
        }
        print("ASSEMBLED_VERIFIABLE_PACK", language, basename, size, digest.hexdigest())
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--depot", required=True, type=Path)
    parser.add_argument("--changed-list", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--result", required=True, type=Path)
    args = parser.parse_args()
    changes = args.changed_list.read_text(encoding="utf-8").splitlines()
    result = collect_deposits(args.depot, changes, args.output)
    args.result.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
