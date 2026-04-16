"""
BODSLancePipeline: orchestrate reading, transforming, and writing.

Usage::

    from bods_lance.pipeline import BODSLancePipeline

    pipeline = BODSLancePipeline(input_path="data.jsonl", output_dir="output/")
    pipeline.run()
"""

from __future__ import annotations

import logging
from pathlib import Path

from bods_lance.ingestion.reader import BODSReader
from bods_lance.output.writer import LanceWriter
from bods_lance.transform.entities import transform_entity
from bods_lance.transform.persons import transform_person
from bods_lance.transform.relationships import transform_relationship

logger = logging.getLogger(__name__)

TRANSFORMERS = {
    "entityStatement": transform_entity,
    "personStatement": transform_person,
    "ownershipOrControlStatement": transform_relationship,
}


class BODSLancePipeline:
    """End-to-end pipeline: BODS JSON/JSONL → Lance datasets."""

    def __init__(
        self,
        input_path: str | Path,
        output_dir: str | Path,
        mode: str = "create",
    ) -> None:
        """
        Parameters
        ----------
        input_path:
            Path to a BODS v0.4 ``.json`` or ``.jsonl`` file.
        output_dir:
            Directory where Lance sub-datasets will be written.
        mode:
            Lance write mode: ``"create"`` (default), ``"overwrite"``,
            or ``"append"``.
        """
        self._input_path = Path(input_path)
        self._output_dir = Path(output_dir)
        self._mode = mode

    def run(self) -> dict[str, int]:
        """Run the pipeline and return row counts per table."""
        reader = BODSReader()
        writer = LanceWriter(self._output_dir, mode=self._mode)

        counts: dict[str, int] = {
            "entityStatement": 0,
            "personStatement": 0,
            "ownershipOrControlStatement": 0,
            "unknown": 0,
        }

        for stmt in reader.read(self._input_path):
            stmt_type = stmt.get("statementType")
            transformer = TRANSFORMERS.get(stmt_type)
            if transformer is None:
                logger.warning("Unknown statementType %r — skipping", stmt_type)
                counts["unknown"] += 1
                continue

            row = transformer(stmt)
            writer.add_row(stmt_type, row)
            counts[stmt_type] += 1

        table_counts = writer.finalise()

        logger.info("Pipeline complete.")
        logger.info(
            "  Statements processed: entity=%d, person=%d, ooc=%d, unknown=%d",
            counts["entityStatement"],
            counts["personStatement"],
            counts["ownershipOrControlStatement"],
            counts["unknown"],
        )
        for table, n in table_counts.items():
            logger.info("  Lance table %s: %d rows", table, n)

        return table_counts
