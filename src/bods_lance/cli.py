"""CLI entry point for bods-lance."""

from __future__ import annotations

import logging
import sys

import click

from bods_lance.pipeline import BODSLancePipeline


def _configure_logging(verbose: bool, quiet: bool) -> None:
    if quiet:
        level = logging.WARNING
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(
        stream=sys.stderr,
        level=level,
        format="%(levelname)s %(message)s",
    )


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable debug logging.")
@click.option("--quiet", "-q", is_flag=True, help="Suppress info logging.")
@click.pass_context
def main(ctx: click.Context, verbose: bool, quiet: bool) -> None:
    """Convert BODS v0.4 data to the Lance columnar format."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    _configure_logging(verbose, quiet)


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--output-dir",
    "-o",
    default="output",
    show_default=True,
    help="Directory to write Lance datasets into.",
)
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["create", "overwrite", "append"]),
    default="create",
    show_default=True,
    help="Lance write mode.",
)
@click.pass_context
def convert(ctx: click.Context, input_file: str, output_dir: str, mode: str) -> None:
    """Convert INPUT_FILE (BODS v0.4 JSON or JSONL) to Lance datasets.

    Three Lance sub-datasets are written inside OUTPUT_DIR:

    \b
      entity_statements/
      person_statements/
      ownership_or_control_statements/

    Example:

    \b
      bods-lance convert gleif.jsonl --output-dir ./gleif-lance
    """
    pipeline = BODSLancePipeline(
        input_path=input_file,
        output_dir=output_dir,
        mode=mode,
    )
    counts = pipeline.run()
    if not ctx.obj.get("quiet"):
        click.echo("Lance datasets written to: " + output_dir)
        for table, n in counts.items():
            click.echo(f"  {table}: {n:,} rows")


@main.command("schema")
@click.option(
    "--type",
    "stmt_type",
    type=click.Choice(
        ["entity", "person", "relationship", "all"], case_sensitive=False
    ),
    default="all",
    show_default=True,
    help="Which schema to print.",
)
def print_schema(stmt_type: str) -> None:
    """Print the PyArrow schema(s) used for Lance output."""
    from bods_lance.schema import ENTITY_SCHEMA, OOC_SCHEMA, PERSON_SCHEMA

    schemas = {
        "entity": ("entityStatement → entity_statements", ENTITY_SCHEMA),
        "person": ("personStatement → person_statements", PERSON_SCHEMA),
        "relationship": (
            "ownershipOrControlStatement → ownership_or_control_statements",
            OOC_SCHEMA,
        ),
    }

    to_print = (
        list(schemas.items())
        if stmt_type == "all"
        else [(stmt_type, schemas[stmt_type])]
    )

    for key, (label, schema) in to_print:
        click.echo(f"\n── {label} ──")
        for field in schema:
            nullable = "" if field.nullable else " [required]"
            click.echo(f"  {field.name}: {field.type}{nullable}")
