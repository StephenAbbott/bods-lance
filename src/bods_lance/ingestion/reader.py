"""
BODS v0.4 statement reader.

Supports:
  - JSON  (single array of statements)
  - JSONL (one statement per line)

Usage::

    from bods_lance.ingestion.reader import BODSReader

    reader = BODSReader()
    for statement in reader.read("data.jsonl"):
        ...
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Iterator

logger = logging.getLogger(__name__)


class BODSReader:
    """Stream BODS v0.4 statements from a JSON or JSONL file."""

    def read(self, filepath: str | Path) -> Iterator[dict]:
        """Yield raw statement dicts from *filepath*.

        Detects format from the first non-whitespace character:
        ``[`` → JSON array, any other → JSONL.
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {filepath}")

        suffix = path.suffix.lower()
        if suffix == ".jsonl" or suffix == ".ndjson":
            yield from self._read_jsonl(path)
        elif suffix == ".json":
            yield from self._read_json(path)
        else:
            # Sniff from content
            with path.open("r", encoding="utf-8") as fh:
                first_char = fh.read(1).lstrip()
            if first_char == "[":
                yield from self._read_json(path)
            else:
                yield from self._read_jsonl(path)

    # ------------------------------------------------------------------

    def _read_json(self, path: Path) -> Iterator[dict]:
        """Read a JSON file containing an array of statements."""
        logger.info("Reading JSON array from %s", path)
        try:
            with path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {path}: {exc}") from exc

        if not isinstance(data, list):
            raise ValueError(
                f"{path} does not contain a JSON array at the top level. "
                "BODS data must be a flat array of statements."
            )

        count = 0
        for item in data:
            if isinstance(item, dict):
                yield item
                count += 1
            else:
                logger.warning("Skipping non-dict item in JSON array: %r", item)

        logger.info("Read %d statements from %s", count, path)

    def _read_jsonl(self, path: Path) -> Iterator[dict]:
        """Read a JSONL file, yielding one statement per line."""
        logger.info("Reading JSONL from %s", path)
        errors = 0
        count = 0
        with path.open("r", encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                    count += 1
                except json.JSONDecodeError as exc:
                    errors += 1
                    if errors <= 10:
                        logger.warning("Line %d: JSON parse error — %s", lineno, exc)
                    elif errors == 11:
                        logger.warning("Further parse errors suppressed…")

        if errors:
            logger.warning(
                "Finished %s: %d statements read, %d parse errors", path, count, errors
            )
        else:
            logger.info("Read %d statements from %s", count, path)
